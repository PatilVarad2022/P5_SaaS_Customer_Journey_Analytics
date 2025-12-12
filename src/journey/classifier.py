import pandas as pd
import numpy as np
from typing import Dict
from src.utils.logger import get_logger
from src.utils.config import ACTIVATION_WINDOW_DAYS

logger = get_logger(__name__)

def classify_journey_stages(users: pd.DataFrame, events: pd.DataFrame, subs: pd.DataFrame) -> pd.DataFrame:
    """
    Classifies each user into a Journey Stage:
    - New: Signup < 14 days, no activation
    - Onboarding: Signup < 30 days, activated
    - Active: Active subscription or recent activity
    - Churned: Cancelled subscription or no activity > 30 days
    """
    logger.info("Classifying journey stages...")
    
    # Create master DF
    journey = users[["customer_id", "signup_date"]].copy()
    today = pd.Timestamp.now().normalize()
    
    # 1. Activation Status
    act_events = events[events["event_name"].str.lower() == "activate"]
    activated_ids = set(act_events["customer_id"])
    journey["is_activated"] = journey["customer_id"].apply(lambda x: x in activated_ids)
    
    # 2. Subscription Status
    active_sub_ids = set(subs[subs["status"] == "active"]["customer_id"])
    journey["has_active_sub"] = journey["customer_id"].apply(lambda x: x in active_sub_ids)
    
    # 3. Last Activity
    last_active = events.groupby("customer_id")["event_timestamp"].max().reset_index()
    last_active.rename(columns={"event_timestamp": "last_seen"}, inplace=True)
    journey = journey.merge(last_active, on="customer_id", how="left")
    
    journey["days_since_signup"] = (today - journey["signup_date"]).dt.days
    journey["days_since_last_seen"] = (today - journey["last_seen"]).dt.days.fillna(9999)

    # Classification Logic
    def classify(row):
        if row["has_active_sub"]:
            return "Retained" # Paying customer
        if row["is_activated"]:
            if row["days_since_last_seen"] <= 30:
                return "Engagement"
            else:
                return "Dormant"
        if row["days_since_signup"] <= 14:
            return "Acquisition" # New
        return "Churned" # Not activated, old enough, or no sub

    journey["stage"] = journey.apply(classify, axis=1)
    
    logger.info(f"Stages classified: {journey['stage'].value_counts().to_dict()}")
    return journey
