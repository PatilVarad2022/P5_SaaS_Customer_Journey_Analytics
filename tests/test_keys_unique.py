import pandas as pd
import os
import sys

DATA_DIR = "data"

def check_keys():
    print("Testing Unique Keys...")
    
    # Users
    users = pd.read_csv(os.path.join(DATA_DIR, "users.csv"))
    assert users["customer_id"].is_unique, "customer_id in users.csv is not unique"
    
    # Subscriptions
    subs = pd.read_csv(os.path.join(DATA_DIR, "subscriptions.csv"))
    assert subs["subscription_id"].is_unique, "subscription_id in subscriptions.csv is not unique"
    
    print("Unique Key Tests Passed.")

if __name__ == "__main__":
    try:
        check_keys()
    except AssertionError as e:
        print(f"FAILED: {e}")
        sys.exit(1)
