# Fabric Sales Agent Testing Framework

Testing pipeline for the Microsoft Fabric Data Agent, featuring automated query execution, SQL extraction, and OpenAI-based result evaluation.

## 📁 Standardized Project Structure

```
sales_agent/
├── main.py                     # Main Automated Pipeline (Execution Entry)
├── src/                        # Core Client & Business Logic
│   ├── fabric_data_agent_client.py  # Standard Data Agent Client
│   ├── run_analysis.py              # Orchestration Entry Point
│   └── multi_agent_analyst.py       # Multi-Agent Reasoning
├── tests/                      # Testing Framework
│   ├── test_connection.py           # Connectivity & Auth check
│   ├── test_single_query.py         # Debugging single query
│   └── test_results.csv             # Execution Results (Output)
├── scripts/                    # Utilities & Data Preparation
│   ├── generate_test_cases.py       # Test case generator (via OpenAI)
│   ├── generate_sample_data.py      # Sample data builder (via Fabric)
│   └── sample_data_*.txt            # Captured data samples
├── docs/                       # Documentation & Archives
│   ├── test_case/                 # Automated Test Cases (Input)
│   ├── instructions/                # Prompt Engineering & Guardrails
│   ├── process/                     # Execution Flows & Logs
│   └── archive/                     # Legacy scripts and logs
├── .env                        # Environment Variables
└── .fabric_token_cache         # Cached Auth Tokens
```

## 🚀 Quick Start (Testing)

### 1. Verification
Run a connection test to ensure authentication is working:
```bash
python tests/test_connection.py
```

### 2. Single Query Debug
Test a specific query with full SQL and Data Preview extraction:
```bash
python tests/test_single_query.py
```

### 3. Full Automated Pipeline
Execute the complete test suite and generate an evaluation report:
```bash
python main.py
```

## 📖 Key Documentation
- **Execution Flow**: [fabric_client_process.md](file:///docs/process/fabric_client_process.md)
- **Agent Guardrails**: [da_agent_instruction.md](file:///docs/instructions/da_agent_instruction.md)
- **Terminal Logs**: [fabric_terminal_log.md](file:///docs/process/fabric_terminal_log.md)

---
*Refer to [docs/archive/README_legacy.md](file:///docs/archive/README_legacy.md) for original project context.*
