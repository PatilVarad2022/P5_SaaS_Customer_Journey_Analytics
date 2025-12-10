
import pandas as pd
import numpy as np
import os
from datetime import datetime

# Paths
INPUT_DIR = "../02_Data_Generation/outputs"
OUTPUT_DIR = "cleaned"
LOG_FILE = "cleaning_log.csv"
PROFILE_FILE = "data_profile_report.csv"
VERSION = "v1.1"

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

ensure_dir(OUTPUT_DIR)

cleaning_stats = []

def log_stat(table, initial, final, removed, reason):
    cleaning_stats.append({
        'table': table,
        'row_count_before': initial,
        'row_count_after': final,
        'rows_removed': removed,
        'reason_code': reason
    })

def clean_users():
    print("Cleaning users...")
    df = pd.read_csv(os.path.join(INPUT_DIR, "users.csv"))
    initial = len(df)
    
    # 1. Standardize format
    df['email'] = df['user_id'] # No email in schema, using user_id as proxy if needed, but schema didn't ask for email.
    
    # Lowercase categorical
    for col in ['country', 'acquisition_channel', 'initial_plan', 'job_role']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.lower().str.strip()
            
    # Dates
    df['signup_date'] = pd.to_datetime(df['signup_date']).dt.strftime('%Y-%m-%d')
    
    # Deduplicate PK
    df = df.drop_duplicates(subset=['user_id'])
    
    # Constraints? exist checks?
    
    final = len(df)
    log_stat('users', initial, final, initial - final, 'Deduplication')
    
    return df

def clean_subscriptions(users_ids):
    print("Cleaning subscriptions...")
    df = pd.read_csv(os.path.join(INPUT_DIR, "subscriptions.csv"))
    initial = len(df)
    
    # Dates
    for col in ['start_date', 'end_date']:
        df[col] = pd.to_datetime(df[col], errors='coerce')
        
    # FK Check
    valid_mask = df['user_id'].isin(users_ids)
    invalid_count = (~valid_mask).sum()
    if invalid_count > 0:
        df = df[valid_mask]
        
    log_stat('subscriptions', initial, len(df), invalid_count, 'Missing FK user_id')
    
    # Negative MRR
    neg_mask = df['amount'] < 0
    neg_count = neg_mask.sum()
    if neg_count > 0:
        df = df[~neg_mask]
        
    log_stat('subscriptions', len(df)+neg_count, len(df), neg_count, 'Negative MRR')
    
    # Format dates back to string
    df['start_date'] = df['start_date'].dt.strftime('%Y-%m-%d')
    df['end_date'] = df['end_date'].dt.strftime('%Y-%m-%d')
    
    # Lowercase status/type
    for col in ['status', 'transaction_type', 'plan_id']:
        df[col] = df[col].astype(str).str.lower().str.strip()
        
    return df

def clean_events(users_ids):
    print("Cleaning events...")
    df = pd.read_csv(os.path.join(INPUT_DIR, "events.csv"))
    initial = len(df)
    
    # Dates
    df['event_timestamp'] = pd.to_datetime(df['event_timestamp'], errors='coerce')
    
    # Drop invalid dates
    # Filter 2024 only? Schema said 12 month window. Generator produces 2024.
    # Let's enforce range for safety
    mask_date = (df['event_timestamp'] >= '2024-01-01') & (df['event_timestamp'] <= '2025-01-01')
    df = df[mask_date]
    
    # FK Check
    valid_mask = df['user_id'].isin(users_ids)
    df = df[valid_mask]
    
    log_stat('events', initial, len(df), initial - len(df), 'Invalid Date or Missing FK')
    
    # UTC Format
    df['event_timestamp'] = df['event_timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    # Lowercase
    for col in ['event_type', 'device']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.lower().str.strip()
            
    return df

def clean_support(users_ids):
    print("Cleaning support...")
    df = pd.read_csv(os.path.join(INPUT_DIR, "support_nps.csv"))
    initial = len(df)
    
    # Dates
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['resolved_at'] = pd.to_datetime(df['resolved_at'])
    
    # FK
    df = df[df['user_id'].isin(users_ids)]
    
    log_stat('support_nps', initial, len(df), initial - len(df), 'Missing FK')
    
    # Format
    df['created_at'] = df['created_at'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    df['resolved_at'] = df['resolved_at'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    # Lowercase
    df['ticket_category'] = df['ticket_category'].str.lower().str.strip()
    
    return df

def generate_profile(dfs):
    print("Generating profile...")
    profile_rows = []
    
    for name, df in dfs.items():
        for col in df.columns:
            stats = {
                'table': name,
                'column': col,
                'type': str(df[col].dtype),
                'count': len(df),
                'nulls': df[col].isnull().sum(),
                'unique': df[col].nunique(),
                'min_val': df[col].dropna().min() if df[col].dtype != 'object' else '',
                'max_val': df[col].dropna().max() if df[col].dtype != 'object' else ''
            }
            # For objects, just take min/max string for rough idea or skip
            if df[col].dtype == 'object':
                 try:
                     stats['min_val'] = str(df[col].dropna().min())[:20]
                     stats['max_val'] = str(df[col].dropna().max())[:20]
                 except: pass
                 
            profile_rows.append(stats)
            
    return pd.DataFrame(profile_rows)

def main():
    # Load and Clean
    users = clean_users()
    users_ids = set(users['user_id'])
    
    subs = clean_subscriptions(users_ids)
    events = clean_events(users_ids)
    support = clean_support(users_ids)
    
    # Save Cleaned
    users.to_csv(os.path.join(OUTPUT_DIR, f"users_cleaned_{VERSION}.csv"), index=False)
    subs.to_csv(os.path.join(OUTPUT_DIR, f"subscriptions_cleaned_{VERSION}.csv"), index=False)
    events.to_csv(os.path.join(OUTPUT_DIR, f"events_cleaned_{VERSION}.csv"), index=False)
    support.to_csv(os.path.join(OUTPUT_DIR, f"support_nps_cleaned_{VERSION}.csv"), index=False)
    
    # Parquet
    users.to_parquet(os.path.join(OUTPUT_DIR, f"users_cleaned_{VERSION}.parquet"), index=False)
    subs.to_parquet(os.path.join(OUTPUT_DIR, f"subscriptions_cleaned_{VERSION}.parquet"), index=False)
    events.to_parquet(os.path.join(OUTPUT_DIR, f"events_cleaned_{VERSION}.parquet"), index=False)
    support.to_parquet(os.path.join(OUTPUT_DIR, f"support_nps_cleaned_{VERSION}.parquet"), index=False)

    # Save Log
    log_df = pd.DataFrame(cleaning_stats)
    log_df.to_csv(LOG_FILE, index=False)
    
    # Profile
    dfs = {
        'users': users,
        'subscriptions': subs,
        'events': events,
        'support': support
    }
    profile_df = generate_profile(dfs)
    profile_df.to_csv(PROFILE_FILE, index=False)
    
    print("Cleaning complete.")

if __name__ == "__main__":
    main()
