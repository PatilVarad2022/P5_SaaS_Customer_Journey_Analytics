import pytest
import pandas as pd
from src.utils.config import USERS_FILE, EVENTS_FILE, SUBSCRIPTIONS_FILE, REVENUE_FILE

def test_files_exist():
    assert USERS_FILE.exists(), "users.csv missing"
    assert EVENTS_FILE.exists(), "events.csv missing"
    assert SUBSCRIPTIONS_FILE.exists(), "subscriptions.csv missing"

def test_schema_columns():
    users = pd.read_csv(USERS_FILE)
    expected_cols = ["customer_id", "signup_date"]
    for col in expected_cols:
        assert col in users.columns, f"users.csv missing {col}"
    
    events = pd.read_csv(EVENTS_FILE)
    assert "event_name" in events.columns
    assert "customer_id" in events.columns
    assert "event_timestamp" in events.columns
