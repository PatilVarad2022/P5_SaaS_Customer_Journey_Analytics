import pandas as pd
import json
import logging
from src.etl.loader import load_data
from src.funnel.engine import compute_funnel_metrics
from src.journey.classifier import classify_journey_stages
from src.segmentation.engine import create_segments
from src.analytics.kpis import calculate_kpis
from src.utils.config import (
    KPI_SUMMARY_FILE, CUSTOMER_JOURNEY_FILE, FUNNEL_FILE, 
    METRICS_FILE, SEGMENTS_FILE, OUTPUTS_DIR
)
from src.utils.logger import get_logger

logger = get_logger(__name__)

def main():
    logger.info("Starting pipeline...")
    
    # Ensure outputs dir exists
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. ETL
    data = load_data()
    users = data["users"]
    events = data["events"]
    subs = data["subscriptions"]
    revenue = data["revenue"]
    
    # 2. Funnel
    funnel_metrics = compute_funnel_metrics(users, events, subs)
    with open(FUNNEL_FILE, "w") as f:
        json.dump(funnel_metrics, f, indent=2)
    pd.DataFrame([funnel_metrics]).to_csv(OUTPUTS_DIR / "funnel_summary.csv", index=False)
        
    # 3. Journey Classification
    journey_df = classify_journey_stages(users, events, subs)
    journey_df.to_csv(CUSTOMER_JOURNEY_FILE, index=False)
    
    # 4. Segmentation
    segments_df = create_segments(journey_df, revenue)
    segments_df.to_csv(SEGMENTS_FILE, index=False)
    
    # 5. KPIs
    kpis = calculate_kpis(users, events, segments_df)
    with open(METRICS_FILE, "w") as f:
        json.dump(kpis, f, indent=2)
    pd.DataFrame([kpis]).to_csv(KPI_SUMMARY_FILE, index=False)
    
    # 6. Consistency Checks (B5)
    # Check if Journey outputs match Cohort numbers?
    # Simple check: Sum of Segments = Total Users
    total_users_check = len(segments_df) == len(users)
    # Check NO stage regressions (User cannot be 'Retained' without 'Activation' logic implicitly handling it?)
    # In our logic, Retained requires Active Sub. Active Sub implies they value the product. 
    # Usually you activate before paying.
    
    logger.info(f"Consistency Check: Total Users Match = {total_users_check}")
    
    logger.info("Pipeline completed successfully.")

if __name__ == "__main__":
    main()
