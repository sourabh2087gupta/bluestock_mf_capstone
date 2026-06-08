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