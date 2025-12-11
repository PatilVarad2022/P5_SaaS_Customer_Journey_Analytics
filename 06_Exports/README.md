# SaaS Exports & Canonical Data

This directory contains the final, canonical CSV datasets for Dashboarding (Tableau) and Modeling (Excel/Python).

## 1. Primary Files
| File | Description | Destination |
|------|-------------|-------------|
| **mrr_metrics.csv** | Dedicated MRR Bridge (New, Exp, Cont, Churn, Net). Strict formula reconciliation. | Excel / Tableau |
| **arpu_ltv.csv** | Monthly Unit Economics (Active Users, ARPU, Churn Rate, LTV). | Excel Simulator / Tableau |
| **segmentation_plan.csv** | Segmented metrics by Country & Plan (Activation, Conv, Churn Rates). | Tableau |
| **segmentation_acquisition.csv** | Segmented metrics by Channel. | Tableau |
| **scenario_inputs.csv** | Parameter configuration loaded by the Forecast Engine. | Simulator Inputs |

## 2. Formulas & Definitions
- **Activation**: User has >0 events (`events_cleaned.parquet`).
- **Paid Conversion**: User has at least one subscription with `amount > 0`.
- **Churn Rate**: `Churned Paid Users / Total Paid Users` (Segment) or `Churned Users_t / Active Users_{t-1}` (Monthly).
- **MRR Bridge**: `End = Start + New + Expansion - Contraction - Churn`.
- **LTV**: `ARPU / Churn Rate`. (If Churn=0, LTV cap applied).

## 3. Usage
- **Tableau**: Connects to `mrr_metrics.csv`, `segmentation_*.csv`.
- **Excel Simulator**: Imports `scenario_inputs.csv` and `arpu_ltv.csv`.

*Generated from `04_Derived_Tables` (Source of Truth).*
