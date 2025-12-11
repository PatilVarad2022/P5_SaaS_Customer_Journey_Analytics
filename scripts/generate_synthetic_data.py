"""
Generate basic synthetic SaaS data (users, events, subscriptions, revenue).
Only run this if your /data folder lacks realistic records.
Produces: data/users.csv, data/events.csv, data/subscriptions.csv, data/revenue.csv
"""
import random
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

N_USERS = 2000
start = datetime.now() - timedelta(days=365*1)

users = []
for i in range(1, N_USERS+1):
    signup = start + timedelta(days=random.randint(0, 365))
    users.append({
        "customer_id": f"C{i:05d}",
        "email": f"user{i}@example.com",
        "signup_date": signup.strftime("%Y-%m-%d"),
        "country": random.choice(["IN","US","GB","CA","AU"]),
        "pricing_plan": random.choice(["free","pro","enterprise"]),
        "acquisition_channel": random.choice(["organic","ads","referral","partner"]),
        "status": random.choice(["active","cancelled"])
    })
users_df = pd.DataFrame(users)
users_df.to_csv(DATA / "users.csv", index=False)

# events: signup, activate (within 14 days some), upgrade
events = []
eid = 1
for u in users:
    signup = datetime.strptime(u["signup_date"], "%Y-%m-%d")
    events.append({"event_id": f"E{eid:07d}", "customer_id": u["customer_id"], "event_name": "signup", "event_timestamp": signup.isoformat()})
    eid += 1
    if random.random() < 0.6:  # activation
        act = signup + timedelta(days=random.randint(0,14))
        events.append({"event_id": f"E{eid:07d}", "customer_id": u["customer_id"], "event_name": "activate", "event_timestamp": act.isoformat()})
        eid += 1
    if random.random() < 0.2:
        up = signup + timedelta(days=random.randint(15, 200))
        events.append({"event_id": f"E{eid:07d}", "customer_id": u["customer_id"], "event_name": "upgrade", "event_timestamp": up.isoformat()})
        eid += 1

events_df = pd.DataFrame(events)
events_df.to_csv(DATA / "events.csv", index=False)

# subscriptions and revenue (simple monthly)
subs = []
revs = []
sid = 1
for u in users:
    if random.random() < 0.25:  # convert to paid at some point
        start_date = datetime.strptime(u["signup_date"], "%Y-%m-%d") + timedelta(days=random.randint(7,120))
        price = random.choice([199, 499, 999])  # monthly INR-like
        subs.append({
            "subscription_id": f"S{sid:06d}",
            "customer_id": u["customer_id"],
            "plan": "pro",
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": "",
            "status": "active",
            "price": price,
            "billing_period": "monthly"
        })
        # generate 6 months revenue
        for m in range(6):
            date = start_date + pd.DateOffset(months=m)
            revs.append({
                "invoice_id": f"I{sid:06d}_{m}",
                "customer_id": u["customer_id"],
                "amount": price,
                "revenue_date": date.strftime("%Y-%m-%d"),
                "revenue_type": "recurring"
            })
        sid += 1

pd.DataFrame(subs).to_csv(DATA / "subscriptions.csv", index=False)
pd.DataFrame(revs).to_csv(DATA / "revenue.csv", index=False)

print("Synthetic data generated in /data")
