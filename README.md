# SaaS Customer Journey Analytics (P5)

## Purpose
An end-to-end analytics pipeline for a B2B SaaS product. This project generates synthetic user journey data, computes core business KPIs (MRR, Churn, LTV, Activation), and produces Tableau-ready extracts. It is designed to demonstrate full-stack data engineering and analytics capabilities, ensuring data consistency from raw logs to executive dashboards.

**Tech Stack**: Python (Pandas, Numpy), Tableau (prepared extracts), Excel (LTV Simulator).

### Project Structure
![Project Structure](docs/screenshots/project_structure.png)

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

## Key Outputs
### KPI Summary (Automated Output)
![KPI Summary](docs/screenshots/kpi_summary.png)

### LTV Scenario Simulator (Excel Model)
The **Excel Simulator** (`P5_LTV_Simulator.xlsx`) allows dynamic modeling of churn reduction and price changes.
![LTV Simulator](docs/screenshots/ltv_simulator_output.png)

## Folder Structure
- **/data/**: Raw CSV inputs (Users, Events, Subscriptions, Revenue, Support Tickets).
- **/scripts/**: Python processing scripts.
  - `run_inspect.py`: specific data validation checks (nulls, keys, types).
  - `compute_metrics.py`: Calculation of Activation Rate, Funnel, MRR, ARPU, LTV.
  - `export_tableau_extracts.py`: Flattens data for easy import into Tableau/PowerBI.
- **/outputs/**: Computed metrics.
  - `kpi_summary.csv`: High-level monthly metrics.
  - `cohort_retention_matrix.csv`: User retention by cohort month.
  - `mrre_breakdown.csv`: Detailed MRR movement.
- **/docs/**: Documentation.
- **/tests/**: Unit tests for code integrity.

## Key Datasets
**Canonical Key**: `customer_id` is used across all files.

- **users.csv**: Customer metadata.
- **events.csv**: Product usage log (`campaign_create` = Activation).
- **subscriptions.csv**: Billing history.
- **revenue.csv**: Transactional revenue log.

