import csv
import os
import time
import datetime
import random

# Configuration
GOLDEN_FILE = "tests/golden/qa_pairs.csv"
LOG_DIR = "tests/logs"
AGENT_API_URL = os.getenv("DATA_AGENT_URL")

def run_tests():
    if not os.path.exists(GOLDEN_FILE):
        print("Golden file not found. Run golden_generator.py first.")
        return

    # Create log filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOG_DIR, f"run_{timestamp}.csv")
    os.makedirs(LOG_DIR, exist_ok=True)

    results = []
    
    with open(GOLDEN_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        cases = list(reader)
        
    print(f"Starting test run for {len(cases)} cases...")

    for case in cases:
        difficulty = case["difficulty"]
        question = case["question"]
        expected_sql = case["expected_sql"]
        
        print(f"[{difficulty}] Testing: {question}")
        
        # MOCK A CALL TO THE AGENT
        # In a real environment, this would be requests.post(AGENT_API_URL, json={"query": question})
        # For now, we simulate success and failure
        
        start_time = time.time()
        
        # Simulation Logic
        is_success = random.random() > 0.2 # 80% success rate simulation
        latency = round(random.uniform(0.5, 4.5), 2)
        
        if is_success:
            generated_sql = expected_sql # Perfect match
            status = "PASS"
            error_msg = ""
        else:
            generated_sql = "SELECT WRONG_COLUMN FROM WRONG_TABLE"
            status = "FAIL"
            error_msg = random.choice(["INVALID_COLUMN", "SYNTAX_ERROR", "TIMEOUT"])
            
        results.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "difficulty": difficulty,
            "question": question,
            "expected_sql": expected_sql,
            "generated_sql": generated_sql,
            "latency_sec": latency,
            "status": status,
            "error_message": error_msg
        })
        
        time.sleep(0.1) # Simulate processing time

    # Save Results
    fieldnames = ["timestamp", "difficulty", "question", "expected_sql", "generated_sql", "latency_sec", "status", "error_message"]
    with open(log_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Test run completed. Logs saved to {log_file}")
    
    # Calculate Success Rate
    success_count = sum(1 for r in results if r["status"] == "PASS")
    rate = (success_count / len(results)) * 100
    print(f"Overall Success Rate: {rate:.2f}%")

if __name__ == "__main__":
    run_tests()
