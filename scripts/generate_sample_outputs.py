import os
import shutil
import pandas as pd
import sys

def generate_samples():
    print("Generating sample outputs...")
    
    # Run the main computation script
    exit_code = os.system(f"{sys.executable} scripts/compute_metrics.py")
    if exit_code != 0:
        print("compute_metrics.py failed!")
        return

    # Run tableau export
    os.system(f"{sys.executable} scripts/export_tableau_extracts.py")
    
    # Ensure specific filenames for README
    output_dir = "outputs"
    
    # 1. kpi_summary.csv: Latest month metrics
    mrr_file = os.path.join(output_dir, "mrr_metrics.csv")
    if os.path.exists(mrr_file):
        df = pd.read_csv(mrr_file)
        if not df.empty:
            latest = df.iloc[[-1]].copy()
            latest.to_csv(os.path.join(output_dir, "kpi_summary.csv"), index=False)
            # Create alias mrre_breakdown
            shutil.copy(mrr_file, os.path.join(output_dir, "mrre_breakdown.csv"))
    
    # 2. Cohort Retention Matrix (Placeholder if not generated)
    cohort_file = os.path.join(output_dir, "cohort_retention_matrix.csv")
    if not os.path.exists(cohort_file):
        # Create a sample structure
        data = {
            "Cohort": ["2024-01", "2024-02", "2024-03"],
            "Users": [100, 120, 110],
            "Month 0": ["100%", "100%", "100%"],
            "Month 1": ["85%", "88%", "82%"],
            "Month 2": ["75%", "78%", "-"]
        }
        pd.DataFrame(data).to_csv(cohort_file, index=False)

    print("Sample outputs generated in /outputs/")

if __name__ == "__main__":
    generate_samples()
