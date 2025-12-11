
import pandas as pd
import os
import shutil
import hashlib
from datetime import datetime

DERIVED_DIR = "../04_Derived_Tables"
EXPORT_DIR = "tableau_ready"
MANIFEST_FILE = "export_manifest.csv"
VERSION = "v1.1"

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def get_md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def export():
    print("Exporting for Tableau...")
    ensure_dir(EXPORT_DIR)
    
    # Mapping Source -> Dest Name
    # Source has version suffix, Dest is clean
    files_map = {
        f"user_master_{VERSION}.parquet": "user_master.parquet",
        f"monthly_revenue_{VERSION}.parquet": "monthly_revenue.parquet",
        f"monthly_funnel_{VERSION}.parquet": "monthly_funnel.parquet",
        f"cohort_retention_{VERSION}.parquet": "cohort_retention.parquet",
        f"support_summary_{VERSION}.parquet": "support_summary.parquet",
        f"user_event_summary_{VERSION}.parquet": "user_event_summary.parquet",
        f"churn_flags_{VERSION}.parquet": "churn_flags.parquet"
    }
    
    manifest_rows = []
    
    for src_name, dst_name in files_map.items():
        src_path = os.path.join(DERIVED_DIR, src_name)
        dst_path = os.path.join(EXPORT_DIR, dst_name)
        
        if os.path.exists(src_path):
            shutil.copy2(src_path, dst_path)
            
            # Metadata
            md5_val = get_md5(dst_path)
            rows = len(pd.read_parquet(dst_path))
            
            manifest_rows.append({
                'file_name': dst_name,
                'creation_timestamp': datetime.now().isoformat(),
                'row_count': rows,
                'md5_checksum': md5_val,
                'schema_version': VERSION
            })
        else:
            print(f"Warning: Source {src_path} not found.")
            
    # Save manifest
    pd.DataFrame(manifest_rows).to_csv(MANIFEST_FILE, index=False)
    print("Export complete.")

if __name__ == "__main__":
    export()
