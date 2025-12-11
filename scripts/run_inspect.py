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

def validate_date(series, name):
    try:
        pd.to_datetime(series, format="mixed", errors="raise")
    except Exception as e:
        print(f"FAILED: Date format check in {name}: {e}")
        return False
    return True

def run_checks():
    failures = 0
    
    print("Starting inspection...")
    
    for filename, required_cols in REQUIRED_FILES.items():
        filepath = os.path.join(DATA_DIR, filename)
        if not os.path.exists(filepath):
            print(f"FAILED: {filename} missing.")
            failures += 1
            continue
            
        try:
            df = pd.read_csv(filepath)
            
            # Schema Check
            missing = [col for col in required_cols if col not in df.columns]
            if missing:
                print(f"FAILED: {filename} missing columns: {missing}")
                failures += 1
            else:
                print(f"PASSED: {filename} schema check.")
                
            # Null Check
            nulls = df[required_cols].isnull().sum()
            if nulls.any():
                print(f"FAILED: {filename} nulls in critical columns:\n{nulls[nulls>0]}")
                failures += 1
            else:
                print(f"PASSED: {filename} null checks.")
                
            # Unique Key Check
            if filename == "users.csv":
                if not df["customer_id"].is_unique:
                    print(f"FAILED: users.csv customer_id not unique.")
                    failures += 1
            if filename == "subscriptions.csv":
                if not df["subscription_id"].is_unique:
                    print(f"FAILED: subscriptions.csv subscription_id not unique.")
                    failures += 1

            # Date Check
            date_cols = [c for c in df.columns if ("date" in c or "timestamp" in c or "at" in c) and "status" not in c]
            for dc in date_cols:
                if not validate_date(df[dc], f"{filename}.{dc}"):
                    failures += 1

        except Exception as e:
            print(f"FAILED: Could not read or process {filename}: {e}")
            failures += 1

    if failures > 0:
        print(f"\nInspection FAILED with {failures} errors.")
        sys.exit(1)
    else:
        print("\nInspection PASSED.")
        sys.exit(0)

if __name__ == "__main__":
    run_checks()
