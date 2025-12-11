"""
Compute core P5 KPIs and write canonical outputs:
- outputs/kpi_summary.csv (single-row summary per run or per period)
- outputs/cohort_retention_matrix.csv
- outputs/mrr_breakdown.csv
Assumptions: monthly periodization by revenue_date / start_date
"""
import pandas as pd
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)
TABLEAU = OUT / "tableau_ready"
TABLEAU.mkdir(exist_ok=True)

# read
users = pd.read_csv(DATA / "users.csv", parse_dates=["signup_date"])
events = pd.read_csv(DATA / "events.csv", parse_dates=["event_timestamp"])
subs = pd.read_csv(DATA / "subscriptions.csv", parse_dates=["start_date","end_date"], keep_default_na=False)
revenue = pd.read_csv(DATA / "revenue.csv", parse_dates=["revenue_date"])

# 1) Active users (last 30 days)
today = pd.Timestamp.now().normalize()
active_users = users[users["status"]=="active"].shape[0]
active_last_30 = users[users["signup_date"] >= (today - pd.Timedelta(days=30))].shape[0]

# 2) Activation %
# activated within 14 days of signup
act = events[events["event_name"].str.lower()=="activate"]
act = act.merge(users[["customer_id","signup_date"]], on="customer_id", how="left")
act["days_to_activate"] = (act["event_timestamp"].dt.normalize() - act["signup_date"]).dt.days
activated_within_14 = act[act["days_to_activate"].between(0,14)]
activation_pct = len(activated_within_14["customer_id"].unique()) / max(1, users.shape[0])

# 3) Funnel drop-off % (example: signup -> activate -> paid)
# signups
signups = set(users["customer_id"])
activated = set(activated_within_14["customer_id"])
paid = set(subs["customer_id"].unique())
signup_count = len(signups)
activate_count = len(activated)
paid_count = len(paid)
drop_signup_to_activate = 1 - (activate_count / max(1, signup_count))
drop_activate_to_paid = 1 - (paid_count / max(1, activate_count)) if activate_count>0 else np.nan

# 4) Monthly CAC (if you have acquisition cost data; otherwise placeholder)
# Try to read optional marketing_costs.csv if present
import os
cac_value = None
mcost_path = DATA / "marketing_costs.csv"
if mcost_path.exists():
    mc = pd.read_csv(mcost_path, parse_dates=["month"])
    # naive cac = total_cost / customers_acquired_in_month (example)
    # not implemented in depth here
else:
    cac_value = np.nan

# 5) Churn % (MRR-based)
# MRR: sum monthly recurring revenue for current active subscriptions
# Normalize annual to monthly if billing_period == annual
subs_copy = subs.copy()
subs_copy["monthly_price"] = subs_copy.apply(lambda r: r["price"] / 12 if str(r["billing_period"]).lower()=="annual" else r["price"], axis=1)
# compute MRR per month from revenue.csv instead if preferred
mrr_by_customer = subs_copy.groupby("customer_id")["monthly_price"].sum().reset_index()
total_mrr = mrr_by_customer["monthly_price"].sum()

# churn MRR: find subscriptions that ended in the last month
subs_copy["end_date_parsed"] = pd.to_datetime(subs_copy["end_date"], errors="coerce")
last_month_start = (pd.Timestamp.now().normalize() - pd.DateOffset(months=1)).replace(day=1)
last_month_end = (last_month_start + pd.DateOffset(months=1)) - pd.Timedelta(days=1)
churned_last_month = subs_copy[(subs_copy["end_date_parsed"] >= last_month_start) & (subs_copy["end_date_parsed"] <= last_month_end)]
churn_mrr = churned_last_month["monthly_price"].sum()
monthly_churn_pct = churn_mrr / max(1e-9, total_mrr) if total_mrr>0 else np.nan

# 6) Re-activation %
# customers who were cancelled then had a new subscription
# simple approach: count unique customer_id in subs with multiple rows and status toggles
ra_pct = np.nan
if "status" in subs_copy.columns:
    # customers with an end_date and later a new start_date
    t = subs_copy.sort_values(["customer_id","start_date"])
    reactivated_customers = []
    for cid, g in t.groupby("customer_id"):
        if g.shape[0] > 1:
            # if there is more than one subscription record, consider as reactivated
            reactivated_customers.append(cid)
    ra_pct = len(reactivated_customers) / max(1, users.shape[0])

