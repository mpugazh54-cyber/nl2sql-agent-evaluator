    """
Utility to fetch distinct sample values from Fabric SQL Endpoint tables.

Inputs:
    - .env (FABRIC_SQL_ENDPOINT)
Outputs:
    - data/sample/sample_data_billing.txt
    - data/sample/sample_data_booking.txt
"""

import os
import pyodbc
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_sample_data(table_name, columns, output_file):
    print(f"📊 Processing table: {table_name}")
    
    endpoint = os.getenv("FABRIC_SQL_ENDPOINT")
    if not endpoint:
        print("❌ Error: FABRIC_SQL_ENDPOINT not found in .env")
        return

    # Connection string for Fabric Warehouse using MSI or Interactive Browser
    # Note: InteractiveBrowserCredential is handled by the driver when Authentication=ActiveDirectoryInteractive
    conn_str = (
        f"Driver={{ODBC Driver 17 for SQL Server}};"
        f"Server={endpoint};"
        f"Database=DATAAGENT_WH;"
        f"Authentication=ActiveDirectoryInteractive;"
    )

    try:
        conn = pyodbc.connect(conn_str)
        
        # We only need a sample or top records to get distinct values, 
        # but to be safe and efficient, we query 10 distinct values per column directly if possible,
        # or just pull a reasonable amount of data and process in pandas.
        # Since we want to be sure about the 10 distinct values, pulling a subset is better.
        
        query = f"SELECT TOP 1000 * FROM {table_name} WHERE year_month = '2025-01'"
        print(f"🔍 Executing query: {query}")
        df = pd.read_sql(query, conn)
        conn.close()

        output_lines = []
        for col in columns:
            if col not in df.columns:
                output_lines.append(f"{col}: [Column not found]")
                continue
            
            distinct_values = df[col].dropna().unique()
            # Convert to Series to use sample method safely
            val_series = pd.Series(distinct_values)
            num_to_sample = min(10, len(val_series))
            
            if num_to_sample > 0:
                sample_values = val_series.sample(
                    n=num_to_sample, random_state=42
                ).astype(str).tolist()
                output_lines.append(f"{col}: {', '.join(sample_values)}")
            else:
                output_lines.append(f"{col}: [No data]")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))
        
        print(f"✅ Saved samples to {output_file}")

    except Exception as e:
        print(f"❌ Error processing {table_name}: {e}")

def main():
    script_dir = os.path.dirname(__file__)
    project_root = os.path.dirname(script_dir)
    sample_data_dir = os.path.join(project_root, "data", "sample")
    os.makedirs(sample_data_dir, exist_ok=True)

    billing_columns = ["year_month","order_type","brand","ru","sub_unit","pbg","pbu","pbu_1","pbu_2","focus_flag","customer_parent","local_assembler","final_customer","g7","fu_us_oem_flag","fu_global_ems_flag","fu_g7_flag","fu_emea_oem_flag","erp_sales_rep","total_sales","total_cost","total_qty","updated_date"]
    booking_columns = ["year_month","order_type","brand","ru","sub_unit","pbg","pbu","pbu_1","pbu_2","focus_flag","customer_parent","local_assembler","final_customer","g7","fu_us_oem_flag","fu_global_ems_flag","fu_g7_flag","fu_emea_oem_flag","erp_sales_rep","total_sales","total_qty","updated_date"]

    get_sample_data("ods.fact_monthly_sales_poa_billing", billing_columns, os.path.join(sample_data_dir, "sample_data_billing.txt"))
    get_sample_data("ods.fact_monthly_sales_poa_booking", booking_columns, os.path.join(sample_data_dir, "sample_data_booking.txt"))

if __name__ == "__main__":
    main()
