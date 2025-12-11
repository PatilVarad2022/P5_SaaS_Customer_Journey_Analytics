import pandas as pd
import os
import sys

DATA_DIR = "data"

def check_dates():
    print("Testing Date Formats...")
    
    # Users
    users = pd.read_csv(os.path.join(DATA_DIR, "users.csv"))
    pd.to_datetime(users["signup_date"], format="mixed", errors="raise")
    
    # Events
    events = pd.read_csv(os.path.join(DATA_DIR, "events.csv"))
    pd.to_datetime(events["event_timestamp"], format="mixed", errors="raise")
    
    # Subs
    subs = pd.read_csv(os.path.join(DATA_DIR, "subscriptions.csv"))
    pd.to_datetime(subs["start_date"], format="mixed", errors="raise")
    
    print("Date Format Tests Passed.")

if __name__ == "__main__":
    try:
        check_dates()
    except Exception as e:
        print(f"FAILED: {e}")
        sys.exit(1)
