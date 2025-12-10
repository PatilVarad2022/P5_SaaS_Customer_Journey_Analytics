
import pandas as pd
import os

INPUT_DIR = "../04_Derived_Tables"
OUTPUT_FILE = "clv_inputs.xlsx"

def generate_excel():
    print("Generating CLV Inputs Excel...")
    
    # Load data
    mrr_df = pd.read_csv(os.path.join(INPUT_DIR, "monthly_revenue.csv"))
    cohort_df = pd.read_csv(os.path.join(INPUT_DIR, "cohort_retention.csv"))
    
    with pd.ExcelWriter(OUTPUT_FILE, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # 1. Inputs Sheet
        inputs_data = {
            'Parameter': ['Gross Margin', 'Discount Rate', 'Basic Price', 'Pro Price', 'CAC Target'],
            'Value': [0.85, 0.10, 29.0, 99.0, 150.0],
            'Description': ['Margin after COGS', 'Annual WACC', 'Monthly Basic', 'Monthly Pro', 'Target Cost per Acq']
        }
        pd.DataFrame(inputs_data).to_excel(writer, sheet_name='Inputs', index=False)
        
        # Named Ranges handled by Pandas? No, need workbook.define_name
        # But XlsxWriter makes it easy.
        
        # 2. Monthly Data
        mrr_df.to_excel(writer, sheet_name='Monthly_Data', index=False)
        
        # 3. User Summary (Aggregation for Excel modeling)
        # Summarize retention curve (avg retention per offset)
        retention_curve = cohort_df.groupby('month_offset')['retention_rate'].mean().reset_index()
        retention_curve.columns = ['Month_Offset', 'Avg_Retention']
        retention_curve.to_excel(writer, sheet_name='User_Summary', index=False)
        
        # Define Names
        # Inputs
        workbook.define_name('Gross_Margin', '=Inputs!$B$2')
        workbook.define_name('Discount_Rate', '=Inputs!$B$3')
        
        # Tables
        # Just whole sheets for now or specific columns
    
    print(f"Saved {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_excel()
