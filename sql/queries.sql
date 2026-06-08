-- Query 1: Top 5 Mutual Fund Schemes by highest 3-Year CAGR
SELECT scheme_name, fund_house, cagr_3yr 
FROM fact_performance 
ORDER BY cagr_3yr DESC 
LIMIT 5;

-- Query 2: Total Transaction Volume and Capital Invested broken down by State
SELECT state, COUNT(*) as total_transactions, SUM(amount_inr) as total_capital_invested
FROM fact_transactions 
GROUP BY state 
ORDER BY total_capital_invested DESC;

-- Query 3: Identify institutional funds with a low Expense Ratio (Less than 1.0%)
SELECT scheme_name, fund_house, expense_ratio_pct 
FROM dim_fund 
WHERE expense_ratio_pct < 1.0 
ORDER BY expense_ratio_pct ASC;

-- Query 4: Calculate Average Net Asset Value (NAV) per month for tracking trends
SELECT amfi_code, strftime('%Y-%m', date) as transaction_month, AVG(nav) as average_nav
FROM fact_nav
GROUP BY amfi_code, transaction_month
LIMIT 10;

-- Query 5: Segment transactions based on City Tier classification (T30 vs B30)
SELECT city_tier, COUNT(*) as total_orders, SUM(amount_inr) as absolute_investment
FROM fact_transactions
GROUP BY city_tier;

-- Query 6: Identify Top 3 Asset Categories with Highest Transaction Frequency
SELECT category, COUNT(tx_id) as total_transactions 
FROM fact_transactions t 
JOIN dim_fund f ON t.amfi_code = f.amfi_code 
GROUP BY category 
ORDER BY total_transactions DESC LIMIT 3;

-- Query 7: Month-on-Month Growth Trend of Total Investment Value
SELECT strftime('%Y-%m', transaction_date) as monthly_period, SUM(amount_inr) as total_invested 
FROM fact_transactions 
GROUP BY monthly_period 
ORDER BY monthly_period ASC;

-- Query 8: Active Investors Distribution by Gender Framework
SELECT gender, COUNT(DISTINCT investor_id) as total_unique_investors Framework, SUM(amount_inr) as absolute_volume
FROM fact_transactions 
GROUP BY gender;

-- Query 9: Filter High-Risk Growth Portfolio Schemes
SELECT scheme_name, fund_house, risk_category, beta 
FROM dim_fund f 
JOIN fact_performance p ON f.amfi_code = p.amfi_code 
WHERE risk_category LIKE '%High%' AND beta > 1.0;

-- Query 10: Calculate Average Expense Ratio Across Mutual Fund Houses
SELECT fund_house, ROUND(AVG(expense_ratio_pct), 2) as avg_expense_ratio_pct 
FROM dim_fund 
GROUP BY fund_house 
ORDER BY avg_expense_ratio_pct ASC;