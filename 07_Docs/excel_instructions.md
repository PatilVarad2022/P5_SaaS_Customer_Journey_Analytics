# Excel Integration Instructions

## File: `clv_inputs.xlsx`
This file connects the backend SaaS data to your financial models (CLV, LTV/CAC).

## Sheets
1. **Inputs**: Key assumptions (Gross Margin, Discount Rate).
   - **Named Ranges**: `Gross_Margin`, `Discount_Rate`.
2. **Monthly_Data**: Rollup of MRR and Active Users from `monthly_revenue.csv`.
   - Columns: `MRR_total`, `new_MRR`, `churned_MRR`, `ARPU`.
3. **User_Summary**: Average retention curve derived from cohort analysis.
   - Columns: `Month_Offset`, `Avg_Retention`.

## Usage in Modeling
- Link your calculation cells to these sheets.
- Do not edit the data in `Monthly_Data` or `User_Summary` manually; strictly treat as an import.
- Edit `Inputs` to test sensitivity scenarios.
