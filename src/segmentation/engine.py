import pandas as pd
from typing import Dict
from src.utils.logger import get_logger

logger = get_logger(__name__)

def create_segments(journey_df: pd.DataFrame, revenue_df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates segments:
    - Lifecycle: New, Active, At-Risk, Churned (mapped from stages)
    - Revenue: Free, Low-Tier, High-Tier
    """
    logger.info("Creating segments...")
    
    df = journey_df.copy()
    
    # Lifecycle Segment
    # Mapping our Stages to the requested segments
    # Requested: New, Active, At-Risk, Churned
    def map_lifecycle(stage):
        if stage == "Acquisition": return "New"
        if stage in ["Retained", "Engagement"]: return "Active"
        if stage == "Dormant": return "At-Risk"
        return "Churned"
    
    df["lifecycle_segment"] = df["stage"].apply(map_lifecycle)
    
    # Revenue Segment
    # Calc total Lifetime Revenue
    ltv = revenue_df.groupby("customer_id")["amount"].sum().reset_index()
    df = df.merge(ltv, on="customer_id", how="left")
    df["amount"] = df["amount"].fillna(0)
    
    def map_revenue(amount):
        if amount == 0: return "Free"
        if amount < 500: return "Low-Tier"
        return "High-Tier"
        
    df["revenue_segment"] = df["amount"].apply(map_revenue)
    
    return df
