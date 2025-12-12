import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DIR = ROOT / "data" / "sample"

def create_sample_data():
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Users
    users = pd.DataFrame({
        "customer_id": ["C1", "C2", "C3"],
        "signup_date": ["2024-01-01", "2024-01-02", "2024-01-03"]
    })
    users.to_csv(SAMPLE_DIR / "users.csv", index=False)
    
    # Events
    events = pd.DataFrame({
        "event_id": ["E1", "E2"],
        "customer_id": ["C1", "C2"],
        "event_name": ["activate", "activate"],
        "event_timestamp": ["2024-01-02 10:00:00", "2024-01-05 10:00:00"]
    })
    events.to_csv(SAMPLE_DIR / "events.csv", index=False)
    
    # Subscriptions
    subs = pd.DataFrame({
        "subscription_id": ["S1"],
        "customer_id": ["C1"],
        "start_date": ["2024-01-10"],
        "end_date": [None],
        "status": ["active"],
        "price": [100]
    })
    subs.to_csv(SAMPLE_DIR / "subscriptions.csv", index=False)
    
    # Revenue (for load_data compatibility)
    rev = pd.DataFrame({
        "revenue_id": ["R1"],
        "customer_id": ["C1"],
        "amount": [100],
        "revenue_date": ["2024-01-10"]
    })
    rev.to_csv(SAMPLE_DIR / "revenue.csv", index=False)
    
    print("Sample data created in data/sample/")

if __name__ == "__main__":
    create_sample_data()
