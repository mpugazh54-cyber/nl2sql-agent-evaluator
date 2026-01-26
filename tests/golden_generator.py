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
PROMPTS_DIR = "docs/qa_prompts"

# Initialize OpenAI Client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

MODEL = os.getenv("LLM_MODEL", "gpt-4o")

# Dimensions & Metrics (Seeds for generation)
METRICS = [
    "Total Billing (Sales)", "Total Cost", "Gross Profit (GP)", "Gross Margin % (GM%)", 
    "Average Selling Price (ASP)", "Total Bookings", "Booking Qty", "Book-to-Bill Ratio",
    "Sales MoM", "Sales QoQ", "Sales YoY", "Hit Rate (HR)", "Net Income"
]

DIMENSIONS = {
    "year_month": ["2023-01", "2023-02", "2023-03", "2023-04", "2023-05", "2023-06", "2023-07", "2023-08", "2023-09", "2023-10", "2023-11", "2023-12", "2024-01", "2024-02", "2024-03", "2024-04", "2024-05", "2024-06", "2024-07", "2024-08", "2024-09", "2024-10", "2024-11", "2024-12"],
    "order_type": ["SHIPMENT", "PAST DUE", "PAST DUE - GIT", "BOOKING"],
    "brand": ["YAGEO", "PULSE", "KEMET", "TOKIN", "Nexensos", "CHILISIN", "FERROXCUBE"],
    "pbg": ["Capacitor", "Resistors", "SENSOR", "Magnetics", "OTHER"],
    "pbu": ["MLCC", "Ceramic", "TANTALUM", "MSA", "Standard Power", "Wireless", "Wired Comm", "Std Power-FXC", "Specialized Power", "R-Chip", "Nexensos", "F&E"],
    "pbu_1": ["COMMODITY", "Antenna Chilisin", "L Mold", "Ferrite", "M Mold", "CPC", "WPC Chilisin", "LTCC Chilisin", "MCP", "Network_Pulse", "Wireless LTCC", "T LEADLESS", "Wire Wound", "SENSORS & ACTUATORS", "Leaded-R"],
    "pbu_2": ["Power - Transformer (XFMR)", "Comms. Magnetics - LAN - Pulse", "Comms. Magnetics - WAN", "EMI CORE DC LINE FILTER", "C-OTHERS", "SMD", "AC HV >=500V", "FILM RADIAL", "Power - Common Mode Choke (CMC)", "Comms. Magnetics - Automotive", "RC1206", "Power Supply", "Network", "Network - Local Area Networking", "RC01005", "SMD STD POWER", "RC0603", "SP-NT SUPER CAPACIT", "Power - Bead (BEAD)", "CARBON"],
    "focus_flag": ["Yes", "No", "Adjustment"],
    "ru": ["AMERICAS", "EMEA", "GREAT CHINA", "JAPAN & KOREA", "SOUTHEAST ASIA", "OTHERS"],
    "sub_unit": ["AMERICAS", "DIRECT FACTORY", "INDIA", "EMEA", "MALAYSIA", "EMEA GLOBAL OEMS", "NORTH EUROPE", "OTHERS", "RU HEAD OFFICE", "CHINA", "KOREA", "SINGAPORE/OEMS", "SE ASIA-G7", "VIETNAM", "TAIWAN", "PHIL/INDO"],
    "customer_parent": ["HON HAI", "ARTESYN", "Google", "FESTOOL", "BECKHOFF", "VALEO", "B&R", "H3C", "ZTE", "FDTD", "IDEAL STANDARD", "LEAR", "NORD", "GOERTEK", "ARCADIAN", "VVDN", "SHINKO", "RYODENSYA", "ENICS", "RIVIAN", "NVT"],
    "local_assembler": ["KAMSTRUP", "GARDNER", "XFUSION", "OLIGO", "AUDIX", "AUSA", "OKAZAKI", "HANSGROHE", "JABIL", "UBICQUIA", "GOOGLE", "ACCTON", "NT SALES", "POLAR", "SUZUKI FISH FINDER CO., LTD.", "OTHER - VANCOUVER", "TOEI ELECTRIC", "ACUITY", "INNORIID", "SONY"],
    "final_customer": ["ENPHASE", "STEYR", "MELLANOX TECHNOLOGIES", "CARL ZEISS", "WD", "GATESAIR", "ATLAS", "ASML", "ASCOM", "ZODIAC DATA SYSTEMS", "MOTOROLA", "CORNING", "FARNELL", "LOOTCO", "AVIAT NETWORKS", "ELM", "INFINERA", "HITACHI", "ICOM", "OMRON"],
    "g7": ["AVNET", "Non-G7", "RUTRONIK", "TTI", "ARROW", "FUTURE", "MOUSER", "DIGIKEY"],
    "fu_us_oem_flag": ["Yes", "No"],
    "fu_global_ems_flag": ["YES", "NO"],
    "fu_g7_flag": ["YES", "NO"],
    "fu_emea_oem_flag": ["Yes", "No"],
    "erp_sales_rep": ["王韻筑 Helen Wang", "葛梅芳 Sablina Ge", "Kusch", "Sclarlett", "陸英 Ying Lu", "燕禹良 David Yan", "白玉秀 Betty Bai", "王雨新 Yuxin Wang", "Ekstrom", "Sune", "YOSHIKO", "MATSUMOTO", "SHMAON", "FRANK"]
}

