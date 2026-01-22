import os
import sys
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from sales_agent.client import FabricDataAgentClient

def test_interaction():
    # Load environment variables from the project root
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    env_path = os.path.join(root_dir, ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"✅ Loaded environment variables from {env_path}")
    else:
        load_dotenv() # Fallback to standard search

    # Get configuration
    tenant_id = os.getenv("TENANT_ID")
    data_agent_url = os.getenv("DATA_AGENT_URL")

    if not tenant_id or not data_agent_url:
        print("❌ Missing TENANT_ID or DATA_AGENT_URL in environment variables.")
        return

    print("🚀 Initializing Fabric Data Agent Client...")
    try:
        client = FabricDataAgentClient(tenant_id=tenant_id, data_agent_url=data_agent_url)
        
        # 使用 get_run_details 可以取得包含 SQL 在內的詳細資訊
        # question = "Show me the total sales for KEMET in 2025-01?"
        question = "Give me 10 unique sample values for each column in the billing table."
        print(f"\n❓ Sending test question: '{question}'")
        
        # response = client.ask(question)
        details = client.get_run_details(question)

        print("\n📝 Response Highlights:")
        print("-" * 50)
        
        # 取得最後一則訊息 (Agent 的回答)
        messages = details.get("messages", {}).get("data", [])
        if messages:
            assistant_msg = next((m for m in reversed(messages) if m["role"] == "assistant"), None)
            if assistant_msg:
                print("Final Answer:", assistant_msg["content"][0]["text"]["value"])
        
        # 顯示 SQL 語法
        sql_queries = details.get("sql_queries", [])
        if sql_queries:
            print("\n🗃️ Generated SQL Queries:")
            for i, sql in enumerate(sql_queries, 1):
                print(f"[{i}] {sql}")
        else:
            print("\n⚠️ No SQL queries found in this run.")

        # 顯示資料預覽 (如果有)
        previews = details.get("sql_data_previews", [])
        if previews:
            print("\n📊 Data Previews:")
            for p in previews:
                print(p)

        print("-" * 50)
        print("\n✅ Interaction test with details completed!")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")

if __name__ == "__main__":
    test_interaction()
