"""
Orchestrator to run full P5 backend pipeline end-to-end.
Usage: python scripts/run_pipeline.py
Outputs: /outputs/inspections/report.json, /outputs/kpi_summary.csv, /outputs/tableau_ready/*
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

commands = [
    [sys.executable, str(SCRIPTS / "validate_data.py")],
    [sys.executable, str(SCRIPTS / "compute_metrics.py")],
    [sys.executable, str(SCRIPTS / "export_tableau_extracts.py")]
]

def run_cmd(cmd):
    print("RUN:", " ".join(cmd))
    r = subprocess.run(cmd)
    if r.returncode != 0:
        print("ERROR: command failed:", cmd)
        sys.exit(r.returncode)

if __name__ == "__main__":
    for cmd in commands:
        run_cmd(cmd)
    print("Pipeline finished. Check /outputs for artifacts.")
