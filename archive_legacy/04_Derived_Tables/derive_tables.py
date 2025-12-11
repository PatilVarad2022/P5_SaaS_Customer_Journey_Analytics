
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

INPUT_DIR = "../03_Data_Cleaning/cleaned"
OUTPUT_DIR = "." # Current dir

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def derive_tables():
    print("Loading data...")
    try:
        # Canonical inputs
        users = pd.read_parquet(os.path.join(INPUT_DIR, "users_cleaned.parquet"))
        subs = pd.read_parquet(os.path.join(INPUT_DIR, "subscriptions_cleaned.parquet"))
        events = pd.read_parquet(os.path.join(INPUT_DIR, "events_cleaned.parquet"))
        support = pd.read_parquet(os.path.join(INPUT_DIR, "support_nps_cleaned.parquet"))
    except FileNotFoundError:
        print("Canonical input files not found. Please run cleaning script.")
        return
    
    # Pre-process dates
    users['signup_date'] = pd.to_datetime(users['signup_date'])
    subs['start_date'] = pd.to_datetime(subs['start_date'])
    subs['end_date'] = pd.to_datetime(subs['end_date'])
    events['event_timestamp'] = pd.to_datetime(events['event_timestamp'])
    
    # ---------------------------
    # 1. User Master
    # ---------------------------
    print("Building User Master...")
    # Get latest sub status
    latest_sub = subs.sort_values('start_date').drop_duplicates('user_id', keep='last')
    
    # First activation (first event)
    first_event = events.groupby('user_id')['event_timestamp'].min().reset_index()
    first_event.columns = ['user_id', 'first_event_date']
    
    # Merge
    user_master = users.merge(latest_sub[['user_id', 'status', 'plan_id']], on='user_id', how='left', suffixes=('', '_current'))
    user_master = user_master.merge(first_event, on='user_id', how='left')
    
    # Calculate lifetime
    today = pd.Timestamp('2024-12-31')
    
    # Churn Date from subs
    churn_subs = subs[subs['transaction_type'] == 'churn']
    churn_map = churn_subs.groupby('user_id')['start_date'].max() # Approx churn date
    
    user_master['churn_date'] = user_master['user_id'].map(churn_map)
    user_master['is_churned'] = user_master['churn_date'].notnull()
    
    user_master['lifetime_end'] = user_master['churn_date'].fillna(today)
    user_master['lifetime_days'] = (user_master['lifetime_end'] - user_master['signup_date']).dt.days
    
    user_master['cohort_month'] = user_master['signup_date'].dt.to_period('M').astype(str)
    
    # ---------------------------
    # 2. Monthly Revenue (Strict Snapshot Bridge)
    # ---------------------------
    print("Building Revenue Summary (Strict)...")
    months = pd.period_range('2024-01', '2024-12', freq='M')
    revenue_rows = []
    
    # Helper to get active MRR at a specific timestamp
    def get_active_mrr(target_date):
        cond_start = subs['start_date'] <= target_date
        eff_end = subs['end_date'] + pd.Timedelta(days=1)
        cond_end = (eff_end > target_date) | (subs['end_date'].isnull())
        cond_type = subs['transaction_type'] != 'churn'
        cond_amt = subs['amount'] > 0
        mask = cond_start & cond_end & cond_type & cond_amt
        active_subs = subs[mask]
        return active_subs.groupby('user_id')['amount'].sum()

    # Initial state (Month 0 - Dec 2023) -> Assume 0
    previous_mrr_map = pd.Series(dtype=float)
    
    for m in months:
        m_start = m.start_time
        m_end = m.end_time
        
        # Current Active MRR at end of month
        current_mrr_map = get_active_mrr(m_end)
        
        # Calculate Delta per user
        all_users = previous_mrr_map.index.union(current_mrr_map.index)
        prev = previous_mrr_map.reindex(all_users, fill_value=0.0)
        curr = current_mrr_map.reindex(all_users, fill_value=0.0)
        delta = curr - prev
        
        # Classification
        # 1. New: Prev=0, Curr>0
        is_new = (prev == 0) & (curr > 0)
        new_mrr = delta[is_new].sum()
        
        # 2. Churn: Prev>0, Curr=0
        is_churn = (prev > 0) & (curr == 0)
        churned_mrr = -delta[is_churn].sum() # Positive magnitude
        
        # 3. Expansion: Prev>0, Curr>0, Delta>0
        is_exp = (prev > 0) & (curr > 0) & (delta > 0)
        expansion_mrr = delta[is_exp].sum()
        
        # 4. Contraction: Prev>0, Curr>0, Delta<0
        is_cont = (prev > 0) & (curr > 0) & (delta < 0)
        contraction_mrr = -delta[is_cont].sum() # Positive magnitude
        
        total_prev = prev.sum()
        total_curr = curr.sum()
        
        reconciled = total_prev + new_mrr + expansion_mrr - contraction_mrr - churned_mrr
        diff = abs(total_curr - reconciled)
        
        active_users = len(curr[curr > 0])
        arpu = total_curr / active_users if active_users > 0 else 0
        
        revenue_rows.append({
            'month': str(m),
            'MRR_total': total_curr,
            'MRR_start': total_prev,
            'new_MRR': new_mrr,
            'expansion_MRR': expansion_mrr,
            'contraction_MRR': contraction_mrr,
            'churned_MRR': churned_mrr,
            'active_paid_users': active_users,
            'ARPU': arpu,
            'validation_diff': diff
        })
        
        if diff > 1e-9:
            print(f"WARNING: Month {m} mismatch! Diff: {diff}")
            
        previous_mrr_map = current_mrr_map

    rev_df = pd.DataFrame(revenue_rows)

    # ---------------------------
    # 3. Cohort Retention
    # ---------------------------
    print("Building Cohort Analysis...")
    cohort_data = []
    user_cohorts = users[['user_id', 'signup_date']].copy()
    user_cohorts['cohort'] = user_cohorts['signup_date'].dt.to_period('M')
    
    for m in months:
        period_end = m.end_time
        period_start = m.start_time
        active_ids = subs[ (subs['start_date'] <= period_end) & ( (subs['end_date'] >= period_start) | (subs['end_date'].isnull()) ) ]['user_id'].unique()
        
        active_df = pd.DataFrame({'user_id': active_ids})
        merged = active_df.merge(user_cohorts, on='user_id')
        
        counts = merged.groupby('cohort').size().reset_index(name='active_users')
        counts['month'] = m
        cohort_data.append(counts)
        
    cohort_df = pd.concat(cohort_data)
    cohort_df['month_offset'] = (cohort_df['month'].dt.year - cohort_df['cohort'].dt.year) * 12 + (cohort_df['month'].dt.month - cohort_df['cohort'].dt.month)
    cohort_df = cohort_df[cohort_df['month_offset'] >= 0]
    
    cohort_sizes = user_cohorts.groupby('cohort').size().reset_index(name='cohort_size')
    cohort_df = cohort_df.merge(cohort_sizes, on='cohort')
    cohort_df['retention_rate'] = cohort_df['active_users'] / cohort_df['cohort_size']
    
    # ---------------------------
    # 4. Funnel
    # ---------------------------
    print("Building Funnel...")
    funnel_rows = []
    for m in months:
        m_users = users[ users['signup_date'].dt.to_period('M') == m ]
        n_signups = len(m_users)
        
        m_uids = m_users['user_id']
        n_activated = len(first_event[first_event['user_id'].isin(m_uids)])
        
        paid_subs = subs[ (subs['user_id'].isin(m_uids)) & (subs['amount'] > 0) ]
        n_paid = paid_subs['user_id'].nunique()
        
        funnel_rows.append({
            'month': str(m),
            'signups': n_signups,
            'activations': n_activated,
            'paid_conversions': n_paid
        })
    funnel_df = pd.DataFrame(funnel_rows)

    # ---------------------------
    # Saving
    # ---------------------------
    print("Saving derived tables...")
    # Canonical outputs
    save = lambda df, name: (df.to_csv(f"{output_path(name)}.csv", index=False), df.to_parquet(f"{output_path(name)}.parquet", index=False))
    def output_path(name): return os.path.join(OUTPUT_DIR, name)
    
    save(user_master, "user_master")
    save(rev_df, "monthly_revenue")
    save(cohort_df.assign(cohort=lambda x: x['cohort'].astype(str), month=lambda x: x['month'].astype(str)), "cohort_retention")
    save(funnel_df, "monthly_funnel")
    
    # Summary tables
    event_summary = events.groupby('user_id').agg(
        total_events=('event_id', 'count'),
        last_event=('event_timestamp', 'max')
    ).reset_index()
    save(event_summary, "user_event_summary")
    
    support['month'] = pd.to_datetime(support['created_at']).dt.to_period('M').astype(str)
    sup_summary = support.groupby('month').agg(
        tickets_opened=('ticket_id', 'count'),
        avg_nps=('nps_score', 'mean')
    ).reset_index()
    save(sup_summary, "support_summary")
    
    churn_flags = user_master[user_master['is_churned']][['user_id', 'churn_date']].copy()
    churn_flags['churn_flag'] = 1
    save(churn_flags, "churn_flags")
    
    print("Derivation complete.")

if __name__ == "__main__":
    derive_tables()
