"""
Compute core P5 KPIs and write canonical outputs:
- outputs/kpi_summary.csv (single-row summary per run or per period)
- outputs/cohort_retention_matrix.csv
- outputs/mrr_breakdown.csv
- outputs/funnel_summary.csv

MRR-based churn definition for SaaS CV:
- MRR Start: total MRR at beginning of analysis period
- MRR Churn: MRR lost from cancellations during period
- MRR Expansion: MRR gained from upgrades during period
- Monthly Churn %: mrr_churn / mrr_start
- NRR: (mrr_start + mrr_expansion - mrr_churn) / mrr_start
- GRR: (mrr_start - mrr_churn) / mrr_start
- LTV: ARPU / monthly_churn_pct (if churn > 0)
- CAC: total_marketing_costs / new_customers (if marketing_costs.csv exists)
- Payback Period: CAC / ARPU (if CAC available)
"""
import pandas as pd
from pathlib import Path
import numpy as np
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)
TABLEAU = OUT / "tableau_ready"
TABLEAU.mkdir(exist_ok=True)

# ============================================================================
# READ DATA
# ============================================================================
users = pd.read_csv(DATA / "users.csv", parse_dates=["signup_date"])
events = pd.read_csv(DATA / "events.csv", parse_dates=["event_timestamp"])
subs = pd.read_csv(DATA / "subscriptions.csv", parse_dates=["start_date","end_date"], keep_default_na=False)
revenue = pd.read_csv(DATA / "revenue.csv", parse_dates=["revenue_date"])

# ============================================================================
# 1) BASIC USER METRICS
# ============================================================================
today = pd.Timestamp.now().normalize()
active_users = users[users["status"]=="active"].shape[0]
active_last_30 = users[users["signup_date"] >= (today - pd.Timedelta(days=30))].shape[0]

# ============================================================================
# 2) ACTIVATION RATE (activated within 14 days of signup)
# ============================================================================
act = events[events["event_name"].str.lower()=="activate"]
act = act.merge(users[["customer_id","signup_date"]], on="customer_id", how="left")
act["days_to_activate"] = (act["event_timestamp"].dt.normalize() - act["signup_date"]).dt.days
activated_within_14 = act[act["days_to_activate"].between(0,14)]
activation_rate = len(activated_within_14["customer_id"].unique()) / max(1, users.shape[0])

# ============================================================================
# 3) FUNNEL METRICS (signup -> activate -> paid)
# ============================================================================
signups = set(users["customer_id"])
activated = set(activated_within_14["customer_id"])
paid = set(subs["customer_id"].unique())
signup_count = len(signups)
activation_count = len(activated)
paid_count = len(paid)

# ============================================================================
# 4) MRR CALCULATION
# ============================================================================
# Normalize all subscriptions to monthly price
subs_copy = subs.copy()
subs_copy["monthly_price"] = subs_copy.apply(
    lambda r: r["price"] / 12 if str(r["billing_period"]).lower() == "annual" else r["price"], 
    axis=1
)

# Total MRR = sum of monthly-normalized prices across active subscriptions
active_subs = subs_copy[subs_copy["status"] == "active"]
total_mrr = active_subs["monthly_price"].sum()

# Total ARR = MRR * 12
total_arr = total_mrr * 12

# ARPU = MRR / active_users (guard against division by zero)
arpu = total_mrr / max(1, active_users)

# ============================================================================
# 5) MRR-BASED CHURN CALCULATION
# ============================================================================
# Define analysis period: last complete month
last_month_start = (today - pd.DateOffset(months=1)).replace(day=1)
last_month_end = (last_month_start + pd.DateOffset(months=1)) - pd.Timedelta(days=1)
prev_month_start = (last_month_start - pd.DateOffset(months=1)).replace(day=1)

# MRR at start of month (subscriptions active at beginning of last month)
subs_copy["end_date_parsed"] = pd.to_datetime(subs_copy["end_date"], errors="coerce")
subs_at_month_start = subs_copy[
    (subs_copy["start_date"] < last_month_start) & 
    ((subs_copy["end_date_parsed"].isna()) | (subs_copy["end_date_parsed"] >= last_month_start))
]
mrr_start = subs_at_month_start["monthly_price"].sum()

