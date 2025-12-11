import pandas as pd
import os

DATA_DIR = "data"
OUTPUT_DIR = os.path.join("outputs", "tableau_ready")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def export_extracts():
    print("Generating Tableau extracts...")
    
    # Load core data
    try:
        users = pd.read_csv(os.path.join(DATA_DIR, "users.csv"))
        subs = pd.read_csv(os.path.join(DATA_DIR, "subscriptions.csv"))
        revenue = pd.read_csv(os.path.join(DATA_DIR, "revenue.csv"))
    except FileNotFoundError as e:
        print(f"Error loading data: {e}")
        return

    # 1. Customer Master Extract (Flat table: User Info + Current Subscription Status)
    # Get latest subscription per user
    latest_subs = subs.sort_values("start_date").groupby("customer_id").last().reset_index()
    
    master = pd.merge(users, latest_subs, on="customer_id", how="left", suffixes=("", "_sub"))
    
    # Clean up column names if needed
    master.to_csv(os.path.join(OUTPUT_DIR, "customer_master_extract.csv"), index=False)
    print(" - customer_master_extract.csv")
    
    # 2. Revenue Transaction Extract (Optimized for financial dashboards)
    revenue.to_csv(os.path.join(OUTPUT_DIR, "revenue_transaction_extract.csv"), index=False)
    print(" - revenue_transaction_extract.csv")
    
    # 3. Events Aggregate (Optional: Daily events by type)
    if os.path.exists(os.path.join(DATA_DIR, "events.csv")):
        events = pd.read_csv(os.path.join(DATA_DIR, "events.csv"), parse_dates=["event_timestamp"])
        events["date"] = events["event_timestamp"].dt.date
        daily_events = events.groupby(["date", "event_name"]).size().reset_index(name="count")
        daily_events.to_csv(os.path.join(OUTPUT_DIR, "daily_events_extract.csv"), index=False)
        print(" - daily_events_extract.csv")

    print(f"Extracts saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    export_extracts()
