import os
from dotenv import load_dotenv
from openai import OpenAI
from fabric_data_agent_client import FabricDataAgentClient
from multi_agent_analyst import Orchestrator

# Load environment variables
load_dotenv()

def main():
    # Configuration
    # You need to set these in your .env file or environment
    TENANT_ID = os.getenv("TENANT_ID", "66d44188-4e30-446d-9ab1-a4ae1962a1b1")
    DATA_AGENT_URL = os.getenv("DATA_AGENT_URL", "https://api.fabric.microsoft.com/v1/workspaces/c731a089-60d7-4a7c-b7d7-68e549c9972f/dataagents/f16ff0f4-6945-4575-968e-5f56a103ad69/aiassistant/openai")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    if not OPENAI_API_KEY:
        print("⚠️  Please set OPENAI_API_KEY environment variable for the reasoning agents.")
        # For demo purposes, we might stop here or ask user input
        # return

    # Initialize Clients
    print("Initializing Fabric Data Agent Client...")
    fabric_client = FabricDataAgentClient(tenant_id=TENANT_ID, data_agent_url=DATA_AGENT_URL)
    
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
    
    print("Initializing Reasoning Agent Client...")
    # Using standard OpenAI client for the "Brain" agents
    openai_client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)

    # Initialize Orchestrator
    llm_model = os.getenv("LLM_MODEL", "gpt-5-nano")
    orchestrator = Orchestrator(fabric_client, openai_client, model=llm_model)
    
    # Run Analysis (Goal is now generated autonomously)
    context = orchestrator.run_analysis(max_steps=5)
    
    # Summary
    print("\n\n=== Final Analysis Summary ===")
    print(context.get_history_text())

if __name__ == "__main__":
    main()
