import csv
import sys
import collections

def analyze(file_path):
    print(f"Analyzing {file_path}...")
    
    total = 0
    passed = 0
    failed = 0
    
    fail_reasons = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1
            grade = row.get("evaluation_grade", "").strip().upper()
            if grade == "PASS":
                passed += 1
            else:
                failed += 1
                fail_reasons.append({
                    "question": row.get("question", ""),
                    "reason": row.get("evaluation_reason", ""),
                    "generated_sql": row.get("generated_sql", "")
                })
                
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"\nTotal: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Pass Rate: {pass_rate:.2f}%")
    
    print("\n--- Failure Analysis ---")
    # Simple categorization by keywords
    categories = collections.defaultdict(list)
    
    for item in fail_reasons:
        reason = item['reason'].lower()
        if "sql logic" in reason or "incorrect sql" in reason:
            categories["SQL Logic Error"].append(item)
        elif "filter" in reason:
             categories["Filtering Error"].append(item)
        elif "dimension" in reason or "group by" in reason:
             categories["Grouping/Dimension Error"].append(item)
        elif "metric" in reason or "calculation" in reason:
             categories["Metric Calculation Error"].append(item)
        else:
            categories["Other/Mismatch"].append(item)
            
    for cat, items in categories.items():
        print(f"\nCategory: {cat} ({len(items)} items)")
        for i, item in enumerate(items[:3]): # Show top 3 examples per category
            print(f"  {i+1}. Q: {item['question']}")
            print(f"     Reason: {item['reason'][:200]}...")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_failures.py <csv_file>")
    else:
        analyze(sys.argv[1])