# MRR churned during the month (subscriptions that ended during last month)
churned_last_month = subs_copy[
    (subs_copy["end_date_parsed"] >= last_month_start) & 
    (subs_copy["end_date_parsed"] <= last_month_end)
]
mrr_churn = churned_last_month["monthly_price"].sum()

# MRR expansion (new subscriptions or upgrades during the month)
# For simplicity, we'll use new subscriptions started during the month
new_subs_last_month = subs_copy[
    (subs_copy["start_date"] >= last_month_start) & 
    (subs_copy["start_date"] <= last_month_end)
]
mrr_expansion = new_subs_last_month["monthly_price"].sum()

# Calculate churn rate (guard against division by zero)
if mrr_start > 1e-6:  # Use small threshold to avoid tiny denominators
    churn_rate = mrr_churn / mrr_start
else:
    churn_rate = 0.0

# ============================================================================
# 6) REVENUE RETENTION METRICS
# ============================================================================
# Net Revenue Retention = (mrr_start + mrr_expansion - mrr_churn) / mrr_start
if mrr_start > 1e-6:
    net_revenue_retention = (mrr_start + mrr_expansion - mrr_churn) / mrr_start
else:
    net_revenue_retention = np.nan

# Gross Revenue Retention = (mrr_start - mrr_churn) / mrr_start
if mrr_start > 1e-6:
    gross_revenue_retention = (mrr_start - mrr_churn) / mrr_start
else:
    gross_revenue_retention = np.nan

# Quick Ratio = (new MRR + expansion MRR) / churned MRR
if mrr_churn > 1e-6:
    quick_ratio = mrr_expansion / mrr_churn
else:
    quick_ratio = np.nan if mrr_expansion == 0 else np.inf

# ============================================================================
# 7) CUSTOMER LIFETIME VALUE (LTV)
# ============================================================================
# Customer Lifetime Months = 1 / monthly_churn_pct (if churn > 0)
if churn_rate > 1e-6:
    customer_lifetime_months = 1.0 / churn_rate
    # Monthly LTV = ARPU / monthly_churn_pct
    avg_ltv = arpu / churn_rate
else:
    # If churn is zero or negligible, set to null (undefined)
    customer_lifetime_months = np.nan
    avg_ltv = np.nan

# ============================================================================
# 8) CUSTOMER ACQUISITION COST (CAC)
# ============================================================================
# Try to read optional marketing_costs.csv if present
mcost_path = DATA / "marketing_costs.csv"
if mcost_path.exists():
    mc = pd.read_csv(mcost_path, parse_dates=["month"])
    # Filter to last month
    mc_last_month = mc[
        (mc["month"] >= last_month_start) & 
        (mc["month"] <= last_month_end)
    ]
    total_marketing_costs = mc_last_month["cost"].sum() if "cost" in mc.columns else 0
    
    # New customers acquired in period
    new_customers_last_month = users[
        (users["signup_date"] >= last_month_start) & 
        (users["signup_date"] <= last_month_end)
    ].shape[0]
    
    # CAC = total_marketing_costs / new_customers_acquired
    if new_customers_last_month > 0:
        customer_acquisition_cost = total_marketing_costs / new_customers_last_month
    else:
        customer_acquisition_cost = np.nan
else:
    customer_acquisition_cost = np.nan

# ============================================================================
# 9) PAYBACK PERIOD
# ============================================================================
# Payback Period = CAC / ARPU (if CAC available and ARPU > 0)
if not np.isnan(customer_acquisition_cost) and arpu > 1e-6:
    payback_period_months = customer_acquisition_cost / arpu
else:
    payback_period_months = np.nan

# ============================================================================
# 10) AVERAGE REVENUE PER USER
# ============================================================================
avg_revenue_per_user = arpu

