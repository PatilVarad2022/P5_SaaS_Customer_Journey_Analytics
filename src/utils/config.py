from pathlib import Path

# Project Root
ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
OUTPUTS_DIR = ROOT_DIR / "outputs"
SAMPLE_DIR = DATA_DIR / "sample"

# File Paths
USERS_FILE = DATA_DIR / "users.csv"
EVENTS_FILE = DATA_DIR / "events.csv"
SUBSCRIPTIONS_FILE = DATA_DIR / "subscriptions.csv"
REVENUE_FILE = DATA_DIR / "revenue.csv"

# Output Paths
KPI_SUMMARY_FILE = OUTPUTS_DIR / "kpi_summary.csv"
CUSTOMER_JOURNEY_FILE = OUTPUTS_DIR / "customer_journey.csv"
FUNNEL_FILE = OUTPUTS_DIR / "funnel.json"
METRICS_FILE = OUTPUTS_DIR / "metrics.json" # As per checklist C1
SEGMENTS_FILE = OUTPUTS_DIR / "segmentation.csv"
COHORT_MATRIX_FILE = OUTPUTS_DIR / "cohort_retention_matrix.csv"

# Configuration
ACTIVATION_WINDOW_DAYS = 14
RETENTION_WINDOW_DAYS = 30
CHURN_WINDOW_DAYS = 30
