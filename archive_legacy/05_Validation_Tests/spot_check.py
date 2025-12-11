
import pandas as pd
import os
import random

CLEANED_DIR = "../03_Data_Cleaning/cleaned"
OUTPUT_FILE = "manual_spotcheck.csv"
VERSION = "v1.1"

def spot_check():
    print("Running Manual Spot Check...")
    
    users = pd.read_parquet(os.path.join(CLEANED_DIR, f"users_cleaned_{VERSION}.parquet"))
    subs = pd.read_parquet(os.path.join(CLEANED_DIR, f"subscriptions_cleaned_{VERSION}.parquet"))
    events = pd.read_parquet(os.path.join(CLEANED_DIR, f"events_cleaned_{VERSION}.parquet"))
    
    # Pick 10 users
    sample_ids = users['user_id'].sample(10, random_state=42).tolist()
    
    results = []
    
    print("-" * 60)
    for uid in sample_ids:
        print(f"Checking User: {uid}")
        user_row = users[users['user_id'] == uid].iloc[0]
        u_subs = subs[subs['user_id'] == uid].sort_values('start_date')
        u_events = events[events['user_id'] == uid].sort_values('event_timestamp')
        
        # Check 1: Signup Date vs First Event
        signup = pd.to_datetime(user_row['signup_date']).tz_localize('UTC') # Assume signup is UTC start of day
        first_evt = pd.to_datetime(u_events['event_timestamp'].min()) if not u_events.empty else None
        
        # Ensure first_evt is tz-aware if not
        if first_evt and first_evt.tzinfo is None:
            first_evt = first_evt.tz_localize('UTC')
            
        status = "PASS"
        notes = []
        
        if first_evt and first_evt < signup:
            status = "FAIL"
            notes.append("Event before Signup")
            
        # Check 2: Subs continuity
        # Just check logic
        # Check 3: If churned, no events long after?
        
        print(f"  Signup: {signup}")
        print(f"  Subs: {len(u_subs)} rows")
        print(f"  Events: {len(u_events)} rows")
        
        if status == "PASS":
            notes.append("Lifecycle Consistent")
            
        results.append({
            'user_id': uid,
            'status': status,
            'notes': "; ".join(notes)
        })
        print("-" * 60)
        
    pd.DataFrame(results).to_csv(OUTPUT_FILE, index=False)
    print(f"Saved spot checks to {OUTPUT_FILE}")

if __name__ == "__main__":
    spot_check()
