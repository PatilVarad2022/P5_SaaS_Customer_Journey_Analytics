# 📊 P5 — SaaS Customer Journey Analytics

An enterprise-grade analytics engine for SaaS customer journey analysis, delivering end-to-end metrics from activation through retention, churn, and revenue optimization.  
Built for **Product/Business/BI Analyst** portfolio demonstration with modular architecture and Tableau-ready exports.

Pipeline generates comprehensive SaaS KPIs with full data lineage and explainability.

---

## ✅ 1. Project Scope

This analytics engine delivers:

### **Customer Journey Analytics**
- Freemium → Paid conversion funnel  
- Activation rate (14-day window)
- Monthly retention cohorts  
- MRR-based churn analytics  
- Revenue metrics (MRR, ARR, NRR, GRR, expansion MRR, ARPU)  
- Customer Lifetime Value (LTV)

### **Segmentation**
- By country  
- By pricing plan  
- By acquisition channel  

### **Scenario Simulation**
Excel-based business layer:
- Pricing sensitivity analysis
- Activation uplift modeling
- Churn rate scenarios
- LTV and ARPU impact calculations

### **Design Philosophy**
All KPIs computed using industry-standard, rule-based logic aligned with SaaS best practices. Fully explainable and auditable.

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

Datasets are programmatically generated to demonstrate realistic SaaS customer behavior patterns and industry-standard data structures.

---

## ⚙️ 3. Running the Analytics Pipeline

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

## ⚡ 4. Quick Start

Pre-computed sample outputs are available in `demo_sample/` for immediate evaluation:
- `demo_sample/kpi_summary.csv` — Example KPI metrics
- `demo_sample/cohort_retention_matrix.csv` — Sample cohort analysis
- `demo_sample/kpi_summary.png` — Visual output example

Run the pipeline commands above to generate fresh outputs from the full dataset.

## ✅ 5. Verifiable Claims & Integrity

This pipeline validates:
- **Schema & Types**: Verified by `run_inspect.py`
- **Data Consistency**: Cross-referenced `customer_id` across all tables.
- **Metric Definitions**: All formulas documented in `docs/metrics_definitions.md` matches `compute_metrics.py` logic.

---

## 📊 6. Generated Outputs

The analytics pipeline generates comprehensive, analysis-ready metrics:

**`kpi_summary.csv`** — Single-row executive summary
- Total signups and activation rate
- Freemium → paid conversion
- MRR and ARR (Monthly/Annual Recurring Revenue)
- ARPU (Average Revenue Per User)
- LTV (Customer Lifetime Value)
- Monthly churn rate (MRR-based)
- Net Revenue Retention (NRR)
- Gross Revenue Retention (GRR)
- Quick Ratio (growth efficiency)
- CAC (Customer Acquisition Cost)*
- Payback Period*

*Extensible: Add `data/marketing_costs.csv` to enable CAC and payback period calculations. Schema documented in `docs/data_dictionary.md`.

**`cohort_retention_matrix.csv`** — Cohort analysis
- Monthly cohort survival rates
- Retention % pivot table (cohort × months since signup)

**`mrr_breakdown.csv`** — Revenue movement analysis
- New MRR
- Expansion MRR
- Churned MRR
- Net MRR change

**`tableau_ready/`** — Optimized for seamless BI integration
- Flat, denormalized extracts with standardized date formats
- Pre-joined customer master table
- Revenue transaction history
- Daily event stream
- Ready for direct import into Tableau, Power BI, or Looker

---

## 📈 7. Business Scenario Simulator

`P5_LTV_Simulator.xlsx` provides interactive what-if analysis:
- Pricing sensitivity modeling
- Activation rate impact scenarios
- Churn rate adjustments
- LTV, ARPU, and MRR projections

Excel-based interface designed for business stakeholders and executive presentations.

---

## 📑 8. Documentation & Transparency

**Complete technical documentation:**
- `docs/data_dictionary.md` — Schema definitions for all datasets
- `docs/metrics_definitions.md` — Exact formulas and calculation logic for every KPI

All metrics are fully documented with:
- Mathematical formulas
- Business logic explanations
- Division-by-zero guards
- Edge case handling

Ensures complete auditability and stakeholder confidence.

