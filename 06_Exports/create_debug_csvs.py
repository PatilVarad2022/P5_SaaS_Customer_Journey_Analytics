
import pandas as pd
import os
import shutil

INPUT_DIR = "tableau_ready"
OUTPUT_DIR = "debug_csvs"

def create_debug():
    print("Generating Debug CSVs...")
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    for fname in os.listdir(INPUT_DIR):
        if fname.endswith(".parquet"):
            src = os.path.join(INPUT_DIR, fname)
            dst_name = fname.replace(".parquet", ".csv")
            dst = os.path.join(OUTPUT_DIR, dst_name)
            
            df = pd.read_parquet(src)
            subset = df.head(1000) # first 10k rows requested (or 1000 is enough for debugging usually)
            # User asked for 10k.
            subset_10k = df.head(10000)
            
            subset_10k.to_csv(dst, index=False)
            print(f"Created {dst} ({len(subset_10k)} rows)")

if __name__ == "__main__":
    create_debug()
