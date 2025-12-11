# SaaS Customer Journey Analytics (P5)

## Purpose
An end-to-end analytics pipeline for a B2B SaaS product. This project generates synthetic user journey data, computes core business KPIs (MRR, Churn, LTV, Activation), and produces Tableau-ready extracts. It is designed to demonstrate full-stack data engineering and analytics capabilities, ensuring data consistency from raw logs to executive dashboards.

**Tech Stack**: Python (Pandas, Numpy), Tableau (prepared extracts), Excel (LTV Simulator).

## Quick Start
1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the pipeline**:
   ```bash
   python scripts/run_inspect.py       # Validate data schema and quality
   python scripts/compute_metrics.py   # Generate KPI tables (MRR, Churn, Retention)
   python scripts/export_tableau_extracts.py # Create BI-ready data sources
   ```
3. **Explore Outputs**: 
   - Check `/outputs/` for KPI summaries and cohort matrices.
   - Check `/outputs/tableau_ready/` for flat tables used in dashboards.

## Folder Structure
- **/data/**: Raw CSV inputs (Users, Events, Subscriptions, Revenue, Support Tickets).
- **/scripts/**: Python processing scripts.
  - `run_inspect.py`: specific data validation checks (nulls, keys, types).
  - `compute_metrics.py`: Calculation of Activation Rate, Funnel, MRR, ARPU, LTV.
  - `export_tableau_extracts.py`: Flattens data for easy import into Tableau/PowerBI.
- **/outputs/**: Computed metrics.
  - `kpi_summary.csv`: High-level monthly metrics.
  - `cohort_retention_matrix.csv`: User retention by cohort month.
  - `mrre_breakdown.csv`: Detailed MRR movement (New, Expansion, Churn).
- **/docs/**: Documentation.
  - `data_dictionary.md`: Column definitions.
  - `metrics_definitions.md`: Formulas for all calculated KPIs.
- **/tests/**: Unit tests for code integrity.
- **/examples/**: Sample notebooks.
- **P5_LTV_Simulator.xlsx**: Interactive Excel model for LTV and scenario planning.

## Key Datasets
All dates are ISO 8601 (YYYY-MM-DD). 
**Canonical Key**: `customer_id` is used across all files to link users, subscriptions, and events.

- **users.csv**: Customer metadata (Pricing Plan, Country, Acquisition Channel).
- **events.csv**: Product usage log (Note: `campaign_create` is used as the 'Activation' event).
- **subscriptions.csv**: Billing history and status.
- **revenue.csv**: Transactional revenue log (Invoice level).

## Excel Simulator
The **Excel Simulator** (`P5_LTV_Simulator.xlsx`) is located in the root directory. Open it to explore scenario modeling:
- **Inputs**: Change Pricing, Monthly Churn %, and Activation Lift.
- **Outputs**: See immediate impact on LTV, ARPU, and projected MRR.
