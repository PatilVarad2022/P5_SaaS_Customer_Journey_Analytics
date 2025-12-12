import pytest
import pandas as pd
from src.utils.config import USERS_FILE, EVENTS_FILE, SUBSCRIPTIONS_FILE, REVENUE_FILE

def test_keys_unique():
    users = pd.read_csv(USERS_FILE)
    assert users["customer_id"].is_unique, "Customer IDs should be unique in users.csv"
