import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

# Paths
SRC_DIR = "02_Data_Generation/outputs"
DEST_DIR = "data"

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

ensure_dir(DEST_DIR)

print("Processing users.csv...")
users = pd.read_csv(os.path.join(SRC_DIR, "users.csv"))
users = users.rename(columns={
    "user_id": "customer_id",
    "initial_plan": "pricing_plan"
})
# Add missing columns
users["email"] = users["customer_id"] + "@example.com"
users["status"] = np.random.choice(["active", "cancelled"], size=len(users))
# Ensure required columns
required_users = ["customer_id", "email", "signup_date", "country", "pricing_plan", "acquisition_channel", "status"]
# Fill missing if any
for col in required_users:
    if col not in users.columns:
        users[col] = None 
users = users[required_users]
users.to_csv(os.path.join(DEST_DIR, "users.csv"), index=False)

print("Processing events.csv...")
events = pd.read_csv(os.path.join(SRC_DIR, "events.csv"))
events = events.rename(columns={
    "user_id": "customer_id",
    "event_type": "event_name"
})
required_events = ["event_id", "customer_id", "event_name", "event_timestamp"]
events = events[required_events]
events.to_csv(os.path.join(DEST_DIR, "events.csv"), index=False)

print("Processing subscriptions.csv...")
subs = pd.read_csv(os.path.join(SRC_DIR, "subscriptions.csv"))
subs = subs.rename(columns={
    "user_id": "customer_id",
    "plan_id": "plan",
    "amount": "price"
})
subs["billing_period"] = "monthly"
required_subs = ["subscription_id", "customer_id", "plan", "start_date", "end_date", "status", "price", "billing_period"]
subs = subs[required_subs]
subs.to_csv(os.path.join(DEST_DIR, "subscriptions.csv"), index=False)

print("Generating revenue.csv...")
# Simple expansion: one row per month for each subscription
revenue_rows = []
for _, row in subs.iterrows():
    start = pd.to_datetime(row["start_date"])
    end = pd.to_datetime(row["end_date"]) if pd.notna(row["end_date"]) else pd.to_datetime("2025-12-31") # Cap at some future date or now
    
    current = start
    invoice_idx = 1
    while current <= end and current < pd.to_datetime("today"): # Only past/current revenue
        rev_type = "new" if current == start else "recurring"
        # Checking for churn would require looking at the last month
        
        revenue_rows.append({
            "invoice_id": f"{row['subscription_id']}_inv_{invoice_idx}",
            "customer_id": row["customer_id"],
            "amount": row["price"],
            "revenue_date": current.strftime("%Y-%m-%d"),
            "revenue_type": rev_type
        })
        current += pd.DateOffset(months=1)
        invoice_idx += 1

revenue = pd.DataFrame(revenue_rows)
if not revenue.empty:
    revenue.to_csv(os.path.join(DEST_DIR, "revenue.csv"), index=False)
else:
    print("Warning: revenue DF empty")

print("Processing support_tickets.csv...")
tickets = pd.read_csv(os.path.join(SRC_DIR, "support_nps.csv"))
tickets = tickets.rename(columns={
    "user_id": "customer_id",
    "ticket_category": "issue_category"
})
tickets["priority"] = np.random.choice(["High", "Medium", "Low"], size=len(tickets))
required_tickets = ["ticket_id", "customer_id", "created_at", "resolved_at", "issue_category", "priority"]
tickets = tickets[required_tickets]
tickets.to_csv(os.path.join(DEST_DIR, "support_tickets.csv"), index=False)

print("Data preparation complete.")
