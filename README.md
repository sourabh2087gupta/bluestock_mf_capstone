# 📈 Mutual Fund Analytics Platform - Capstone Project
An end-to-end Data Engineering and Analytics platform built to ingest, clean, evaluate, and visualize mutual fund data using Python, SQL, and Power BI.

---

## 📅 Project Timeline & Deliverables

### 🔹 Phase 1: Data Engineering & Pipeline Setup (Days 1-3)
* **Day 1:** Environment setup, `requirements.txt` configuration, and absolute folder design.
* **Day 2:** SQLite database construction, schema normalization, and dynamic SQL data dictionary tracking.
* **Day 3:** Automated ETL pipeline (`run_pipeline.py`) deployment, data type casting, and Exploratory Data Analysis (EDA) rendering 15+ financial charts.

### 🔹 Phase 2: Quantitative Financial Analytics (Day 4)
* Created `04_performance_analytics.ipynb` engine.
* Automated extraction and calculation of active mutual fund metrics saved directly to:
  * `returns_computed.csv` (Daily percentage change rolling logs)
  * `cagr_report.csv` (3-Year Compound Annual Growth Rates)
  * `sharpe_values.csv` & `sortino_values.csv` (Risk-adjusted performance indicators)
  * `alpha_beta.csv` (Market volatility benchmarking metrics)

### 🔹 Phase 3: Interactive Dashboard Development (Days 5-7)
Developed a full-scale interactive **Power BI Dashboard** (`bluestock_mf_dashboard.pbix`) across 4 analytics standpoints:
1. **Industry Overview:** Dynamic metrics tracking Volio sizing, Top 10 Asset Management Companies, and total industry schemes.
2. **Fund Performance Analysis:** High-fidelity Risk vs. Return scatter plotting using Sharpe and CAGR dimensions.
3. **Investor Analytics:** State-wise demographic market penetration charts mapped with transaction behaviors and age brackets.
4. **SIP & Market Trends:** Capital flow streams comparing Equity vs. Debt schemes alongside comprehensive Risk Category distributions.

---

## 🛠️ Tech Stack Used
* **Backend:** Python 3.x, SQLite3
* **Libraries:** Pandas, NumPy, Matplotlib, Seaborn
* **Visualization:** Power BI Desktop
* **Version Control:** Git & GitHub Workflow
