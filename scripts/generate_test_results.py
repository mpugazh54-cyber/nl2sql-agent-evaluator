import os
import csv
import json
import time
import sys
from typing import List, Dict
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# Add src to sys.path for package discovery
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(root_dir, "src"))

# Modern import from our new package
from sales_agent.client import FabricDataAgentClient, TerminalLogger

# Load environment variables
load_dotenv()

def generate_ground_truth(client: OpenAI, user_prompt: str, context: str) -> str:
    """
    Step 1: Use OpenAI to generate an 'expected' correct answer based on context.
    """
    model = os.getenv("LLM_MODEL", "gpt-4o")
    system_prompt = (
        "You are an expert Sales Data Analyst. Given the following data schema and business rules, "
        "predict what the correct answer to the user's query should be. "
        "Your prediction should focus on the analysis dimensions and filtering rules.\n"
        "CRITICAL RULES:\n"
        "1. If the user asks for 'Billing', 'Sales', or does not specify an order type, you MUST assume `order_type = 'SHIPMENT'`. YOU MUST INCLUDE THIS IN YOUR FILTER LIST.\n"
        "2. The provided sample data is incomplete. Do NOT state that data is missing. Synthesize a response assuming data exists.\n"
        "3. Always expect Year-over-Year (YoY) comparison in the answer if prior year data is possible."
    )
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context:\n{context}\n\nUser Query: {user_prompt}"}
            ]
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        return f"Ground truth generation failed: {e}"

def evaluate_answer(client: OpenAI, user_prompt: str, expected_answer: str, agent_answer: str) -> Dict:
    """
    Step 3: Compare results.
    """
    model = os.getenv("LLM_MODEL", "gpt-4o")
    system_prompt = (
        "You are a Quality Assurance specialist. Compare the 'Agent Answer' against the 'Expected Ground Truth'. "
        "Your primary goal is to verify if the agent correctly identified the: "
        "1. Analysis Dimensions (e.g., grouping by brand, RU, or time). "
        "2. Filtering Conditions (e.g., specific year_month, focus_flag, or order_type). "
        "Ignore minor wording differences. If the dimensions and filters are correct, give a high similarity score and PASS. "
        "IMPORTANT: If Ground Truth says 'Data missing' but Agent returns actual data/numbers, DO NOT FAIL. "
        "Focus ONLY on whether the Agent's SQL and Logic (filters, dimensions) match the user's intent. "
        "Return JSON: {'similarity_score': 0-100, 'grade': 'PASS'/'FAIL', 'reason': '...'}"
    )
    
    user_prompt_eval = f"Query: {user_prompt}\nGround Truth: {expected_answer}\nAgent Answer: {agent_answer}"
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt_eval}],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        return json.loads(content) if content else {"similarity_score": 0, "grade": "ERROR", "reason": "Empty response from OpenAI"}
    except Exception as e:
        return {"similarity_score": 0, "grade": "ERROR", "reason": str(e)}

def read_file(path: str) -> str:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    # SOTA Directory Paths
    logs_dir = os.path.join(root_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    log_path = os.path.join(logs_dir, f"execution_{timestamp}.log")
    
    # Standardize output
    sys.stdout = TerminalLogger(log_path)
    print(f"📝 Execution log started at {datetime.now()}")

    # Context gathering from the new structure
    instr_dir = os.path.join(root_dir, "docs", "system_prompts")
    data_raw_dir = os.path.join(root_dir, "data", "raw")
    
    print("📖 Loading context for Ground Truth generation...")
    context = (
        f"Agent Instructions:\n{read_file(os.path.join(instr_dir, 'agent_instructions.md'))}\n\n"
        f"Data Source Instructions:\n{read_file(os.path.join(instr_dir, 'data_instructions.md'))}\n\n"
        f"Billing Samples:\n{read_file(os.path.join(data_raw_dir, 'sample_data_billing.txt'))}\n\n"
        f"Booking Samples:\n{read_file(os.path.join(data_raw_dir, 'sample_data_booking.txt'))}"
    )

    # Configuration
    tenant_id = os.getenv("TENANT_ID")
    data_agent_url = os.getenv("DATA_AGENT_URL")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_base_url = os.getenv("OPENAI_BASE_URL")
    
    fabric_client = FabricDataAgentClient(tenant_id=tenant_id, data_agent_url=data_agent_url)
    openai_client = OpenAI(api_key=openai_api_key, base_url=openai_base_url)

    input_file = os.path.join(root_dir, "data", "repro_test_case.csv")
    results_dir = os.path.join(root_dir, "data")
    # os.makedirs(results_dir, exist_ok=True) # data dir should exist
    output_file = os.path.join(results_dir, f"test_results_{timestamp}.csv")
    
    if not os.path.exists(input_file):
        print(f"❌ Input file {input_file} not found.")
        return

    test_cases = []
    with open(input_file, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            test_cases.append(row)

    print(f"📋 Found {len(test_cases)} test cases. Starting pipeline...")

    results = []
    for i, tc in enumerate(test_cases):
        prompt = tc.get("user_prompt") or tc.get("question")
        if not prompt: continue
        
        print(f"\n[{i+1}/{len(test_cases)}] Query: {prompt[:100]}...")
        
        try:
            # Step 1: Generate Ground Truth
            print("🤖 Step 1: Generating Ground Truth...")
            ground_truth = generate_ground_truth(openai_client, prompt, context)
            
            # Step 2: Run Data Agent
            print("🚀 Step 2: Running Data Agent...")
            run_details = fabric_client.get_run_details(prompt)
            agent_answer = run_details.get("answer", "")
            sql_analysis = run_details.get("sql_analysis", {})
            actual_sql = json.dumps(sql_analysis.get("sql_queries", []), indent=2)
            
            # Step 3: Evaluate
            print("🧐 Step 3: Evaluating Similarity...")
            eval_result = evaluate_answer(openai_client, prompt, ground_truth, agent_answer)
            
            results.append({
                "user_prompt": prompt,
                "expected_answer": ground_truth,
                "agent_answer": agent_answer,
                "generated_sql": actual_sql,
                "similarity_score": eval_result.get("similarity_score"),
                "evaluation_grade": eval_result.get("grade"),
                "evaluation_reason": eval_result.get("reason")
            })
            print(f"✨ Score: {eval_result.get('similarity_score')} | Grade: {eval_result.get('grade')}")

        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({"user_prompt": prompt, "agent_answer": f"ERROR: {e}", "evaluation_grade": "ERROR"})

    # Save Results
    fieldnames = ["user_prompt", "expected_answer", "agent_answer", "generated_sql", "similarity_score", "evaluation_grade", "evaluation_reason"]
    with open(output_file, mode='w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"✅ Completed. Results saved to {output_file}")

if __name__ == "__main__":
    main()
