import os
import json
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add project root to sys.path to allow importing from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from sales_agent.client import FabricDataAgentClient, TerminalLogger

# Load environment variables
load_dotenv()

def test_single():
    # Create a timestamped log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"log_{timestamp}.txt"
    sys.stdout = TerminalLogger(log_filename)
    
    print(f"📝 Execution log started at {datetime.now()}")
    print(f"📂 Logging to: {log_filename}\n")

    tenant_id = os.getenv("TENANT_ID")
    data_agent_url = os.getenv("DATA_AGENT_URL")
    
    if not tenant_id or not data_agent_url:
        print("❌ Missing environment variables.")
        return

    print(f"🚀 Initializing Fabric Data Agent Client...")
    client = FabricDataAgentClient(tenant_id=tenant_id, data_agent_url=data_agent_url)
    
    question = "Show me the top 3 brands by total sales in 2025-01 from billing."
    print(f"\n❓ Question: {question}")
    
    try:
        print("⏳ Waiting for agent response...")
        # Use get_run_details to see SQL and steps
        details = client.get_run_details(question)
        
        print("\n--- AGENT RESPONSE ---")
        print(f"Answer: {details.get('answer')}")
        
        print("\n--- SQL ANALYSIS ---")
        sql_analysis = details.get("sql_analysis", {})
        print(f"Queries: {json.dumps(sql_analysis.get('sql_queries'), indent=2)}")
        print(f"Data Previews: {json.dumps(sql_analysis.get('data_previews'), indent=2)}")
        
        print("\n--- FULL DETAILS (JSON) ---")
        # print(json.dumps(details, indent=2))
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_single()
