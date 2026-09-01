# Accenture EMEA Partner Strategy & Pipeline Dashboard (FY26)

Interactive analytics dashboard and data pipeline for Google Cloud's EMEA Accenture Partner Strategy, Top Key Accounts, Sales Play Alignment, and GSI Pipeline Benchmarks.

---

## 🚀 Quick Start

### 1. View Dashboard Locally
To view the generated dashboard directly in your browser:
```bash
# Direct browser opening (macOS)
open index.html
```

Or serve via local HTTP server:
```bash
python3 -m http.server 8080
```
Then visit: [http://localhost:8080](http://localhost:8080)

---

## 🛠️ Data Pipeline & Build Scripts

The dashboard HTML is pre-generated and self-contained, but can be rebuilt at any time from the structured datasets:

- **`generate_html_file.py`**: Compiles the data payload into `FY26_Accenture_EMEA_Partner_Strategy_Report.html` and `index.html`.
  ```bash
  python3 generate_html_file.py
  cp FY26_Accenture_EMEA_Partner_Strategy_Report.html index.html
  ```
- **`prepare_data_payload.py`**: Extracts sheet data, accounts, sales plays, and opportunity mappings into `full_data_payload.json`.
- **`compute_metrics.py`**: Computes ACV, stage velocity, regional distribution, and partner rankings.
- **`full_data_payload.json`**: Processed JSON dataset powering the dashboard charts and tables.

---

## 📊 Features & Views

- **Executive Summary**: KPI metrics covering Total Pipeline ACV, Active Pipeline, Lost Pipeline, P1/Focus Accounts, and GSI Market Share.
- **GSI Partner Comparison**: Comparative benchmark charts across EMEA GSIs.
- **Regional Breakdown**: Detailed analytics across UKI, Central Europe, South Europe, North Europe, and MEA.
- **Sales Play Alignment**: Pipeline distribution across GenAI, Data & Analytics, VMware Engine, SAP on GCP, Security, and Cloud Infrastructure.
- **Key Accounts Matrix**: Filterable and searchable account directory with priority badges, sales play mapping, and opportunity drilldowns.
- **Top Marquee Bets**: Highlight of high-impact deal pursuits.
- **Export & Search**: Live multi-field filtering and CSV export capabilities.

---

## 📋 Requirements
- Python 3.9+ (for running build scripts)
- Modern web browser (Chrome, Safari, Edge, Firefox)
