# Data Quality Report

## Summary

- **Integrity: Subscriptions -> Users**: PASS - 0 orphans
- **Integrity: Events -> Users**: PASS - 0 orphans
- **Uniqueness: Users PK**: PASS - 0 duplicates
- **Date Window**: PASS - Range: 2024-01-01T08:49:37Z to 2024-12-30T23:59:31Z
- **Sanity: MRR Calculation**: FAIL - Table: 311809.0 vs Calc: 312065.0 (Diff: 256.0)
- **Sanity: Retention Decay**: PASS - Retention generally decreases
- **Anomaly: Signups Stability**: PASS - 0 months with >50% change