def load_file(path):
    if not os.path.exists(path):
        return ""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def generate_case_with_ai(level_prompt, intent, schema_context):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": f"{level_prompt}\n\nDATA SCHEMA CONTEXT:\n{schema_context}"},
                {"role": "user", "content": f"Generate one QA case for this intent: {intent}"}
            ]
        )
        content = response.choices[0].message.content.strip()
        data = json.loads(content)
        return data
    except Exception as e:
        print(f"Error generating case for '{intent}': {e}")
        return None

def generate_dataset():
    schema_context = load_file(DATA_INSTRUCTIONS_FILE)
    level_files = {
        "L1": "l1_atomic.md",
        "L2": "l2_filtering.md",
        "L3": "l3_grouping.md",
        "L4": "l4_ratios.md",
        "L5": "l5_time_series.md"
    }

    dataset = []
    
    print(f"Generating Golden Dataset using {MODEL} and modular prompts...")

    for level, filename in level_files.items():
        print(f"\n--- Generating {level} Cases ---")
        prompt_content = load_file(os.path.join(PROMPTS_DIR, filename))
        if not prompt_content:
            print(f"Warning: Prompt file for {level} not found. Skipping.")
            continue

        # Logic for level-specific intents to ensure coverage
        intents = []
        if level == "L1":
            intents = [f"Performance of {m}" for m in METRICS[:5]] # Sample some metrics
        elif level == "L2":
            intents = [f"{METRICS[0]} for {dim}={vals[0]}" for dim, vals in list(DIMENSIONS.items())[:5]]
        elif level == "L3":
            intents = [f"Rank {dim} by {METRICS[0]}" for dim in list(DIMENSIONS.keys())[3:8]]
        elif level == "L4":
            intents = ["Compare Bookings vs Billing", "Gross Margin analysis", "Hit Rate performance"]
        elif level == "L5":
            intents = [f"{m} growth analysis" for m in METRICS if "Sales" in m]

        for intent in intents:
            print(f"[{level}] Intent: {intent}")
            case = generate_case_with_ai(prompt_content, intent, schema_context)
            if case:
                # Ensure all required fields exist
                clean_case = {
                    "difficulty": case.get("difficulty", level),
                    "question": case.get("question", ""),
                    "metric": case.get("metric", "N/A"),
                    "dimension": case.get("dimension", "N/A")
                }
                dataset.append(clean_case)
            time.sleep(1) # Prevent rate limiting

    # Save to CSV
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["difficulty", "question", "metric", "dimension"])
        writer.writeheader()
        writer.writerows(dataset)
    
    print(f"\nSuccessfully generated {len(dataset)} test cases to {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_dataset()
