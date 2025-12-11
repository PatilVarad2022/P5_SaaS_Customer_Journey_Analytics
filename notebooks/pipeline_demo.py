# pipeline_demo.py
"""
Run this script to see the end-to-end pipeline in action!
"""
import pandas as pd
import os
import sys

# Ensure we are in root
if not os.path.exists("scripts/compute_metrics.py"):
    print("Please run this from the project root.")
    sys.exit(1)

print("=== P5 SaaS Analytics Pipeline Demo ===")

print("\n1. Running Metrics Computation...")
os.system(f"{sys.executable} scripts/compute_metrics.py")

print("\n2. Inspecting Outputs...")

files = ["outputs/kpi_summary.csv", "outputs/mrre_breakdown.csv", "outputs/cohort_retention_matrix.csv"]

for f in files:
    if os.path.exists(f):
        print(f"\n--- {f} ---")
        df = pd.read_csv(f)
        print(df.head())
    else:
        print(f"\nMISSING: {f}")

print("\n=== Demo Complete ===")