# 7) Monthly LTV (simple: ARPU / monthly_churn)
# ARPU = MRR / active_users
arpu = total_mrr / max(1, active_users)
monthly_ltv = arpu / max(1e-9, monthly_churn_pct) if (monthly_churn_pct and monthly_churn_pct>0) else np.nan

# 8) MRR / ARR
arr = total_mrr * 12

# 9) Compose kpi_summary.csv (single-row)
kpi = {
    "run_date": pd.Timestamp.now().isoformat(),
    "active_users": int(active_users),
    "active_last_30_days": int(active_last_30),
    "signup_count": int(signup_count),
    "activate_count": int(activate_count),
    "paid_count": int(paid_count),
    "activation_pct": float(activation_pct),
    "drop_signup_to_activate": float(drop_signup_to_activate),
    "drop_activate_to_paid": float(drop_activate_to_paid) if not np.isnan(drop_activate_to_paid) else None,
    "total_mrr": float(total_mrr),
    "churn_mrr": float(churn_mrr),
    "monthly_churn_pct": float(monthly_churn_pct) if not np.isnan(monthly_churn_pct) else None,
    "arpu": float(arpu),
    "monthly_ltv": float(monthly_ltv) if not np.isnan(monthly_ltv) else None,
    "arr": float(arr),
    "cac": float(cac_value) if cac_value is not None else None,
    "reactivation_pct": float(ra_pct) if not np.isnan(ra_pct) else None
}

kpi_df = pd.DataFrame([kpi])
kpi_df.to_csv(OUT / "kpi_summary.csv", index=False)

# 10) Cohort retention matrix (monthly cohorts by signup month)
users["signup_month"] = users["signup_date"].dt.to_period("M").dt.to_timestamp()
events["event_month"] = events["event_timestamp"].dt.to_period("M").dt.to_timestamp()
# define activity as any event in a month
activity = events.groupby(["customer_id", "event_month"]).size().reset_index(name="activity")
cohorts = users[["customer_id","signup_month"]].merge(activity, on="customer_id", how="left")
cohorts = cohorts.dropna(subset=["event_month"])
# pivot: index signup_month, columns months_since, values retention %
cohorts["months_since"] = ((cohorts["event_month"].dt.year - cohorts["signup_month"].dt.year) * 12 +
                           (cohorts["event_month"].dt.month - cohorts["signup_month"].dt.month))
cohort_pivot = cohorts.groupby(["signup_month","months_since"])["customer_id"].nunique().reset_index()
cohort_sizes = users.groupby("signup_month")["customer_id"].nunique().reset_index().rename(columns={"customer_id":"cohort_size"})
cohort_pivot = cohort_pivot.merge(cohort_sizes, on="signup_month", how="left")
cohort_pivot["retention_pct"] = cohort_pivot["customer_id"] / cohort_pivot["cohort_size"]
# wide format
retention_wide = cohort_pivot.pivot(index="signup_month", columns="months_since", values="retention_pct").fillna(0)
retention_wide.to_csv(OUT / "cohort_retention_matrix.csv")

# 11) MRR breakdown by type (new / expansion / churn)
# Using revenue.csv: revenue_type flags
if "revenue_type" in revenue.columns:
    rev = revenue.copy()
    rev["month"] = rev["revenue_date"].dt.to_period("M").dt.to_timestamp()
    mrev = rev.groupby(["month","revenue_type"])["amount"].sum().unstack(fill_value=0).reset_index()
    mrev.to_csv(OUT / "mrr_breakdown.csv", index=False)
else:
    # fallback: aggregate subs monthly_price as new/active
    sub_monthly = subs_copy.groupby("plan")["monthly_price"].sum().reset_index()
    sub_monthly.to_csv(OUT / "mrr_breakdown.csv", index=False)

# Export some tableau-ready extracts
kpi_df.to_csv(TABLEAU / "kpi_summary_for_tableau.csv", index=False)
retention_wide.reset_index().to_csv(TABLEAU / "cohort_retention_for_tableau.csv", index=False)

print("Metrics computed. Outputs in /outputs/")
