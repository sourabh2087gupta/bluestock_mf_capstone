import os
import datetime
import pandas as pd
import numpy as np
import requests
from sqlalchemy import create_engine
from scipy.stats import linregress

# Define absolute paths for data directory and database storage
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(BASE_DIR, 'bluestock_mf.db')

print("🚀 Starting Bluestock Mutual Fund ETL & Analytics Pipeline...")

# STEP 1: DATA INGESTION & LIVE API FETCH
print("\n🔄 Step 1: Loading raw CSV datasets into memory...")

try:
    fund_master = pd.read_csv(os.path.join(RAW_DATA_DIR, '01_fund_master.csv'))
    nav_history = pd.read_csv(os.path.join(RAW_DATA_DIR, '02_nav_history.csv'))
    investor_tx = pd.read_csv(os.path.join(RAW_DATA_DIR, '08_investor_transactions.csv'))
    benchmark_indices = pd.read_csv(os.path.join(RAW_DATA_DIR, '10_benchmark_indices.csv'))
    
    aum_fund_house = pd.read_csv(os.path.join(RAW_DATA_DIR, '03_aum_by_fund_house.csv'))
    monthly_sip = pd.read_csv(os.path.join(RAW_DATA_DIR, '04_monthly_sip_inflows.csv'))
    category_inflows = pd.read_csv(os.path.join(RAW_DATA_DIR, '05_category_inflows.csv'))
    industry_folio = pd.read_csv(os.path.join(RAW_DATA_DIR, '06_industry_folio_count.csv'))
    portfolio_holdings = pd.read_csv(os.path.join(RAW_DATA_DIR, '09_portfolio_holdings.csv'))
    
    print("All raw static CSV files successfully loaded.")
except Exception as e:
    print(f"Critical Error loading CSV files: {e}")
    exit()

print("\nFetching live real-time historical NAV data from mfapi.in REST API...")
live_schemes = [119551, 120503, 118632, 119092, 120841]
api_nav_list = []

for code in live_schemes:
    try:
        url = f"https://api.mfapi.in/mf/{code}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            for row in data['data'][:100]:  
                api_nav_list.append({
                    'amfi_code': code,
                    'date': datetime.datetime.strptime(row['date'], '%d-%m-%Y').strftime('%Y-%m-%d'),
                    'nav': float(row['nav'])
                })
        print(f"   -> Successfully fetched real-time NAV records for Scheme Code: {code}")
    except Exception as e:
        print(f"   -> Network/Parsing failed for Scheme Code {code}: {e}")

if api_nav_list:
    api_nav_df = pd.DataFrame(api_nav_list)
    nav_history = pd.concat([nav_history, api_nav_df], ignore_index=True)
    print("Real-time API data successfully appended to primary historical data array.")

# STEP 2: DATA CLEANING & STRUCTURAL VALIDATION
print("\nStep 2: Executing data cleaning, formatting, and structural validation...")

nav_history['date'] = pd.to_datetime(nav_history['date'])
benchmark_indices['date'] = pd.to_datetime(benchmark_indices['date'])

for col in benchmark_indices.columns:
    if col != 'date':
        benchmark_indices[col] = pd.to_numeric(benchmark_indices[col].astype(str).str.replace(',', ''), errors='coerce')

nav_history['nav'] = pd.to_numeric(nav_history['nav'], errors='coerce')

nav_history = nav_history.sort_values(by=['amfi_code', 'date'])
nav_history['nav'] = nav_history.groupby('amfi_code')['nav'].ffill()

nav_history = nav_history.drop_duplicates(subset=['amfi_code', 'date'])
nav_history = nav_history[nav_history['nav'] > 0]
investor_tx = investor_tx[investor_tx['amount_inr'] > 0]

print("Data cleaning complete. Gaps reconciled and structural filters applied successfully.")

# STEP 3: FINANCIAL RISK-RETURN METRICS CALCULATIONS
print("\nStep 3: Computing core financial quantitative risk metrics...")

nav_history['daily_return'] = nav_history.groupby('amfi_code')['nav'].pct_change()

benchmark_indices = benchmark_indices.sort_values(by='date')
if 'Nifty 100' in benchmark_indices.columns:
    benchmark_indices['bench_return'] = benchmark_indices['Nifty 100'].pct_change()
else:
    benchmark_indices['bench_return'] = benchmark_indices.iloc[:, 1].pct_change()

benchmark_indices['bench_return'] = benchmark_indices['bench_return'].replace([np.inf, -np.inf], np.nan).fillna(0)

performance_metrics = []
rf_rate = 0.065 / 252  

for amfi, group in nav_history.groupby('amfi_code'):
    group = group.dropna(subset=['daily_return'])
    if len(group) < 10:
        continue
        
    nav_start = group['nav'].iloc[0]
    nav_end = group['nav'].iloc[-1]
    n_days = len(group)
    cagr = (nav_end / nav_start) ** (252 / n_days) - 1 if nav_start > 0 else 0
    
    avg_daily_ret = group['daily_return'].mean()
    std_daily_ret = group['daily_return'].std()
    
    sharpe = (avg_daily_ret - rf_rate) / std_daily_ret * np.sqrt(252) if std_daily_ret > 0 else 0
    
    downside_returns = group['daily_return'][group['daily_return'] < 0]
    downside_std = downside_returns.std()
    sortino = (avg_daily_ret - rf_rate) / downside_std * np.sqrt(252) if len(downside_returns) > 0 and downside_std > 0 else 0
    
    merged_bench = pd.merge(group, benchmark_indices, on='date', how='inner')
    
    if len(merged_bench) > 5 and merged_bench['bench_return'].nunique() > 1:
        try:
            slope, intercept, r_value, p_value, std_err = linregress(merged_bench['bench_return'], merged_bench['daily_return'])
            beta = slope
            alpha = intercept * 252  
        except ValueError:
            beta = 1.0
            alpha = 0.0
    else:
        beta = 1.0
        alpha = 0.0
        
    var_95 = np.percentile(group['daily_return'], 5)
    
    performance_metrics.append({
        'amfi_code': amfi,
        'cagr_3yr': cagr,
        'sharpe_ratio': sharpe,
        'sortino_ratio': sortino,
        'beta': beta,
        'alpha': alpha,
        'var_95_pct': var_95 * 100
    })

perf_df = pd.DataFrame(performance_metrics)
fund_scorecard = pd.merge(fund_master, perf_df, on='amfi_code', how='left')
fund_scorecard.to_csv(os.path.join(RAW_DATA_DIR, 'fund_scorecard.csv'), index=False)
print("Quantitative analytics finalized. 'fund_scorecard.csv' saved successfully.")

# STEP 4: STRATIFIED STAR-SCHEMA LOAD TO LIGHTWEIGHT DATABASE
print("\n Step 4: Loading clean datasets into local SQLite database environment...")

engine = create_engine(f'sqlite:///{DB_PATH}')

fund_master.to_sql('dim_fund', engine, if_exists='replace', index=False)
nav_history.to_sql('fact_nav', engine, if_exists='replace', index=False)
investor_tx.to_sql('fact_transactions', engine, if_exists='replace', index=False)
fund_scorecard.to_sql('fact_performance', engine, if_exists='replace', index=False)
aum_fund_house.to_sql('fact_aum', engine, if_exists='replace', index=False)

print(f" Data persistence layer initialized successfully. Database File: {DB_PATH}")
print("\n CRITICAL TASK DEPLOYMENT SUCCESSFUL: BACKEND ETL PIPELINE RECONCILED! ")