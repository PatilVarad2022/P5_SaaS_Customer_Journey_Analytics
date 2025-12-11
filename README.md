# 📊 P5 — SaaS Customer Journey Analytics (Backend Only)

This project implements the complete backend analytics layer for a SaaS product, covering the full customer journey: activation, conversion, retention, churn, MRR, ARPU, LTV, and scenario simulation.  
It is designed as a portfolio project for **Product/Business/BI Analyst** roles.

The backend is fully operational and generates all SaaS KPIs.  
A Tableau dashboard will be added later — the dataset and extracts are already prepared.

---

## ✅ 1. Project Scope (Strict P5 Specification)

This project includes:

### **Customer Journey Analytics**
- Freemium → Paid conversion funnel  
- Activation rate  
- Retention cohorts  
- Churn analytics  
- Revenue metrics (MRR, churn MRR, expansion MRR, ARPU)  
- Customer Lifetime Value (rule-based, no ML)

### **Segmentation**
- By country  
- By pricing plan  
- By acquisition channel  

### **Scenario Simulation**
Implemented in Excel:
- Pricing changes  
- Activation uplift  
- Churn rate override  
- LTV and ARPU sensitivity

### **NO ML • NO Forecasting • NO Clustering**
All metrics are rule-based and fully explainable.

---

## 📁 2. Repository Structure

```text
/data
    users.csv
    events.csv
    subscriptions.csv
    revenue.csv

/scripts
    run_inspect.py
    compute_metrics.py
    export_tableau_extracts.py

/outputs
    kpi_summary.csv
    cohort_retention_matrix.csv
    mrr_breakdown.csv
    /tableau_ready/

/docs
    data_dictionary.md
    metrics_definitions.md

P5_LTV_Simulator.xlsx
README.md
requirements.txt
```

All datasets are synthetic and follow SaaS industry conventions.

---

## ⚙️ 3. How to Run the Backend Pipeline

Install requirements:

```bash
pip install -r requirements.txt
```

Run validation:

```bash
python scripts/run_inspect.py
```

Compute all SaaS KPIs:

```bash
python scripts/compute_metrics.py
```

Generate Tableau-ready extracts:

```bash
python scripts/export_tableau_extracts.py
```

Outputs will appear in `/outputs/` and `/outputs/tableau_ready/`.

---

## 📊 4. Key Outputs

The backend generates the following metrics:

**`kpi_summary.csv`**
- Total signups
- Activation rate
- Freemium → paid conversion
- ARPU
- LTV
- Monthly churn

**`cohort_retention_matrix.csv`**
- Monthly cohort survival
- Retention % grid

**`mrr_breakdown.csv`**
- New MRR
- Expansion MRR
- Churned MRR
- Net MRR

**`tableau_ready/`**
- Flat, clean extracts prepared for dashboarding (dates standardized, keys aligned).

---

## 📈 5. Scenario Simulator (Excel)

`P5_LTV_Simulator.xlsx` includes:
- Pricing assumptions
- Activation uplift
- Churn override
- LTV, ARPU, and MRR impact calculations

This file is the business-facing layer of the project.

---

## 📑 6. Documentation

- `docs/data_dictionary.md` → column definitions for every dataset
- `docs/metrics_definitions.md` → exact formulas for all KPIs (activation, funnel, churn, MRR, ARPU, LTV, cohorts)

These ensure full transparency and explainability.
