# 🛍️ RFM Customer Segmentation & Retail Analytics

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Plotly](https://img.shields.io/badge/Plotly-7.0+-3F4F75?logo=plotly&logoColor=white)](https://plotly.com/python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An end-to-end Data Analytics and Customer Intelligence project performing **Recency, Frequency, and Monetary (RFM) Segmentation** on multinational e-commerce transactional data. The project features exploratory business analytics in Jupyter Notebooks and an interactive, production-ready **Streamlit** executive dashboard with 3D customer clustering and tailored retention playbooks.

---

## 📌 Executive Summary & Business Problem

In retail and e-commerce, treating every customer with generic, one-size-fits-all marketing leads to inefficient ad spend, high customer acquisition costs, and preventable churn. 

### Core Challenges:
- **Identifying High-Value Customers**: Who are our highest-spending and most reliable patrons, and how do we protect them?
- **Proactive Churn Prevention**: Which previously active buyers have stopped purchasing, and what is our revenue exposure?
- **Targeted Nurturing**: Which recent single-order buyers possess the characteristics to become lifetime brand advocates?
- **Commercial Performance Transparency**: How are revenue, cancellation rates, average order values (AOV), and international sales distributed?

### Proposed Solution:
Using statistical quintile scoring across **Recency (R)**, **Frequency (F)**, and **Monetary Value (M)**, we segment **4,338 unique customers** into 8 strategic behavioral groups. Each segment is paired with actionable commercial recommendations, conversion triggers, and marketing interventions presented through an interactive web dashboard.

---

## 📊 Dataset Overview

The dataset used is the well-known **Online Retail II / Online Retail** transactional dataset from the [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/352/online+retail). It contains all transactions occurring between **01/12/2010 and 09/12/2011** for a UK-based, registered non-store online retail company specializing in unique all-occasion giftware.

| Dimension | Raw Dataset | Cleaned Analytical Base |
| :--- | :--- | :--- |
| **Total Rows** | 541,909 transactions | **392,692** valid sales lines |
| **Unique Invoices** | 25,900 orders | **18,532** completed orders |
| **Cancellation Invoices** | 3,836 cancelled orders | Excluded (Return rate: ~14.8%) |
| **Unique Customers** | 4,372 Customer IDs | **4,338** active customers |
| **Product SKUs** | ~4,070 Stock Codes | **3,665** unique giftware items |
| **Geographic Markets** | 38 Countries | 37 Countries (led by UK, Germany, France) |
| **Analysis Period** | Dec 1, 2010 – Dec 9, 2011 | Reference Snapshot: **Dec 10, 2011** |

### Data Cleaning Rules:
1. **Deduplication**: Removed exact duplicate transaction rows.
2. **Missing Value Treatment**: Filtered out transactions without a recorded `CustomerID` or `Description`.
3. **Cancellations & Outliers**: Excluded return/cancellation invoices (starting with `'C'`) and non-positive `Quantity` or `UnitPrice` records.
4. **Feature Engineering**: Derived `Revenue = Quantity * UnitPrice`, monthly period stamps (`YearMonth`), high-level product taxonomy categories, and calculated days since latest purchase relative to snapshot date.

---

## 🧠 RFM Segmentation Methodology

Each customer is scored across three dimensions using **quintile binning (1 to 5)**:
- **Recency (R)**: Days elapsed between the customer's last transaction and the snapshot date (`2011-12-10`). Score **5** represents the most recent buyers (top 20%), while **1** represents the longest dormancy.
- **Frequency (F)**: Total number of distinct completed orders (`InvoiceNo`). Score **5** represents top repeat purchasers, while **1** represents single-order buyers.
- **Monetary (M)**: Total cumulative revenue contribution (£). Score **5** represents top spenders, while **1** represents lowest spenders.

### Customer Segments & Behavioral Mapping

| Segment | R Score | F Score | Customer Count | Share (%) | Total Revenue (£) | Revenue Share (%) | Strategic Objective |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Loyal Customers** | 2–5 | 3–5 | **1,263** | 29.1% | £3,138,409.11 | 35.2% | Upsell premium tiers, loyalty milestones, automated reordering |
| **Champions** | 4–5 | 4–5 | **1,139** | 26.3% | £4,682,757.25 | 52.5% | VIP concierge, early access, brand advocacy (No heavy discounts) |
| **Potential Loyalists** | 3–5 | 1–2 | **670** | 15.4% | £344,228.02 | 3.9% | Onboarding welcome series, next-order 30-day coupon |
| **Hibernating** | 1 | 2–3 | **442** | 10.2% | £148,881.04 | 1.7% | Clearance blowouts, low-cost email reactivation |
| **Lost / Churned** | 1 | 1 | **364** | 8.4% | £64,369.30 | 0.7% | Suppress from paid ads; study root causes of drop-off |
| **Customers Needing Attention** | 2–3 | 2 | **202** | 4.7% | £124,008.20 | 1.4% | "We Miss You" personalized emails, limited-time flash perks |
| **About to Sleep** | 2–3 | 1 | **199** | 4.6% | £56,063.29 | 0.6% | Win-back discounts, feedback pulse survey |
| **At Risk / Can't Lose Them** | 1 | 4–5 | **59** | 1.4% | £352,654.49 | 4.0% | **Critical Alert**: Personal outreach, £50 VIP credit, executive review |
| **Total / Overall** | — | — | **4,338** | **100%** | **£8,911,370.70** | **100%** | **8 Distinct Actionable Cohorts** |

> **Key Discovery**: **Champions** and **Loyal Customers** combined represent **55.4% of all customers** but drive **87.7% of total company revenue** (£7.82M+). Conversely, 59 **At Risk** customers alone hold over £352K in historical value, representing immediate high-ROI retention targets.

---

## 🖥️ Streamlit Interactive Dashboard Architecture

The dashboard (`app.py`) provides a dual-page executive interface designed for commercial leaders, CRM specialists, and inventory planners:

```
📁 Retail Analytics & RFM Dashboard
│
├── 📊 Page 1: Executive Business Overview
│   ├── KPI Metric Banner (Revenue, Orders, Customers, AOV, Cancellation Rate)
│   ├── Monthly Revenue, Order Volume & Active Buyers Trendlines
│   ├── Geographic Performance (Interactive World Choropleth & Top Countries Bar)
│   ├── Product Assortment Matrix (Top 10 SKUs by Revenue, Unit Sales, Pareto Share)
│   └── Category Revenue Breakdown & Order Value Distribution
│
└── 🎯 Page 2: Customer RFM Intelligence
    ├── Segment Performance Comparison (Customer Distribution vs Revenue Share)
    ├── Interactive 3D RFM Cluster Visualizer (Recency vs Frequency vs Monetary)
    ├── Segment Action Playbook & Playbook Cards (Targeting tactics, dos & don'ts)
    ├── Segment Customer Directory (Searchable, sortable, and downloadable CSV)
    └── 360° Individual Customer Profile Inspector:
        ├── Customer RFM Scorecards & Lifecycle Tenure
        ├── Historical Order Log & Purchase Frequency
        ├── Category Affinity Pie Chart & Monthly Spend Timeline
        └── Customer Top SKUs Purchased
```

---

## 📁 Repository Structure

```plaintext
rfm-customer-segmentation-analysis/
│
├── .gitignore                      # Git ignore file for Python, Jupyter & environment caches
├── README.md                       # Comprehensive project documentation & findings
├── requirements.txt                # Production Python dependencies
├── run_dashboard.bat               # One-click Windows runner for local Streamlit app
│
├── app.py                          # Streamlit multi-page web application entry point
├── data_loader.py                  # Optimized data pipeline, caching, and segment logic
├── analysis.py                     # Standalone CLI analysis script
│
├── RFM_Analysis.ipynb              # Jupyter Notebook: Complete RFM pipeline & visualizations
├── Retail_Analysis.ipynb           # Jupyter Notebook: Exploratory data analysis & business trends
│
├── Online Retail.xlsx              # Raw UCI e-commerce dataset (23.7 MB)
├── online_retail_cleaned.parquet   # High-speed cleaned transaction base (3.26 MB)
├── rfm_segmented.parquet           # Precomputed customer RFM scores & segments (82.8 KB)
└── raw_stats.json                  # Baseline metrics cache (cancellations & snapshot date)
```

---

## 🚀 Getting Started (Local Setup)

### 1. Prerequisites
Ensure you have **Python 3.10+** installed on your system.

### 2. Clone the Repository
```bash
git clone https://github.com/<your-username>/rfm-customer-segmentation-analysis.git
cd rfm-customer-segmentation-analysis
```

### 3. Create & Activate a Virtual Environment
- **Windows (PowerShell)**:
  ```powershell
  python -m venv .venv
  .venv\Scripts\Activate.ps1
  ```
- **macOS / Linux**:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Launch the Interactive Dashboard
Run the following command:
```bash
streamlit run app.py
```
*(On Windows, you can also simply double-click `run_dashboard.bat`)*

Your default web browser will automatically open:
```
Local URL: http://localhost:8501
```

### 6. Explore the Jupyter Notebooks
To inspect or re-execute the step-by-step analysis:
```bash
jupyter notebook RFM_Analysis.ipynb
# or
jupyter notebook Retail_Analysis.ipynb
```

---

## 🌐 Deploying to Streamlit Community Cloud

This project is fully optimized for one-click deployment on [Streamlit Community Cloud](https://streamlit.io/cloud):

1. **Push your repository** to your GitHub account (named `rfm-customer-segmentation-analysis`).
2. Navigate to [share.streamlit.io](https://share.streamlit.io/) and log in with GitHub.
3. Click **"New app"** and select:
   - **Repository**: `<your-username>/rfm-customer-segmentation-analysis`
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. Click **"Deploy!"**
5. Streamlit will install `requirements.txt`, load the pre-cached `.parquet` files instantly, and provide a public HTTPS URL.

---

## 🛠️ Tools & Technologies

- **Language**: Python 3.12
- **Data Manipulation**: Pandas, NumPy
- **High-Performance Storage**: Apache Parquet (`pyarrow`)
- **Interactive Web App**: Streamlit
- **Visualizations**: Plotly Express, Plotly Graph Objects, Seaborn, Matplotlib
- **Spreadsheet Parsing**: OpenPyXL
- **Development Environment**: Jupyter Notebook, VS Code, Google Antigravity

---

## 📜 Dataset Citation & License

- **Dataset Source**: Daqing Chen, Sai Liang Sain, and Kun Guo. *Online Retail*. UCI Machine Learning Repository, 2012. [DOI: 10.24432/C5BW33](https://doi.org/10.24432/C5BW33).
- **Dataset License**: Creative Commons Attribution 4.0 International (CC BY 4.0).
- **Code License**: This project is licensed under the [MIT License](LICENSE).

#   D A T A _ A N A L Y T I C S _ P O R T F O L I O  
 #   D A T A _ A N A L Y T I C S _ P O R T F O L I O  
 #   D A T A _ A N A L Y T I C S _ P O R T F O L I O  
 