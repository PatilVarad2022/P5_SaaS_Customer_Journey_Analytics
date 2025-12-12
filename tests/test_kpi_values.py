"""
Test KPI values for sanity and valid ranges.
Ensures computed metrics fall within expected bounds.
"""
import pandas as pd
import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KPI_FILE = ROOT / "outputs" / "kpi_summary.csv"


def test_kpi_file_exists():
    """Ensure KPI summary file exists."""
    assert KPI_FILE.exists(), f"KPI file not found at {KPI_FILE}"


def test_kpi_ranges():
    """Test that KPI values are within valid ranges."""
    k = pd.read_csv(KPI_FILE).iloc[0]
    
    # Activation rate should be between 0 and 1
    assert 0 <= float(k["activation_rate"]) <= 1, \
        f"activation_rate {k['activation_rate']} out of range [0,1]"
    
    # Churn rate should be between 0 and 1
    assert 0 <= float(k["churn_rate"]) <= 1, \
        f"churn_rate {k['churn_rate']} out of range [0,1]"
    
    # MRR should be non-negative
    assert float(k["total_mrr"]) >= 0, \
        f"total_mrr {k['total_mrr']} should be non-negative"
    
    # ARR should be non-negative
    assert float(k["total_arr"]) >= 0, \
        f"total_arr {k['total_arr']} should be non-negative"
    
    # ARR should equal MRR * 12
    assert abs(float(k["total_arr"]) - float(k["total_mrr"]) * 12) < 0.01, \
        f"total_arr {k['total_arr']} should equal total_mrr * 12"
    
    # ARPU should be non-negative
    assert float(k["avg_revenue_per_user"]) >= 0, \
        f"avg_revenue_per_user {k['avg_revenue_per_user']} should be non-negative"


def test_kpi_retention_metrics():
    """Test revenue retention metrics if available."""
    k = pd.read_csv(KPI_FILE).iloc[0]
    
    
    # If NRR is available
    if "net_revenue_retention" in k and pd.notna(k["net_revenue_retention"]):
        assert float(k["net_revenue_retention"]) >= 0, \
            f"net_revenue_retention {k['net_revenue_retention']} should be non-negative"
    
    # If GRR is available
    if "gross_revenue_retention" in k and pd.notna(k["gross_revenue_retention"]):
        assert 0 <= float(k["gross_revenue_retention"]) <= 1, \
            f"gross_revenue_retention {k['gross_revenue_retention']} out of range [0,1]"


def test_kpi_ltv_metrics():
    """Test LTV and customer lifetime metrics if available."""
    k = pd.read_csv(KPI_FILE).iloc[0]
    
    # If LTV is available, it should be positive
    if pd.notna(k["avg_ltv"]):
        assert float(k["avg_ltv"]) > 0, \
            f"avg_ltv {k['avg_ltv']} should be positive"
    
    # If customer lifetime months is available
    if "customer_lifetime_months" in k and pd.notna(k["customer_lifetime_months"]):
        assert float(k["customer_lifetime_months"]) > 0, \
            f"customer_lifetime_months {k['customer_lifetime_months']} should be positive"


def test_kpi_cac_metrics():
    """Test CAC and payback period if available."""
    k = pd.read_csv(KPI_FILE).iloc[0]
    
    # If CAC is available
    if "customer_acquisition_cost" in k and pd.notna(k["customer_acquisition_cost"]):
        assert float(k["customer_acquisition_cost"]) >= 0, \
            f"customer_acquisition_cost {k['customer_acquisition_cost']} should be non-negative"
    
    # If payback period is available
    if "payback_period_months" in k and pd.notna(k["payback_period_months"]):
        assert float(k["payback_period_months"]) > 0, \
            f"payback_period_months {k['payback_period_months']} should be positive"


def test_kpi_user_counts():
    """Test user count metrics."""
    k = pd.read_csv(KPI_FILE).iloc[0]
    
    # All user counts should be non-negative integers
    assert int(k["active_users"]) >= 0, "active_users should be non-negative"
    assert int(k["active_last_30_days"]) >= 0, "active_last_30_days should be non-negative"
    assert int(k["signup_count"]) >= 0, "signup_count should be non-negative"
    assert int(k["activation_count"]) >= 0, "activation_count should be non-negative"
    assert int(k["churn_count"]) >= 0, "churn_count should be non-negative"
    
    # Activation count should not exceed signup count
    assert int(k["activation_count"]) <= int(k["signup_count"]), \
        "activation_count should not exceed signup_count"
