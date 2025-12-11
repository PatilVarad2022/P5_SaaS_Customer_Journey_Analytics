# Excel Integration Instructions

## File: `clv_inputs_v1.1.xlsx`
This file connects the backend SaaS data to your financial models (CLV, LTV/CAC).

## 1. Internal Structure

### Sheet: `Inputs`
Contains global scalar variables. **Named Ranges** are strictly defined as follows:

| Named Range | Cell | Description |
| :--- | :--- | :--- |
| **gross_margin** | Inputs!$B$2 | Gross Margin % (e.g. 0.85) |
| **discount_rate** | Inputs!$B$3 | Annual WACC (e.g. 0.10) |
| **price_basic** | Inputs!$B$4 | Monthly Price - Basic |
| **price_pro** | Inputs!$B$5 | Monthly Price - Pro |
| **monthly_churn_basic** | Inputs!$B$6 | Est. Monthly Churn Rate (Basic) |
| **monthly_churn_pro** | Inputs!$B$7 | Est. Monthly Churn Rate (Pro) |
| **cac_target** | Inputs!$B$8 | Target CAC |

### Sheet: `Monthly_Data`
Rollup of MRR and Active Users from `monthly_revenue.csv`.
- **Columns**: `month`, `MRR_total`, `MRR_start`, `new_MRR`, `expansion_MRR`, `contraction_MRR`, `churned_MRR`, `active_paid_users`, `ARPU`.
- **Usage**: Reference this range for historical actuals in your model.

### Sheet: `User_Summary`
Average retention curve derived from cohort analysis.
- **Columns**: `Month_Offset`, `Avg_Retention`.
- **Usage**: Use `VLOOKUP` or `INDEX/MATCH` on `Month_Offset` to project future cohort behavior.

### Sheet: `README`
Contains version info and integrity warnings.

## 2. Usage in Modeling
- **Do NOT** hardcode values like Price or Margin in your formulas. Use the Named Ranges (e.g., `=price_basic * 12`).
- **Data Refresh**: Overwrite the `Monthly_Data` and `User_Summary` sheets when new backend data is released, but **preserve** the `Inputs` sheet values if you have customized them for scenarios.
