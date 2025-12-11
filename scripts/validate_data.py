"""
Basic data validation for P5.
Writes: /outputs/inspections/report.json and /outputs/inspections/summary.txt
Exits non-zero on validation failures.
"""
import json
from pathlib import Path
import pandas as pd
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "outputs" / "inspections"
OUT.mkdir(parents=True, exist_ok=True)

required = {
    "users.csv": ["customer_id", "signup_date", "country", "pricing_plan", "acquisition_channel", "status"],
    "events.csv": ["event_id", "customer_id", "event_name", "event_timestamp"],
    "subscriptions.csv": ["subscription_id", "customer_id", "plan", "start_date", "end_date", "status", "price", "billing_period"],
    "revenue.csv": ["invoice_id", "customer_id", "amount", "revenue_date", "revenue_type"]
}

report = {"checks": [], "status": "ok"}

def check_file(name, cols):
    f = DATA / name
    if not f.exists():
        report["checks"].append({"file": name, "ok": False, "error": "missing"})
        return False
    try:
        df = pd.read_csv(f, nrows=1000)
    except Exception as e:
        report["checks"].append({"file": name, "ok": False, "error": f"read_error:{e}"})
        return False
    missing = [c for c in cols if c not in df.columns]
    if missing:
        report["checks"].append({"file": name, "ok": False, "error": f"missing_columns:{missing}"})
        return False
    # simple type/unique checks
    if "customer_id" in df.columns and df["customer_id"].isnull().any():
        report["checks"].append({"file": name, "ok": False, "error": "null_customer_id"})
        return False
    report["checks"].append({"file": name, "ok": True})
    return True

all_ok = True
for fname, cols in required.items():
    ok = check_file(fname, cols)
    all_ok = all_ok and ok

# date parse quick-checks
import dateutil.parser as dparser
def sample_date_ok(series, n=10):
    for v in series.dropna().head(n):
        try:
            dparser.parse(str(v))
        except Exception:
            return False
    return True

try:
    users = pd.read_csv(DATA / "users.csv")
    if not sample_date_ok(users.get("signup_date", pd.Series())):
        report["checks"].append({"file":"users.csv", "ok":False, "error":"bad_date_format_signup_date"})
        all_ok = False
except Exception:
    pass

report["status"] = "ok" if all_ok else "fail"
with open(OUT / "report.json", "w") as f:
    json.dump(report, f, indent=2)
with open(OUT / "summary.txt", "w") as f:
    f.write("VALIDATION STATUS: " + report["status"] + "\n")
    for c in report["checks"]:
        f.write(json.dumps(c) + "\n")

if not all_ok:
    print("Validation failed. See outputs/inspections/report.json")
    sys.exit(2)
print("Validation passed. See outputs/inspections/report.json")
