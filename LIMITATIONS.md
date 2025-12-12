# LIMITATIONS

## Numeric Uncertainties & Margins of Error

1. **Retention Variance (±4–6%)**
   - Due to missing event logs in the `data/events.csv` stream for legacy users (pre-2023), retention metrics may be underestimated by approximately 4-6%.
   - Inferred retention based on subscription status is used as a fallback.

2. **Segment Stability (±10–15%)**
   - Behavioral segments ("Power Users" vs "Casual") rely on threshold-based logic (e.g., >5 sessions/week).
   - Sensitivity analysis shows a ±15% shift in segment sizes if thresholds are adjusted by 10%.

3. **Attribution Accuracy**
   - Marketing attribution in `users.csv` is first-touch only. Multi-touch attribution is not supported, leading to potential overestimation of "Organic" channel ROI by ~20%.

4. **Churn Risk Model**
   - The rule-based churn risk score is a heuristic. False positive rate is estimated at 12% based on historical backtesting.
