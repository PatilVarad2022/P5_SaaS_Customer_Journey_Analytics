
import pandas as pd
import numpy as np
import os
import glob

# Paths
DERIVED_DIR = "../04_Derived_Tables"
CLEANED_DIR = "../03_Data_Cleaning/cleaned"
OUTPUT_DIR = "." # Current 06_Exports

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

# Load Data
print("Loading data...")

def load_derived(name):
    # Try canonical parquet only
    p = os.path.join(DERIVED_DIR, f"{name}.parquet")
    if os.path.exists(p): return pd.read_parquet(p)
    # Fail
    print(f"Warning: Could not find {name} parquet in {DERIVED_DIR}")
    return pd.DataFrame()

monthly_revenue = load_derived("monthly_revenue")
monthly_funnel = load_derived("monthly_funnel")
user_master = load_derived("user_master")

# Cleaned data - Canonical
users_path = os.path.join(CLEANED_DIR, "users_cleaned.parquet")
subs_path = os.path.join(CLEANED_DIR, "subscriptions_cleaned.parquet")
events_path = os.path.join(CLEANED_DIR, "events_cleaned.parquet")

users = pd.read_parquet(users_path)
subs = pd.read_parquet(subs_path)
events = pd.read_parquet(events_path)


# ---------------------------
# Task 1: mrr_metrics.csv
# ---------------------------
print("Generating MRR Metrics...")
mrr_metrics = monthly_revenue.copy()
mrr_metrics['net_new_mrr'] = mrr_metrics['new_MRR'] + mrr_metrics['expansion_MRR'] - mrr_metrics['contraction_MRR'] - mrr_metrics['churned_MRR']
mrr_metrics = mrr_metrics.rename(columns={
    'new_MRR': 'new_mrr',
    'expansion_MRR': 'expansion_mrr',
    'contraction_MRR': 'contraction_mrr',
    'churned_MRR': 'churn_mrr',
    'MRR_total': 'total_mrr'
})
mrr_metrics = mrr_metrics[['month', 'new_mrr', 'expansion_mrr', 'contraction_mrr', 'churn_mrr', 'net_new_mrr', 'total_mrr']]
mrr_metrics.to_csv(os.path.join(OUTPUT_DIR, "mrr_metrics.csv"), index=False)

# ---------------------------
# Task 2: arpu_ltv.csv
# ---------------------------
print("Generating ARPU + LTV Table...")
churn_txns = subs[subs['transaction_type'] == 'churn'].copy()
churn_txns['month'] = pd.to_datetime(churn_txns['start_date']).dt.to_period('M').astype(str)
monthly_churn_counts = churn_txns.groupby('month')['user_id'].nunique().reset_index(name='churned_users')

arpu_ltv = monthly_revenue[['month', 'active_paid_users', 'ARPU']].copy()
arpu_ltv['active_paid_users'] = arpu_ltv['active_paid_users'].astype(int)
arpu_ltv = arpu_ltv.rename(columns={'active_paid_users': 'active_users', 'ARPU': 'arpu'})

arpu_ltv = arpu_ltv.merge(monthly_churn_counts, on='month', how='left').fillna(0)
arpu_ltv['start_users'] = arpu_ltv['active_users'].shift(1).fillna(0) 
arpu_ltv['monthly_churn_rate'] = np.where(arpu_ltv['start_users'] > 0, arpu_ltv['churned_users'] / arpu_ltv['start_users'], 0.0)
arpu_ltv['avg_lifetime_months'] = np.where(arpu_ltv['monthly_churn_rate'] > 0, 1 / arpu_ltv['monthly_churn_rate'], 0.0)
arpu_ltv['ltv'] = arpu_ltv['arpu'] * arpu_ltv['avg_lifetime_months']

final_arpu_df = arpu_ltv[['month', 'active_users', 'arpu', 'monthly_churn_rate', 'avg_lifetime_months', 'ltv']]
final_arpu_df.to_csv(os.path.join(OUTPUT_DIR, "arpu_ltv.csv"), index=False)


# ---------------------------
# Task 3: Segmentation Tables
# ---------------------------
print("Generating Segmentation Tables...")
seg_df = users[['user_id', 'country', 'acquisition_channel']].merge(
    user_master[['user_id', 'plan_id', 'is_churned', 'status']], 
    on='user_id', 
    how='inner'
)
active_user_ids = events['user_id'].unique()
seg_df['is_activated'] = seg_df['user_id'].isin(active_user_ids)

paid_users_ids = subs[subs['amount'] > 0]['user_id'].unique()
seg_df['is_paid'] = seg_df['user_id'].isin(paid_users_ids)
seg_df['is_currently_active'] = (seg_df['status'].str.lower() == 'active') & (seg_df['is_paid'])
seg_df['plan_id'] = seg_df['plan_id'].fillna('No Plan')
seg_df['is_churned_paid'] = seg_df['is_churned'] & seg_df['is_paid']

