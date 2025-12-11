
import pandas as pd
import numpy as np
import uuid
import random
import os
import argparse
from datetime import datetime, timedelta

# Configuration
OUTPUT_DIR = "outputs"
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2024, 12, 31)
COUNTRIES = ['US', 'UK', 'DE', 'FR', 'ES', 'IN']
CHANNELS = ['Organic', 'Paid_Search', 'Referral', 'Social', 'Direct', 'Email']
PLANS = ['Free', 'Trial_Basic', 'Trial_Pro']
PAID_PLANS = ['Basic_Monthly', 'Pro_Monthly', 'Basic_Annual', 'Pro_Annual']
EVENT_TYPES = [
    'login', 'dashboard_view', 'report_create', 'report_export',
    'feature_x_use', 'settings_change', 'invite_user', 'page_view',
    'campaign_create', 'data_import', 'api_call', 'logout'
]
EVENT_WEIGHTS = [0.25, 0.20, 0.10, 0.05, 0.10, 0.02, 0.01, 0.15, 0.05, 0.03, 0.02, 0.02]

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def generate_users(num_users):
    print(f"Generating {num_users} users...")
    users = []
    
    # Seasonality weights (higher in Q1/Q4)
    # Jan-Dec weights
    month_weights = [1.2, 1.1, 1.1, 1.0, 0.9, 0.8, 0.8, 0.9, 1.0, 1.1, 1.2, 0.9]
    total_weight = sum(month_weights)
    probs = [w/total_weight for w in month_weights]
    
    days_range = (END_DATE - START_DATE).days
    
    for _ in range(num_users):
        user_id = f"usr_{uuid.uuid4().hex[:8]}"
        
        # Determine signup date based on seasonality
        # Pick a month
        month_idx = np.random.choice(range(12), p=probs)
        # Random day in that month (simplified: just pick day in year, filter later or logic)
        # Better: Pick random day in year considering weight? 
        # Simple approach: Random day in year, then if it falls in month X, keep it with prob Y?
        # Let's just pick a random day from START to END uniformly for simplicity then adjust? 
        # Actually random day within the specific chosen month is better.
        
        # Calculate start of month
        y = 2024
        m = month_idx + 1
        d_start = datetime(y, m, 1)
        # Next month
        if m == 12:
            d_end = datetime(y+1, 1, 1)
        else:
            d_end = datetime(y, m+1, 1)
            
        delta_days = (d_end - d_start).days
        signup_date = d_start + timedelta(days=random.randint(0, delta_days - 1))
        
        # B2B logic: some users share company_id
        if random.random() < 0.3: # 30% join existing company
             # This is hard to do in one pass without state. 
             # Let's just assign random company IDs, then post-process duplications?
             # Or just generate company_id. 
             pass
        company_id = f"cmp_{uuid.uuid4().hex[:6]}" # Placeholder, effectively unique mostly
        
        users.append({
            'user_id': user_id,
            'company_id': company_id,
            'signup_date': signup_date,
            'country': np.random.choice(COUNTRIES),
            'acquisition_channel': np.random.choice(CHANNELS),
            'initial_plan': np.random.choice(PLANS, p=[0.2, 0.4, 0.4]), # Mostly trials
            'job_role': np.random.choice(['Admin', 'Member', 'Viewer'], p=[0.2, 0.5, 0.3])
        })
        
    df = pd.DataFrame(users)
    
    # Simulate B2B clustering
    # Randomly overwrite company_ids to correlate them
    company_pool = df['company_id'].sample(int(num_users * 0.2)).values # pool of companies
    # Assign some users to these companies
    mask = np.random.rand(len(df)) < 0.25
    df.loc[mask, 'company_id'] = np.random.choice(company_pool, size=mask.sum())
    
    return df

