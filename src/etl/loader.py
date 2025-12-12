import pandas as pd
from typing import Dict
from src.utils.config import USERS_FILE, EVENTS_FILE, SUBSCRIPTIONS_FILE, REVENUE_FILE
from src.utils.logger import get_logger

logger = get_logger(__name__)

def load_data() -> Dict[str, pd.DataFrame]:
    """Loads all datasets with proper types."""
    logger.info("Loading datasets...")
    
    try:
        users = pd.read_csv(USERS_FILE, parse_dates=["signup_date"])
        events = pd.read_csv(EVENTS_FILE, parse_dates=["event_timestamp"])
        subs = pd.read_csv(SUBSCRIPTIONS_FILE, parse_dates=["start_date", "end_date"])
        revenue = pd.read_csv(REVENUE_FILE, parse_dates=["revenue_date"])
        
        logger.info(f"Loaded {len(users)} users, {len(events)} events, {len(subs)} subs.")
        return {
            "users": users,
            "events": events,
            "subscriptions": subs,
            "revenue": revenue
        }
    except FileNotFoundError as e:
        logger.error(f"Data file not found: {e}")
        raise
