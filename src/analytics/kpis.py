import pandas as pd
import numpy as np
from typing import Dict
from src.utils.logger import get_logger

logger = get_logger(__name__)

def calculate_kpis(users: pd.DataFrame, events: pd.DataFrame, journey_df: pd.DataFrame, subs: pd.DataFrame) -> Dict[str, float]:
    """
    Calculates Mandatory KPIs:
    - Activation rate
    - Engagement depth (avg events/user)
    - Retention rate (30-day inferred from active status)
    - Churn risk score (avg prob)
    - Avg time between key actions
    """
    logger.info("Calculating KPIs...")
    
    # 1. Activation Rate
    n_users = len(users)
    n_activated = journey_df[journey_df["is_activated"]].shape[0]
    activation_rate = n_activated / n_users if n_users > 0 else 0
    
    # 2. Engagement Depth
    # Avg events per user
    total_events = len(events)
    engagement_depth = total_events / n_users if n_users > 0 else 0
    
    # 3. Retention Rate (30 day)
    # Defined here as % of users > 30 days old who are still "Active" (Retained or Engagement)
    # Strict cohort retention is better, but this is a summary scalar.
    cohort_30_plus = journey_df[journey_df["days_since_signup"] >= 30]
    if len(cohort_30_plus) > 0:
        retained = cohort_30_plus[cohort_30_plus["lifecycle_segment"] == "Active"]
        retention_rate = len(retained) / len(cohort_30_plus)
    else:
        retention_rate = 0.0
        
    # 4. Churn Risk Score
    # Simple rule-based: if At-Risk -> 0.8, Churned -> 1.0, else 0.1
    def risk_score(segment):
        if segment == "Churned": return 1.0
        if segment == "At-Risk": return 0.8
        return 0.1
    
    journey_df["churn_risk"] = journey_df["lifecycle_segment"].apply(risk_score)
    avg_churn_risk = journey_df["churn_risk"].mean()
    
    # 5. Time between actions (e.g., Signup to Activate)
    # We can use the 'activate' events merge
    act_events = events[events["event_name"].str.lower() == "activate"].copy()
    act_events = act_events.merge(users[["customer_id", "signup_date"]], on="customer_id")
    act_events["time_to_activate"] = (act_events["event_timestamp"] - act_events["signup_date"]).dt.total_seconds() / 3600 # hours
    avg_time_to_activate_hours = act_events["time_to_activate"].mean()
    
    # 6. Revenue Metrics (MRR, ARR, LTV)
    # Filter active subscriptions
    if not subs.empty:
        active_subs = subs[subs["status"] == "active"].copy()
        # Normalization (assuming monthly price)
        total_mrr = active_subs["price"].sum()
        total_arr = total_mrr * 12
        
        # ARPU
        avg_revenue_per_user = total_mrr / n_users if n_users > 0 else 0
        
        # Simple LTV = ARPU / Churn Rate (use Churn Risk as proxy or strict churn rate?)
        # Let's use strict churn rate from segments
        churned_users = journey_df[journey_df["lifecycle_segment"] == "Churned"].shape[0]
        churn_rate_strict = churned_users / n_users if n_users > 0 else 0
        
        # Avoid div by zero
        if churn_rate_strict > 0.001:
            avg_ltv = avg_revenue_per_user / churn_rate_strict
        else:
            avg_ltv = 0 # or infinity
            
    else:
        total_mrr = 0.0
        total_arr = 0.0
        avg_revenue_per_user = 0.0
        avg_ltv = 0.0
        churn_rate_strict = 0.0

    return {
        "activation_rate": float(activation_rate),
        "engagement_depth": float(engagement_depth),
        "retention_rate": float(retention_rate),
        "churn_risk_score": float(avg_churn_risk),
        "avg_time_to_activate_hours": float(avg_time_to_activate_hours),
        "total_mrr": float(total_mrr),
        "total_arr": float(total_arr),
        "avg_revenue_per_user": float(avg_revenue_per_user),
        "avg_ltv": float(avg_ltv),
        "churn_rate": float(churn_rate_strict), # for test compatibility
        "active_users": int(journey_df[journey_df["lifecycle_segment"] == "Active"].shape[0]),
        "active_last_30_days": int(journey_df[journey_df["stage"].isin(["Engagement", "Retained"])].shape[0]), # similar to Active
        "signup_count": int(n_users),
        "activation_count": int(n_activated),
        "churn_count": int(churned_users)
    }