def generate_subscriptions(users_df):
    print("Generating subscriptions...")
    subs = []
    
    # Prices
    prices = {
        'Free': 0.0,
        'Basic_Monthly': 29.0,
        'Pro_Monthly': 99.0,
        'Basic_Annual': 290.0, # ~24/mo
        'Pro_Annual': 990.0   # ~82.5/mo
    }
    
    for _, user in users_df.iterrows():
        # Everyone starts with initial plan (Trial or Free)
        start_date = user['signup_date']
        plan = user['initial_plan']
        
        # Trial Entry
        sub_id = f"sub_{uuid.uuid4().hex[:6]}"
        is_trial = 'Trial' in plan
        
        # Trial length
        trial_days = 14 if is_trial else 30 # Free users stay free for a bit?
        
        if is_trial:
            end_date = start_date + timedelta(days=trial_days)
            subs.append({
                'subscription_id': sub_id,
                'user_id': user['user_id'],
                'plan_id': plan,
                'start_date': start_date,
                'end_date': end_date,
                'amount': 0.0,
                'status': 'Trial',
                'transaction_type': 'New_Business'
            })
            
            # Conversion Check
            # Conversion rates: High for Paid Search, Low for Social
            base_conv = 0.20
            if user['acquisition_channel'] == 'Paid_Search': base_conv += 0.1
            if user['acquisition_channel'] == 'Social': base_conv -= 0.05
            
            if random.random() < base_conv:
                # Converted
                new_start = end_date + timedelta(days=1)
                
                # Choose Paid Plan
                paid_plan = np.random.choice(PAID_PLANS, p=[0.4, 0.3, 0.2, 0.1])
                paid_amt = prices[paid_plan]
                
                # Duration
                is_annual = 'Annual' in paid_plan
                duration = 365 if is_annual else 30
                
                # Add Renewal / Churn Logic logic
                # For simplicity, let's just create the first paid period
                # And maybe one renewal if time permits within the year
                
                paid_end = new_start + timedelta(days=duration)
                
                # Check if fits in current year (or slightly after)
                # If new_start > END_DATE, skip
                if new_start <= END_DATE:
                    sub_id_new = f"sub_{uuid.uuid4().hex[:6]}"
                    subs.append({
                        'subscription_id': sub_id_new,
                        'user_id': user['user_id'],
                        'plan_id': paid_plan,
                        'start_date': new_start,
                        'end_date': paid_end if paid_end <= END_DATE else None, # Active if end > window? Or strictly define logic
                        # But for MRR calc, we need valid ranges. 
                        # Let's say if paid_end > END_DATE or not churned, then end_date is None for 'Active' status logic later, 
                        # but here the schema says "NULL if active".
                        # Let's keep date for calculation, remove for final export if active.
                        'amount': paid_amt,
                        'status': 'Active', 
                        'transaction_type': 'New_Business' # Conversion from trial is technically New Business MRR
                    })
                    
                    # Churn check after this period
                    if paid_end <= END_DATE:
                         # Decide if churn or renew
                         if random.random() < 0.15: # Churn
                             # Add churn record? Or just mark previous as ended?
                             # Usually Churn is an event or state change. 
                             # The schema asks for "start/end records, expansions/contractions".
                             # So we just stop having records.
                             # But we might need a specific "Churn" transaction row? 
                             # Schema says transaction_type: New_Business, Renewal, Expansion, Contraction, Churn.
                             # If churn, we might add a row with 0 MRR starting at churn date? 
                             # Or just valid types in the active period.
                             # Let's add a Churn event row for clarity if the user wants "Churn" as a type.
                             subs.append({
                                'subscription_id': f"sub_{uuid.uuid4().hex[:6]}",
                                'user_id': user['user_id'],
                                'plan_id': paid_plan,
                                'start_date': paid_end + timedelta(days=1),
                                'end_date': paid_end + timedelta(days=1),
                                'amount': 0.0,
                                'status': 'Cancelled',
                                'transaction_type': 'Churn'
                            })
                         else:
                             # Renew
                             sub_id_renew = f"sub_{uuid.uuid4().hex[:6]}"
                             subs.append({
                                'subscription_id': sub_id_renew,
                                'user_id': user['user_id'],
                                'plan_id': paid_plan,
                                'start_date': paid_end + timedelta(days=1),
                                'end_date': None, # Assumed active for rest of window
                                'amount': paid_amt,
                                'status': 'Active',
                                'transaction_type': 'Renewal'
                            })

        else:
             # Free user
             pass
             
    return pd.DataFrame(subs)

