import csv
import re
import os
import glob

# Configuration
LOG_DIR = "tests/logs"
REPORT_FILE = "tests/failure_analysis_report.md"

ERROR_PATTERNS = {
    "INVALID_COLUMN": r"Invalid column name|Column .* does not exist",
    "MISSING_VIEW": r"Relation .* does not exist|Table .* not found",
    "SYNTAX_ERROR": r"syntax error at or near",
    "HALLUCINATION": r"Hallucinated value",
    "TIMEOUT": r"Timeout|Deadline Exceeded"
}

def analyze_latest_log():
    # Find latest log file
    if not os.path.exists(LOG_DIR):
        print(f"Log directory {LOG_DIR} does not exist.")
        return

    log_files = glob.glob(os.path.join(LOG_DIR, "*.csv"))
    if not log_files:
        print("No log files found.")
        return

    latest_log = max(log_files, key=os.path.getmtime)
    print(f"Analyzing {latest_log}...")
    
    failures = []
    try:
        with open(latest_log, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("status") == "FAIL":
                    failures.append(row)
    except Exception as e:
        print(f"Error reading log: {e}")
        return

    if not failures:
        print("No failures found in the latest run! 🎉")
        return

    # Categorize Errors
    def categorize(msg):
        if not msg: return "UNKNOWN"
        for cat, pattern in ERROR_PATTERNS.items():
            if re.search(pattern, str(msg), re.IGNORECASE):
                return cat
        return "OTHER"

    error_counts = {}
    for row in failures:
        cat = categorize(row.get("error_message"))
        row["error_category"] = cat
        error_counts[cat] = error_counts.get(cat, 0) + 1
    
    # Generate Report
    stats_markdown = "| Error Category | Count |\n| :--- | :--- |\n"
    for cat, count in error_counts.items():
        stats_markdown += f"| {cat} | {count} |\n"
    
    report_content = f"""# Failure Analysis Report
**Log File**: `{latest_log}`
**Total Failures**: {len(failures)}

## Error Category Breakdown
{stats_markdown}

## Detailed Failures
"""
    
    for row in failures:
        report_content += f"""
### {row.get('question', 'N/A')}
- **Category**: {row['error_category']}
- **Error**: `{row.get('error_message', 'N/A')}`
- **Generated SQL**: 
```sql
{row.get('generated_sql', 'N/A')}
```
---
"""

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(report_content)
    
    print(f"Analysis report saved to {REPORT_FILE}")

if __name__ == "__main__":
    analyze_latest_log()
