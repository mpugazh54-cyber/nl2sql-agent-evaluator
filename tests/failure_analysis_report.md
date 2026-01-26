# Failure Analysis Report
**Log File**: `tests/logs\run_20260123_170933.csv`
**Total Failures**: 4

## Error Category Breakdown
| Error Category | Count |
| :--- | :--- |
| OTHER | 3 |
| TIMEOUT | 1 |


## Detailed Failures

### What is the Total Bookings for this month?
- **Category**: OTHER
- **Error**: `INVALID_COLUMN`
- **Generated SQL**: 
```sql
SELECT WRONG_COLUMN FROM WRONG_TABLE
```
---

### Show me Total Billing for ru GREAT CHINA
- **Category**: OTHER
- **Error**: `SYNTAX_ERROR`
- **Generated SQL**: 
```sql
SELECT WRONG_COLUMN FROM WRONG_TABLE
```
---

### Show me Total Billing for ru JAPAN & KOREA
- **Category**: TIMEOUT
- **Error**: `TIMEOUT`
- **Generated SQL**: 
```sql
SELECT WRONG_COLUMN FROM WRONG_TABLE
```
---

### Show me Total Billing for customer_parent Google
- **Category**: OTHER
- **Error**: `INVALID_COLUMN`
- **Generated SQL**: 
```sql
SELECT WRONG_COLUMN FROM WRONG_TABLE
```
---
