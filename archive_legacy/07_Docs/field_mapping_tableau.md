# Tableau Field Mapping

## 1. Executive KPI Dashboard
**Visuals**: MRR, Active Users, ARPU.
- **Source**: `monthly_revenue.parquet`
- **Fields**:
  - `month` (Date) -> Columns
  - `MRR_total` (Measure) -> Rows
  - `active_paid_users` (Measure)
  - `ARPU` (Measure)

## 2. Revenue Waterfall (Bridge)
**Visuals**: Walk from Start to End MRR.
- **Source**: `monthly_revenue.parquet`
- **Fields**:
  - `new_MRR` (Positive Bar)
  - `expansion_MRR` (Positive Bar)
  - `contraction_MRR` (Negative Bar)
  - `churned_MRR` (Negative Bar)
  - `MRR_total` (Line/End Bar)

## 3. Funnel Analysis
**Visuals**: Conversion Rates.
- **Source**: `monthly_funnel.parquet`
- **Fields**:
  - `signups`
  - `activations`
  - `paid_conversions`
  - *Calc*: `Conversion Rate` = `paid_conversions` / `signups`

## 4. Retention Heatmap
**Visuals**: Cohort Analysis.
- **Source**: `cohort_retention.parquet`
- **Fields**:
  - `cohort` (Y-Axis)
  - `month_offset` (X-Axis)
  - `retention_rate` (Color/Text)

## 5. Churn Analysis
**Visuals**: Churn Reasons/Flags.
- **Source**: `churn_flags.parquet` JOIN `user_master.parquet`
- **Join**: `user_id` = `user_id`
- **Fields**:
  - `churn_reason` (if available in future, currently flag only)
  - `churn_date`
  - `acquisition_channel` (from user_master)
