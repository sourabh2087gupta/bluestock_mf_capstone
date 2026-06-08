import os
import sqlite3
import pandas as pd

# Path configurations
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'bluestock_mf.db')
SCHEMA_PATH = os.path.join(BASE_DIR, 'sql', 'schema.sql')
RAW_DIR = os.path.join(BASE_DIR, 'data', 'raw')
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')

def execute_ddl_schema():
    print("[DB SETUP] Initialising database tables from schema...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    with open(SCHEMA_PATH, 'r') as f:
        cursor.executescript(f.read())
    conn.commit()
    conn.close()
    print("[DB SETUP] SQLite core schema built successfully.")

def run_cleaning_and_loading():
    conn = sqlite3.connect(DB_PATH)
    
    # 1. Populating Core Fund Master Data Layouts
    try:
        scorecard_f = os.path.join(PROCESSED_DIR, 'fund_scorecard.csv')
        if os.path.exists(scorecard_f):
            df_scorecard = pd.read_csv(scorecard_f)
            
            # dim_fund data mapping
            dim_fund_cols = ['amfi_code', 'fund_house', 'scheme_name', 'category', 'sub_category', 'plan', 'launch_date', 'benchmark', 'expense_ratio_pct', 'risk_category']
            df_fund = df_scorecard[[c for c in dim_fund_cols if c in df_scorecard.columns]].drop_duplicates()
            df_fund.to_sql('dim_fund', conn, if_exists='append', index=False)
            
            # fact_performance data mapping
            perf_cols = ['amfi_code', 'return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct', 'alpha', 'beta', 'sharpe_ratio', 'sortino_ratio', 'var_95_pct']
            df_perf = df_scorecard[[c for c in perf_cols if c in df_scorecard.columns]]
            df_perf.to_sql('fact_performance', conn, if_exists='append', index=False)
            print("[SUCCESS] Loaded dim_fund and fact_performance database segments.")
    except Exception as e:
        print(f"[WARNING] Master loading bypassed: {e}")

    # 2. Ingesting Cleaned Investor Transactions (08_investor_transactions.csv)
    tx_file = os.path.join(RAW_DIR, '08_investor_transactions.csv')
    if not os.path.exists(tx_file):
        tx_file = os.path.join(BASE_DIR, 'data', '08_investor_transactions.csv')
        
    if os.path.exists(tx_file):
        df_tx = pd.read_csv(tx_file)
        df_tx['transaction_type'] = df_tx['transaction_type'].str.strip()
        df_tx = df_tx.drop_duplicates()
        if 'tx_id' not in df_tx.columns:
            df_tx.insert(0, 'tx_id', [f"TX_{i:06d}" for i in range(1, len(df_tx) + 1)])
            
        df_tx.to_sql('fact_transactions', conn, if_exists='append', index=False)
        print(f"[SUCCESS] Migrated {len(df_tx)} transaction tracking points to database.")
    
    conn.close()
    print("\nDay 2 ETL Engine and SQL loader completely synchronized.")

if __name__ == "__main__":
    execute_ddl_schema()
    run_cleaning_and_loading()