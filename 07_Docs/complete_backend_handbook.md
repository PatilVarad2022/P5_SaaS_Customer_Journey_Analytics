# Backend Handbook & Data Dictionary

## 1. ETL Flow
Raw Generation -> Cleaning -> Derivation -> Validation -> Exports

```
[Generator] --> /02_Data_Generation/outputs (Raw CSV)
     |
     v
[Cleaner] ----> /03_Data_Cleaning/cleaned (Standardized Parquet/CSV)
     |
     v
[Derivation] -> /04_Derived_Tables (Aggregated Metrics)
     |
     v
[Validation] -> DQ Reports (Pass/Fail)
     |
     v
[Export] -----> /06_Exports/tableau_ready (Final Consumption)
```

## 2. Data Dictionary
(See /01_Dataset_Specs/schema_v1.md for full detail)

## 3. Assumptions & Synthetic Artifacts
- **Seasonality**: Built-in weightings favor Q1/Q4.
- **Trial**: Strict 14-day trial logic.
- **Churn**: Randomly assigned with correlation to low NPS.
- **Data Completeness**: 12 months (2024).

## 4. Operational Guide

### How to Reproduce (Regenerate Data)
```bash
cd /02_Data_Generation
python generate_synthetic_data.py --size 10000
```

### Full Pipeline Refresh
```bash
# 1. Generate
cd /02_Data_Generation
python generate_synthetic_data.py --size 10000

# 2. Clean
cd ../03_Data_Cleaning
python clean_data.py

# 3. Derive
cd ../04_Derived_Tables
python derive_tables.py

# 4. Validate
cd ../05_Validation_Tests
python validate_data.py

# 5. Export
cd ../06_Exports
python export_data.py
python generate_excel.py
```