# ============================================================================
# 11) COMPOSE KPI SUMMARY CSV (single-row)
# ============================================================================
kpi = {
    "run_date": pd.Timestamp.now().isoformat(),
    "active_users": int(active_users),
    "active_last_30_days": int(active_last_30),
    "signup_count": int(signup_count),
    "activation_count": int(activation_count),
    "churn_count": int(len(churned_last_month)),
    "churn_rate": float(churn_rate),
    "activation_rate": float(activation_rate),
    "avg_ltv": float(avg_ltv) if not np.isnan(avg_ltv) else None,
    "total_mrr": float(total_mrr),
    "total_arr": float(total_arr),
    "net_revenue_retention": float(net_revenue_retention) if not np.isnan(net_revenue_retention) else None,
    "gross_revenue_retention": float(gross_revenue_retention) if not np.isnan(gross_revenue_retention) else None,
    "quick_ratio": float(quick_ratio) if not np.isnan(quick_ratio) and not np.isinf(quick_ratio) else None,
    "customer_acquisition_cost": float(customer_acquisition_cost) if not np.isnan(customer_acquisition_cost) else None,
    "avg_revenue_per_user": float(avg_revenue_per_user),
    "customer_lifetime_months": float(customer_lifetime_months) if not np.isnan(customer_lifetime_months) else None,
    "payback_period_months": float(payback_period_months) if not np.isnan(payback_period_months) else None,
}

kpi_df = pd.DataFrame([kpi])
kpi_df.to_csv(OUT / "kpi_summary.csv", index=False)

# ============================================================================
# 12) COHORT RETENTION MATRIX (monthly cohorts by signup month)
# ============================================================================
users["signup_month"] = users["signup_date"].dt.to_period("M").dt.to_timestamp()
events["event_month"] = events["event_timestamp"].dt.to_period("M").dt.to_timestamp()

# Define activity as any event in a month
activity = events.groupby(["customer_id", "event_month"]).size().reset_index(name="activity")
cohorts = users[["customer_id","signup_month"]].merge(activity, on="customer_id", how="left")
cohorts = cohorts.dropna(subset=["event_month"])

# Calculate months since signup
cohorts["months_since"] = (
    (cohorts["event_month"].dt.year - cohorts["signup_month"].dt.year) * 12 +
    (cohorts["event_month"].dt.month - cohorts["signup_month"].dt.month)
)

# Pivot: index signup_month, columns months_since, values retention %
cohort_pivot = cohorts.groupby(["signup_month","months_since"])["customer_id"].nunique().reset_index()
cohort_sizes = users.groupby("signup_month")["customer_id"].nunique().reset_index().rename(columns={"customer_id":"cohort_size"})
cohort_pivot = cohort_pivot.merge(cohort_sizes, on="signup_month", how="left")
cohort_pivot["retention_pct"] = cohort_pivot["customer_id"] / cohort_pivot["cohort_size"]

# Wide format
retention_wide = cohort_pivot.pivot(index="signup_month", columns="months_since", values="retention_pct").fillna(0)
retention_wide.to_csv(OUT / "cohort_retention_matrix.csv")

# ============================================================================
# 13) MRR BREAKDOWN BY TYPE (new / recurring / expansion / churn)
# ============================================================================
if "revenue_type" in revenue.columns:
    rev = revenue.copy()
    rev["month"] = rev["revenue_date"].dt.to_period("M").dt.to_timestamp()
    mrev = rev.groupby(["month","revenue_type"])["amount"].sum().unstack(fill_value=0).reset_index()
    mrev.to_csv(OUT / "mrr_breakdown.csv", index=False)
else:
    # Fallback: aggregate subs monthly_price by plan
    sub_monthly = subs_copy.groupby("plan")["monthly_price"].sum().reset_index()
    sub_monthly.to_csv(OUT / "mrr_breakdown.csv", index=False)

# ============================================================================
# 14) FUNNEL SUMMARY
# ============================================================================
funnel_summary = pd.DataFrame([{
    "stage": "signup",
    "count": signup_count,
    "conversion_rate": 1.0
}, {
    "stage": "activation",
    "count": activation_count,
    "conversion_rate": activation_count / max(1, signup_count)
}, {
    "stage": "paid",
    "count": paid_count,
    "conversion_rate": paid_count / max(1, signup_count)
}])
funnel_summary.to_csv(OUT / "funnel_summary.csv", index=False)

# ============================================================================
# 15) EXPORT TABLEAU-READY EXTRACTS
# ============================================================================
kpi_df.to_csv(TABLEAU / "kpi_summary_for_tableau.csv", index=False)
retention_wide.reset_index().to_csv(TABLEAU / "cohort_retention_for_tableau.csv", index=False)

print("Metrics computed. Outputs in /outputs/")
