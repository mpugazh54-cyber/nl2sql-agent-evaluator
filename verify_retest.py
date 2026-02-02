import csv
import sys

csv_file = 'data/qa/step4_final_20260202_100228.csv'

try:
    with open(csv_file, 'r', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
except Exception as e:
    print(f"Error reading CSV: {e}")
    sys.exit(1)

print(f"Total Retested: {len(rows)}")
passes = [r for r in rows if r['evaluation_grade'] == 'PASS']
fails = [r for r in rows if r['evaluation_grade'] == 'FAIL']

print(f"Passed: {len(passes)}")
print(f"Failed: {len(fails)}")
print("-" * 30)

print("\nRESULTS DETAILS:")
for i, r in enumerate(rows):
    print(f"\n[Case {i+1}] Grade: {r['evaluation_grade']}")
    print(f"Question: {r['question']}")
    
    # Check SQL extraction
    sql = r.get('generated_sql', '')
    print(f"SQL extracted: {len(sql)} chars")
    if len(sql) < 10: print(f"WARNING: SQL content: {sql}")
    
    # Check Data Status removal
    answer = r.get('agent_answer', '')
    if "Data status: Month-end closed" in answer:
        print("WARNING: 'Data status: Month-end closed' still present in answer!")
    else:
        print("OK: 'Data status' not found.")

    if r['evaluation_grade'] == 'FAIL':
        print(f"Reason: {r['evaluation_reason']}")
