import pandas as pd
import os
import sys

DATA_DIR = "data"
REQUIRED_FILES = {
    "users.csv": ["customer_id", "signup_date", "status"],
    "events.csv": ["event_id", "customer_id", "event_name", "event_timestamp"],
    "subscriptions.csv": ["subscription_id", "customer_id", "plan", "start_date", "status"],
    "revenue.csv": ["invoice_id", "customer_id", "amount", "revenue_date", "revenue_type"],
}

def check_schema():
    print("Testing Schema...")
    for f, cols in REQUIRED_FILES.items():
        path = os.path.join(DATA_DIR, f)
        assert os.path.exists(path), f"File {f} is missing"
        
        df = pd.read_csv(path)
        for c in cols:
            assert c in df.columns, f"Column {c} missing in {f}"
    print("Schema Tests Passed.")

if __name__ == "__main__":
    try:
        check_schema()
    except AssertionError as e:
        print(f"FAILED: {e}")
        sys.exit(1)
