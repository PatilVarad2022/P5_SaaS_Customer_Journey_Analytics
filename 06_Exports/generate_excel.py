
import pandas as pd
import os

INPUT_DIR = "../04_Derived_Tables"
OUTPUT_FILE = "clv_inputs.xlsx"

def generate_excel():
    print("Generating CLV Inputs Excel...")
    
    # Load data
    mrr_df = pd.read_csv(os.path.join(INPUT_DIR, "monthly_revenue_v1.1.csv"))
    cohort_df = pd.read_csv(os.path.join(INPUT_DIR, "cohort_retention_v1.1.csv"))
    
    with pd.ExcelWriter(OUTPUT_FILE, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # 1. Inputs Sheet
        inputs_data = {
            'Parameter': ['Gross Margin', 'Discount Rate', 'Price Basic', 'Price Pro', 'Monthly Churn Basic', 'Monthly Churn Pro', 'CAC Target'],
            'Value': [0.85, 0.10, 29.0, 99.0, 0.05, 0.02, 150.0],
            'Key': ['gross_margin', 'discount_rate', 'price_basic', 'price_pro', 'monthly_churn_basic', 'monthly_churn_pro', 'cac_target'],
            'Description': ['Margin after COGS', 'Annual WACC', 'Monthly Basic Price', 'Monthly Pro Price', 'Est. Monthly Churn', 'Est. Monthly Churn', 'Target Cost per Acq']
        }
        pd.DataFrame(inputs_data).to_excel(writer, sheet_name='Inputs', index=False)
        
        # 2. Monthly Data
        mrr_df.to_excel(writer, sheet_name='Monthly_Data', index=False)
        
        # 3. User Summary
        retention_curve = cohort_df.groupby('month_offset')['retention_rate'].mean().reset_index()
        retention_curve.columns = ['Month_Offset', 'Avg_Retention']
        retention_curve.to_excel(writer, sheet_name='User_Summary', index=False)
        
        # 4. README Sheet
        readme_txt = pd.DataFrame([["This file contains inputs for the CLV model."], 
                                   ["Do not rename sheets."], 
                                   ["Named Ranges defined: gross_margin, discount_rate, price_basic, price_pro, etc."]])
        readme_txt.to_excel(writer, sheet_name='README', index=False, header=False)


        # Define Names (Absolute references to Inputs sheet)
        # Assuming table starts at A1, Value is Col B (buffer), Key is Col C, but Data is:
        # A: Parameter, B: Value, C: Key, D: Desc.
        # So Value B2 is first row.
        
        # Map keys to rows (0-indexed in list -> 1-indexed in Excel + header row = +2)
        key_map = {k: i+2 for i, k in enumerate(inputs_data['Key'])}
        
        for key, row_idx in key_map.items():
            workbook.define_name(key, f'=Inputs!$B${row_idx}')

    
    print(f"Saved {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_excel()
