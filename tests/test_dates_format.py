import pytest
import pandas as pd
from src.utils.config import USERS_FILE, EVENTS_FILE

def test_dates_format():
    users = pd.read_csv(USERS_FILE)
    # Check if signup_date is valid datetime
    try:
        pd.to_datetime(users["signup_date"], format="%Y-%m-%d", errors='raise')
    except Exception:
        pytest.fail("signup_date in users.csv is not in YYYY-MM-DD format")

    events = pd.read_csv(EVENTS_FILE)
    try:
        pd.to_datetime(events["event_timestamp"], errors='raise')
    except Exception:
        pytest.fail("event_timestamp in events.csv is not valid")
