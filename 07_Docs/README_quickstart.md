# Frontend Quickstart

1. **Locate Data**: All Tableau-ready files are in `/06_Exports/tableau_ready/`. Use these Parquet files for best performance, or convert to CSV if needed.
2. **Connect**: Open Tableau, select "More..." -> "Parquet" and load `user_master_cleaned.parquet` as your primary table.
3. **Relationships**: Link `monthly_revenue` to `user_master` on `month` (aggregates) or verify independent use cases.
4. **Excel Modeling**: Open `/06_Exports/clv_inputs.xlsx` to see pre-calculated Monthly MRR and Retention feeds.
5. **Check Quality**: Review `/05_Validation_Tests/DQ_report.md` to ensure data hygiene before reporting.
6. **Refresh**: If you need new data, ask Backend to run the "Full Pipeline Refresh" command sequence.
