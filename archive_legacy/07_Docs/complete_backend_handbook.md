# Backend Handbook & Data Dictionary (v1.1)

## 1. ETL Flow (v1.1)
Raw Generation -> Cleaning (v1.1) -> Derivation (v1.1) -> Validation -> Exports

```
[Generator] --> /02_Data_Generation/outputs (Raw CSV)
     |
     v
[Cleaner] ----> /03_Data_Cleaning/cleaned (Standardized *_v1.1.parquet)
     |
     v
[Derivation] -> /04_Derived_Tables (*_v1.1.parquet + Aggregated Metrics)
     |
     v
[Validation] -> DQ Reports (Pass/Fail) + Spot Checks
     |
     v
[Export] -----> /06_Exports/tableau_ready (Clean Names)
         -----> /06_Exports/clv_inputs_v1.1.xlsx
```

## 2. Metric Logic (MRR Bridge)
MRR is calculated using a strict snapshot approach to ensure `End = Start + New + Expansion - Contraction - Churn`.
- **New**: Month Start MRR = 0, Month End MRR > 0.
- **Churn**: Month Start MRR > 0, Month End MRR = 0.
- **Expansion**: Start > 0, End > Start.
- **Contraction**: Start > 0, End < Start (but > 0).

## 3. Assumptions & Synthetic Artifacts
- **Seasonality**: Built-in weightings favor Q1/Q4.
- **Trial**: Strict 14-day trial logic.
- **Churn**: Randomly assigned with correlation to low NPS.
- **Data Completeness**: 12 months (2024).

## 4. Operational Guide
To refresh data:
```bash
# 1. Pipeline
cd /04_Derived_Tables
python derive_tables.py

# 2. Export
cd /06_Exports
python export_data.py
python generate_excel.py
```

## 5. Exports
Primary Keys:
- `user_master`: `user_id`
- `monthly_revenue`: `month`
- `cohort_retention`: `cohort`, `month_offset`

### Example Joins for Dashboarding
1. **Unify Funnel with User Dimensions**:
   ```sql
   /* Link funnel monthly aggregates to user demographics (Conceptual Blend) */
   SELECT 
     f.month, 
     f.signups, 
     f.paid_conversions,
     u.acquisition_channel 
   FROM monthly_funnel f
   LEFT JOIN user_master u ON f.month = u.cohort_month 
   /* Note: Funnel table is pre-aggregated, so better to aggregate user_master directly in Tableau */
   ```

2. **Churn Analysis**:
   ```python
   # Pandas Merge for Churn Flags
   df = pd.read_parquet('user_master.parquet')
   churn = pd.read_parquet('churn_flags.parquet')
   full_view = df.merge(churn, on='user_id', how='left')
   ```

3. **Retention Heatmap**:
   - Use `cohort_retention.parquet` directly.
   - Rows: `cohort`
   - Columns: `month_offset`
   - Color: `retention_rate`

4. **Support Impact on NPS**:
   ```sql
   SELECT 
     s.*, 
     u.current_plan 
   FROM support_summary s
   /* No direct join key to user_master unless blending on Month */
   ```

