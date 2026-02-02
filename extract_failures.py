import csv

input_file = 'data/qa/step4_final_20260202_091922.csv'
output_file = 'data/qa/retest_failures.csv'

with open(input_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = [r for r in reader if r.get('evaluation_grade') == 'FAIL']

if rows:
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=reader.fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Extracted {len(rows)} failures to {output_file}")
else:
    print("No failures found to extract.")
