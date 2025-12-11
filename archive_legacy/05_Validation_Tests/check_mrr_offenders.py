
import pandas as pd
import os
import sys

DERIVED_DIR = "../04_Derived_Tables"
OUTPUT_FILE = "mrr_offenders.csv"

def check_balance():
    print("Checking MRR Balance...")
    
    try:
        df = pd.read_csv(os.path.join(DERIVED_DIR, "monthly_revenue.csv"))
    except FileNotFoundError:
        print("monthly_revenue.csv not found.")
        return

    # Check Columns
    req_cols = ['MRR_total', 'MRR_start', 'new_MRR', 'expansion_MRR', 'contraction_MRR', 'churned_MRR']
    for c in req_cols:
        if c not in df.columns:
            print(f"Missing column {c}")
            return

    offenders = []
    
    for i, row in df.iterrows():
        start = row['MRR_start']
        end_val = row['MRR_total']
        new = row['new_MRR']
        exp = row['expansion_MRR']
        cont = row['contraction_MRR']
        churn = row['churned_MRR']
        
        # Calc logic: End = Start + New + Exp - Cont - Churn
        calc_end = start + new + exp - cont - churn
        
        diff = abs(end_val - calc_end)
        
        if diff > 1e-4: # Floating tolerance
            print(f"FAIL: Month {row['month']} Diff {diff}")
            offenders.append({
                'month': row['month'],
                'user_id': 'AGGREGATE_LEVEL_FAILURE', # Since we don't have user level detail in CSV
                'diff': diff,
                'reason': 'Bridge Mismatch'
            })
            
    # Save offenders
    out_df = pd.DataFrame(offenders)
    if os.path.exists(OUTPUT_FILE): os.remove(OUTPUT_FILE) # clean old
    
    if not out_df.empty:
        out_df.to_csv(OUTPUT_FILE, index=False)
        print(f"Found {len(out_df)} mismatches. Saved to {OUTPUT_FILE}")
    else:
        # Create empty file with headers
        pd.DataFrame(columns=['user_id', 'start_date', 'end_date', 'mrr', 'transaction_type', 'reason_flag']).to_csv(OUTPUT_FILE, index=False)
        print("Balance Check PASS. No offenders.")

if __name__ == "__main__":
    check_balance()
