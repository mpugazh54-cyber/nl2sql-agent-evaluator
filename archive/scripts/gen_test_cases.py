import os
import csv
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def read_sample_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def generate_test_cases():
    print("\n📝 --- Test Case Generation Tool ---")
    
    # User Input for Test Case Type
    print("\nAvailable types include: billing, booking, billing and booking, ambiguous terms (歧異詞), etc.")
    test_type = input("Which 'type' of test cases would you like to generate? (Enter to use default): ")
    if not test_type:
        test_type = "general sales queries"
    
    print("\n📖 Reading sample data and instructions...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, ".."))
    
    # Read Sample Data
    billing_samples = read_sample_file(os.path.join(script_dir, "sample_data_billing.txt"))
    booking_samples = read_sample_file(os.path.join(script_dir, "sample_data_booking.txt"))
    
    # Read Instructions
    instr_dir = os.path.join(root_dir, "docs", "da_instructions")
    data_source_instr = read_sample_file(os.path.join(instr_dir, "da_data_source_instruction.md"))

    print("🤖 Preparing OpenAI request...")
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("LLM_MODEL", "gpt-5-nano")

    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in .env")
        return

    client = OpenAI(api_key=api_key, base_url=base_url)

    system_prompt = (
        "You are an expert Sales Data Analyst and a member of a company's sales team. "
        "Your goal is to help test a new Data Agent that has access to sales billing and booking data."
    )

    user_prompt = f"""
I need you to generate 20 test questions that a sales team member would ask naturally (using business language). 

### Goal:
Generate test cases of the following type/focus: {test_type}

### Context & Rules for the Data Agent:
The Data Agent follows these instructions, which you must use to ensure your questions are valid and challenging:
- **Data Source Instructions**: {data_source_instr}

### Sample Data for Inspiration:
### Billing Table Samples (Actual Sales):
{billing_samples}

### Booking Table Samples (Orders / Pipeline):
{booking_samples}

### Requirements:
1. **Sales Persona**: The questions MUST sound like a human sales person (natural language). 
   - Good example: "How did our bookings look in North America for KEMET last month?"
   - Bad example: "SELECT total_sales FROM booking WHERE ru='NA' AND brand='KEMET'"
2. **Sales Perspective**: Focus on metrics a sales rep cares about: target achievement, customer trends, product performance, and comparison across regions.
3. **Guardrail Testing**: If the user requested 'ambiguous terms' (歧異詞) or 'unsupported metrics', include questions that test if the agent correctly identifies missing data or unsupported columns (like order count or average per order) based on the provided instructions.
4. **Format**: Return the output in a JSON format. You can return either a list of objects `[[{{"question": "..."}}]]` or an object with a key like 'test_cases' containing that list.

Return ONLY the JSON.
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        data = json.loads(content)
        
        # Extract questions list flexibly
        test_cases = []
        if isinstance(data, list):
            test_cases = data
        elif isinstance(data, dict):
            # Check common keys first
            for key in ["test_cases", "questions", "list", "data"]:
                if key in data and isinstance(data[key], list):
                    test_cases = data[key]
                    break
            
            # If still empty, look for any list value
            if not test_cases:
                for val in data.values():
                    if isinstance(val, list):
                        test_cases = val
                        break
        
        # Timestamped Filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_case_{test_type}_{timestamp}.csv"
        # We also create/overwrite the standard test_case.csv for the main pipeline to use
        output_dir = os.path.join(root_dir, "docs", "test_case")
        standard_output = os.path.join(output_dir, "test_case.csv")
        timestamped_output = os.path.join(output_dir, filename)
        
        if not test_cases:
            print("⚠️ OpenAI returned 0 questions. Raw content for debugging:")
            print(content)
            return

        print(f"📝 Saving {len(test_cases)} questions to {filename}...")
        
        # Write to both for convenience
        for output_file in [standard_output, timestamped_output]:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=["question"])
                writer.writeheader()
                for tc in test_cases:
                    q = tc.get("question") if isinstance(tc, dict) else str(tc)
                    if q:
                        writer.writerow({"question": q})

        print(f"✅ Successfully generated {len(test_cases)} questions in {filename}")

    except Exception as e:
        print(f"❌ Error during generation: {e}")
        if 'content' in locals():
            print("Raw response content:", content)

if __name__ == "__main__":
    generate_test_cases()
