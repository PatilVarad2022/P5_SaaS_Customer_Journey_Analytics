import pandas as pd
import matplotlib.pyplot as plt
import os

# Set style
plt.style.use('ggplot')
OUTPUT_DIR = "docs/screenshots"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def save_table_image(df, title, filename):
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.axis('off')
    ax.axis('tight')
    
    # round numeric
    df_display = df.round(2)
    
    table = ax.table(cellText=df_display.values, colLabels=df_display.columns, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.2)
    
    plt.title(title, pad=20)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved {filename}")

def generate_visuals():
    # 1. KPI Summary (Last 5 months)
    mrr_path = "outputs/mrre_breakdown.csv"
    if os.path.exists(mrr_path):
        df = pd.read_csv(mrr_path)
        # Columns available: month, mrr, active_customers, arpu, mrr_growth
        cols = ["month", "mrr", "active_customers", "arpu", "mrr_growth"]
        # Handle missing cols gracefully if schema changes
        cols = [c for c in cols if c in df.columns]
        
        subset = df[cols].tail(5)
        save_table_image(subset, "Key Performance Indicators (Recent)", "kpi_summary.png")
        
        # Plotting Trends instead of Breakdown (since we lack breakdown columns)
        plt.figure(figsize=(10, 6))
        df['month'] = df['month'].astype(str)
        
        # Dual axis
        fig, ax1 = plt.subplots(figsize=(10,6))
        
        ax1.set_xlabel('Month')
        ax1.set_ylabel('MRR ($)', color='tab:blue')
        ax1.plot(df['month'], df['mrr'], color='tab:blue', marker='o', label='Total MRR')
        ax1.tick_params(axis='y', labelcolor='tab:blue')
        
        ax2 = ax1.twinx()
        ax2.set_ylabel('Active Customers', color='tab:green')
        ax2.plot(df['month'], df['active_customers'], color='tab:green', marker='x', linestyle='--', label='Customers')
        ax2.tick_params(axis='y', labelcolor='tab:green')
        
        plt.title("Growth Metrics: MRR and Customer Count")
        fig.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, "mrr_breakdown.png"), dpi=150) # Keep filename requested by user
        plt.close()
        print("Saved mrr_breakdown.png (Trends)")

    # 2. Cohort Retention Matrix
    cohort_path = "outputs/cohort_retention_matrix.csv"
    if os.path.exists(cohort_path):
        df = pd.read_csv(cohort_path)
        save_table_image(df, "Cohort Retention Matrix", "cohort_matrix.png")

if __name__ == "__main__":
    generate_visuals()
