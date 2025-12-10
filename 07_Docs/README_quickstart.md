# Frontend Quickstart v1.1

1. **Locate Data**: All Tableau-ready files are in `/06_Exports/tableau_ready/`. 
   - Files are Parquet format (clean names).
   - Validation Status: **PASS**.
   - **Note**: All timestamps are UTC — set Tableau datasource to interpret timestamps as UTC (or convert on import).
2. **Connect**: Open Tableau, select "More..." -> "Parquet" and load `user_master.parquet` as your primary table.
3. **Relationships**: 
   - Link `monthly_revenue.parquet` to `user_master` isn't direct (Month aggregation vs User granularity). Treat Revenue as a separate data source or blend on Date.
   - Link `monthly_funnel.parquet` on `month`.
4. **Excel Modeling**: Open `/06_Exports/clv_inputs_v1.1.xlsx`.
   - `Monthly_Data` sheet contains pre-calculated MRR bridge.
5. **Debug**: Use `/06_Exports/debug_csvs/` for quick text verification.