def generate_events(users_df, subs_df):
    print("Generating events...")
    events = []
    
    # Pre-compute valid ranges for each user (signup to today/churn)
    # This is complex. Simplified: Generate random events between signup and min(churn_date, END_DATE)
    
    # Get max date per user
    user_max_dates = {}
    for uid in users_df['user_id']:
        user_max_dates[uid] = END_DATE
    
    # Adjust for churned users
    churn_subs = subs_df[subs_df['transaction_type'] == 'Churn']
    for _, row in churn_subs.iterrows():
        user_max_dates[row['user_id']] = row['start_date']
        
    for _, user in users_df.iterrows():
        uid = user['user_id']
        start = user['signup_date']
        end = user_max_dates.get(uid, END_DATE)
        
        if start >= end:
            continue
            
        # Number of events
        # Heavy users vs light users
        num_events = random.randint(6, 50)
        
        # Taxonomy
        
        # Timestamps
        # Generate random seconds offsets
        total_seconds = (end - start).total_seconds()
        if total_seconds <= 0: continue
        
        offsets = sorted(np.random.randint(0, int(total_seconds), num_events))
        
        for i in range(num_events):
            evt_ts = start + timedelta(seconds=int(offsets[i]))
            evt_type = np.random.choice(EVENT_TYPES, p=EVENT_WEIGHTS)
            
            events.append({
                'event_id': f"evt_{uuid.uuid4().hex[:8]}",
                'user_id': uid,
                'event_timestamp': evt_ts,
                'event_type': evt_type,
                'session_id': f"ses_{uuid.uuid4().hex[:8]}", # Simplified session logic
                'device': np.random.choice(['Desktop', 'Mobile', 'Tablet'], p=[0.7, 0.2, 0.1]) 
            })
            
    return pd.DataFrame(events)

def generate_support(users_df, subs_df):
    print("Generating support/NPS...")
    tickets = []
    
    # Correlate with churn
    churn_users = set(subs_df[subs_df['transaction_type'] == 'Churn']['user_id'])
    
    for _, user in users_df.iterrows():
        uid = user['user_id']
        # Chance of ticket
        prob = 0.3 if uid in churn_users else 0.1
        
        if random.random() < prob:
            # Create ticket
            t_created = user['signup_date'] + timedelta(days=random.randint(1, 60))
            if t_created > END_DATE: continue
            
            tkt_id = f"tkt_{uuid.uuid4().hex[:4]}"
            
            cat = np.random.choice(['Billing', 'Technical', 'Feature_Req', 'Access'])
            
            # Resolution
            tat_hours = random.randint(1, 100) # Long tail
            t_resolved = t_created + timedelta(hours=tat_hours)
            if t_resolved > END_DATE: t_resolved = None
            
            # NPS
            nps = None
            if t_resolved:
                # Lower score if churned
                if uid in churn_users:
                    nps = np.random.choice(range(11), p=[0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.05, 0.05]) # mostly low
                else:
                    nps = np.random.choice(range(11), p=[0.01]*7 + [0.1, 0.2, 0.3, 0.33]) # mostly high
                    
            tickets.append({
                'ticket_id': tkt_id,
                'user_id': uid,
                'created_at': t_created,
                'resolved_at': t_resolved,
                'ticket_category': cat,
                'nps_score': nps,
                'nps_comment': "Sample comment" if random.random() < 0.3 else None
            })
            
    return pd.DataFrame(tickets)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--size', type=int, default=10000, help='Number of users to generate')
    args = parser.parse_args()
    
    ensure_dir(os.path.join(OUTPUT_DIR))
    
    # 1. Users
    users_df = generate_users(args.size)
    
    # 2. Subscriptions
    subs_df = generate_subscriptions(users_df)
    
    # 3. Events
    events_df = generate_events(users_df, subs_df)
    
    # 4. Support
    support_df = generate_support(users_df, subs_df)
    
    # Save
    out_path = lambda x: os.path.join(OUTPUT_DIR, x)
    
    print("Saving files...")
    users_df.to_csv(out_path("users.csv"), index=False)
    subs_df.to_csv(out_path("subscriptions.csv"), index=False)
    events_df.to_csv(out_path("events.csv"), index=False)
    support_df.to_csv(out_path("support_nps.csv"), index=False)
    
    # Also Parquet
    users_df.to_parquet(out_path("users.parquet"), index=False)
    subs_df.to_parquet(out_path("subscriptions.parquet"), index=False)
    events_df.to_parquet(out_path("events.parquet"), index=False)
    support_df.to_parquet(out_path("support_nps.parquet"), index=False)
    
    # Log
    with open(out_path("generation_log.txt"), "w") as f:
        f.write(f"Generated on {datetime.now()}\n")
        f.write(f"Users: {len(users_df)}\n")
        f.write(f"Events: {len(events_df)}\n")
        f.write(f"Subscriptions: {len(subs_df)}\n")
        f.write(f"Support Tickets: {len(support_df)}\n")

if __name__ == "__main__":
    main()
