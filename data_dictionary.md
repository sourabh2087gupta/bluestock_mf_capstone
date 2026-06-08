# 📘 Bluestock Mutual Fund Capstone - Data Dictionary

### 1. dim_fund (Dimension Table)
| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| amfi_code | TEXT (PK) | Unique identifier for the Mutual Fund Scheme |
| fund_house | TEXT | Asset Management Company (AMC) name |
| scheme_name | TEXT | Full nomenclature of the fund scheme |
| risk_category | TEXT | Risk grading assigned to the portfolio |

### 2. fact_transactions (Fact Table)
| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| tx_id | TEXT (PK) | System generated transaction track sequence |
| investor_id | TEXT | Unique verification identifier for the investor |
| amount_inr | INTEGER | Currency amount processed in Indian Rupees |
| state | TEXT | Demographical state source of investment |