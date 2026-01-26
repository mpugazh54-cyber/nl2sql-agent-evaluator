import csv
import json
import os
import time
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
OUTPUT_FILE = "tests/golden/qa_pairs.csv"
DATA_INSTRUCTIONS_FILE = "docs/system_prompts/data_instructions.md"

# Initialize OpenAI Client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

MODEL = os.getenv("LLM_MODEL", "gpt-4o")

# Dimensions & Metrics
METRICS = [
    "Total Billing", "Total Bookings", "Gross Profit (GP)"
]

DIMENSIONS = {
    "ru": ["AMERICAS", "EMEA", "GREAT CHINA", "JAPAN & KOREA", "SOUTHEAST ASIA"],
    "brand": ["YAGEO", "PULSE", "KEMET", "TOKIN", "Nexensos", "CHILISIN", "FERROXCUBE"],
    "order_type": ["SHIPMENT", "BOOKING", "PAST DUE", "PAST DUE - GIT"],
    "customer_parent": ["HON HAI", "ARTESYN", "Google", "FESTOOL", "BECKHOFF", "VALEO"],
    "pbg": ["Capacitor", "Resistors", "SENSOR", "Magnetics"],
    "focus_flag": ["Yes", "No", "Adjustment"]
}

def load_instructions():
    with open(DATA_INSTRUCTIONS_FILE, 'r', encoding='utf-8') as f:
        return f.read()

def generate_pair_with_ai(intent, context):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": f"""You are a Sales Data QA Expert. 
Your goal is to generate a test case consisting of:
1. A Natural Language Question (How a Sales Rep would ask).
2. The Correct SQL Query (Standard Answer).

Schema Instructions:
{context}

Format your output exactly as:
QUESTION: [The natural question]
SQL: [The SQL query]
"""},
                {"role": "user", "content": f"Generate a test case for this intent: {intent}"}
            ]
        )
        content = response.choices[0].message.content.strip()
        
        # Simple parsing
        q_part = ""
        s_part = ""
        
        # Handle cases where output might be in blocks
        clean_content = content.replace("```json", "").replace("```", "")
        
        if "QUESTION:" in content and "SQL:" in content:
            parts = content.split("SQL:")
            q_part = parts[0].replace("QUESTION:", "").strip()
            s_part = parts[1].strip().replace("```sql", "").replace("```", "").strip()
        else:
            # Fallback if format is not perfect
            print(f"Warning: Unexpected format for '{intent}': {content[:50]}...")
            q_part = intent 
            s_part = "SELECT 'ERROR_PARSING_LLM_OUTPUT'"

        return q_part, s_part

    except Exception as e:
        print(f"Error generating pair for '{intent}': {e}")
        return intent, "ERROR"

def generate_dataset():
    context = load_instructions()
    data = []
    
    print(f"Generating Golden Dataset using {MODEL} with Natural Language Questions...")
    
    # 1. Generate L1 Cases (Basic Metric)
    for metric in METRICS:
        intent = f"Check {metric} for the current month"
        print(f"Generating L1: {intent}")
        question, sql = generate_pair_with_ai(intent, context)
        data.append({
            "difficulty": "L1",
            "question": question,
            "expected_sql": sql,
            "metric": metric,
            "dimension": "N/A"
        })
        time.sleep(0.5)

    # 2. Generate L2 Cases (Dimension Filter)
    for dim, values in DIMENSIONS.items():
        for val in values:
            intent = f"Check Total Billing filtering by {dim} is {val}"
            print(f"Generating L2: {intent}")
            question, sql = generate_pair_with_ai(intent, context)
            data.append({
                "difficulty": "L2",
                "question": question,
                "expected_sql": sql,
                "metric": "Total Billing",
                "dimension": dim
            })
            time.sleep(0.5)

    # Save to CSV
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["difficulty", "question", "expected_sql", "metric", "dimension"])
        writer.writeheader()
        writer.writerows(data)
    
    print(f"Generated {len(data)} AI-verified test cases to {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_dataset()
