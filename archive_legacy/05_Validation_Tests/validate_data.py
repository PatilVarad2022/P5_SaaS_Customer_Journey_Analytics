
import pandas as pd
import os
import sys


import pandas as pd
import os
import sys
import json
from datetime import datetime

CLEANED_DIR = "../03_Data_Cleaning/cleaned"
DERIVED_DIR = "../04_Derived_Tables"
REPORT_FILE_MD = "DQ_report.md"
REPORT_FILE_JSON = "DQ_report.json"
VERSION = "v1.1"

def validate():
    print("Running validation tests...")
    
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "tables": {},
        "tests": []
    }
    
    report_lines = ["# Data Quality Report", "", "## Summary", ""]
    failures = 0
    
    # Load Data
    try:
        users = pd.read_parquet(os.path.join(CLEANED_DIR, f"users_cleaned_{VERSION}.parquet"))
        subs = pd.read_parquet(os.path.join(CLEANED_DIR, f"subscriptions_cleaned_{VERSION}.parquet"))
        events = pd.read_parquet(os.path.join(CLEANED_DIR, f"events_cleaned_{VERSION}.parquet"))
        rev = pd.read_csv(os.path.join(DERIVED_DIR, f"monthly_revenue_{VERSION}.csv"))
        funnel = pd.read_csv(os.path.join(DERIVED_DIR, f"monthly_funnel_{VERSION}.csv"))
        cohort = pd.read_csv(os.path.join(DERIVED_DIR, f"cohort_retention_{VERSION}.csv"))
        
        # Log table stats
        for name, df in [("users", users), ("subs", subs), ("events", events), ("rev", rev)]:
            report_data["tables"][name] = {"rows": len(df), "columns": list(df.columns)}
            
        # Convert dates
        subs['start_date'] = pd.to_datetime(subs['start_date'])
        subs['end_date'] = pd.to_datetime(subs['end_date'])
        events['event_timestamp'] = pd.to_datetime(events['event_timestamp'])
            
    except Exception as e:
        print(f"FATAL: Could not load files: {e}")
        return
        
    def check(name, condition, msg, severity="Critical"):
        nonlocal failures
        status = "PASS" if condition else "FAIL"
        if not condition: 
            if severity == "Critical": failures += 1
        
        # MD
        report_lines.append(f"- **{name}**: {status} - {msg}")
        # JSON
        report_data["tests"].append({
            "test_name": name,
            "status": status,
            "message": msg,
            "severity": severity
        })
        return condition

    # 1. Integrity
    orphans_sub = (~subs['user_id'].isin(users['user_id'])).sum()
    check("Integrity: Subscriptions -> Users", orphans_sub == 0, f"{orphans_sub} orphans")
    
    orphans_evt = (~events['user_id'].isin(users['user_id'])).sum()
    check("Integrity: Events -> Users", orphans_evt == 0, f"{orphans_evt} orphans")
    
    # 2. Uniqueness
    dup_users = users['user_id'].duplicated().sum()
    check("Uniqueness: Users PK", dup_users == 0, f"{dup_users} duplicates")
    
    # 3. Date Window
    evt_min = events['event_timestamp'].min()
    evt_max = events['event_timestamp'].max()
    check("Date Window", '2024' in str(evt_min) and '2024' in str(evt_max), f"Range: {evt_min} to {evt_max}")
    
    # 4. Aggregation Sanity - MRR Calculation
    # New Strict Bridge Check from Rev Table Itself
    # Diff column exists now
    if 'validation_diff' in rev.columns:
        max_diff = rev['validation_diff'].max()
        check("MRR Calculation Bridge", max_diff < 1e-4, f"Max Diff: {max_diff}")
    else:
        check("MRR Calculation Bridge", False, "validation_diff column missing")

    # Sum check external (Sanity)
    # Check Dec 2024
    mrr_dec_table = rev[rev['month'] == '2024-12']['MRR_total'].values[0] if not rev[rev['month'] == '2024-12'].empty else 0
    # Recalc from subs
    dec_end = pd.Timestamp('2024-12-31 23:59:59')
    # Active logic same as derive
    # Inclusive End: End + 1 day > Target (23:59:59)
    eff_end = subs['end_date'] + pd.Timedelta(days=1)
    
    mask = (subs['start_date'] <= dec_end) & \
           ((eff_end > dec_end) | (subs['end_date'].isnull())) & \
           (subs['transaction_type'] != 'churn') & (subs['amount'] > 0)
           
    active_subs = subs[mask]
    mrr_dec_calc = active_subs.groupby('user_id')['amount'].sum().sum()
    
    diff = abs(mrr_dec_table - mrr_dec_calc)
    check("Sanity: MRR Dec vs Subs", diff < 100, f"Table: {mrr_dec_table} vs Calc: {mrr_dec_calc} (Diff: {diff})")
    
    # 5. Metric Sanity
    # Retention Monotonic
    ret_avg = cohort.groupby('month_offset')['retention_rate'].mean()
    monotonic = True
    for i in range(len(ret_avg)-1):
        if ret_avg.iloc[i+1] > ret_avg.iloc[i] + 0.05:
            monotonic = False
    check("Sanity: Retention Decay", monotonic, "Retention generally decreases", "Medium")
    
    # 6. Anomalies
    signups = funnel['signups']
    jumps = 0
    for i in range(1, len(signups)):
        pct_change = abs(signups.iloc[i] - signups.iloc[i-1]) / (signups.iloc[i-1] + 1)
        if pct_change > 0.5:
            jumps += 1
    check("Anomaly: Signups Stability", jumps == 0, f"{jumps} months with >50% change", "Medium")
    
    # Final Output
    with open(REPORT_FILE_MD, 'w') as f:
        f.write('\n'.join(report_lines))
        
    with open(REPORT_FILE_JSON, 'w') as f:
        json.dump(report_data, f, indent=2)
        
    print(f"Validation complete. {failures} critical failures.")
    if failures > 0:
        pass

if __name__ == "__main__":
    validate()