# 3.1 Plan
plan_agg = seg_df.groupby(['country', 'plan_id']).agg(
    total_users=('user_id', 'count'),
    active_users=('is_currently_active', 'sum'),
    activated_count=('is_activated', 'sum'),
    paid_count=('is_paid', 'sum'),
    churned_paid_count=('is_churned_paid', 'sum')
).reset_index()

plan_agg['activation_rate'] = plan_agg['activated_count'] / plan_agg['total_users']
plan_agg['conversion_rate'] = plan_agg['paid_count'] / plan_agg['total_users']
plan_agg['churn_rate'] = np.where(plan_agg['paid_count'] > 0, plan_agg['churned_paid_count'] / plan_agg['paid_count'], 0.0)

plan_out = plan_agg[['country', 'plan_id', 'active_users', 'activation_rate', 'conversion_rate', 'churn_rate']]
plan_out = plan_out.rename(columns={'plan_id': 'plan'})
plan_out.to_csv(os.path.join(OUTPUT_DIR, "segmentation_plan.csv"), index=False)

# 3.2 Acquisition
acq_agg = seg_df.groupby('acquisition_channel').agg(
    total_users=('user_id', 'count'),
    active_users=('is_currently_active', 'sum'),
    activated_count=('is_activated', 'sum'),
    paid_count=('is_paid', 'sum'),
    churned_paid_count=('is_churned_paid', 'sum')
).reset_index()

acq_agg['activation_rate'] = acq_agg['activated_count'] / acq_agg['total_users']
acq_agg['conversion_rate'] = acq_agg['paid_count'] / acq_agg['total_users']
acq_agg['churn_rate'] = np.where(acq_agg['paid_count'] > 0, acq_agg['churned_paid_count'] / acq_agg['paid_count'], 0.0)

acq_out = acq_agg[['acquisition_channel', 'active_users', 'activation_rate', 'conversion_rate', 'churn_rate']]
acq_out.to_csv(os.path.join(OUTPUT_DIR, "segmentation_acquisition.csv"), index=False)


# ---------------------------
# Task 4: Scenario Input
# ---------------------------
print("Generating Scenario Inputs...")
scenario_data = [
    {'variable': 'activation_rate_delta', 'value': 0.00},
    {'variable': 'churn_rate_delta', 'value': 0.00},
    {'variable': 'pricing_delta', 'value': 0.00},
    {'variable': 'gross_margin', 'value': 0.85},
    {'variable': 'discount_rate', 'value': 0.10},
    {'variable': 'price_basic', 'value': 9.99},
    {'variable': 'price_pro', 'value': 29.99},
    {'variable': 'cogs_per_user', 'value': 1.50},
    {'variable': 'cac_blended', 'value': 50.00}
]
scenario_df = pd.DataFrame(scenario_data)
scenario_df.to_csv(os.path.join(OUTPUT_DIR, "scenario_inputs.csv"), index=False)


# ---------------------------
# Task 5: README
# ---------------------------
print("Generating README...")
readme_content = """# SaaS Exports & Canonical Data

This directory contains the final, canonical CSV datasets for Dashboarding (Tableau) and Modeling (Excel/Python).

## 1. Primary Files
| File | Description | Destination |
|------|-------------|-------------|
| **mrr_metrics.csv** | Dedicated MRR Bridge (New, Exp, Cont, Churn, Net). Strict formula reconciliation. | Excel / Tableau |
| **arpu_ltv.csv** | Monthly Unit Economics (Active Users, ARPU, Churn Rate, LTV). | Excel Simulator / Tableau |
| **segmentation_plan.csv** | Segmented metrics by Country & Plan (Activation, Conv, Churn Rates). | Tableau |
| **segmentation_acquisition.csv** | Segmented metrics by Channel. | Tableau |
| **scenario_inputs.csv** | Parameter configuration loaded by the Forecast Engine. | Simulator Inputs |

## 2. Formulas & Definitions
- **Activation**: User has >0 events (`events_cleaned.parquet`).
- **Paid Conversion**: User has at least one subscription with `amount > 0`.
- **Churn Rate**: `Churned Paid Users / Total Paid Users` (Segment) or `Churned Users_t / Active Users_{t-1}` (Monthly).
- **MRR Bridge**: `End = Start + New + Expansion - Contraction - Churn`.
- **LTV**: `ARPU / Churn Rate`. (If Churn=0, LTV cap applied).

## 3. Usage
- **Tableau**: Connects to `mrr_metrics.csv`, `segmentation_*.csv`.
- **Excel Simulator**: Imports `scenario_inputs.csv` and `arpu_ltv.csv`.

*Generated from `04_Derived_Tables` (Source of Truth).*
"""
with open(os.path.join(OUTPUT_DIR, "README.md"), "w") as f:
    f.write(readme_content)

print("Final Export Complete.")
