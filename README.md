# SOTA Sales Agent Framework

This project has been restructured to follow **State-Of-The-Art (SOTA)** Python development standards. It features a modular package layout, standardized configuration, and clean data management.

## 📂 Project Structure

```text
sales_agent/
├── src/                        # Source code package
│   └── sales_agent/            # Main Python package
│       ├── __init__.py         # Package initialization
│       ├── client.py           # Fabric Data Agent Client
│       ├── analyst.py          # Multi-Agent Reasoning Logic
│       └── orchestrator.py     # Execution Orchestrator
├── tests/                      # Test suite
│   ├── test_connection.py
│   └── ...
├── data/                       # Data management
│   ├── raw/                    # Input samples & test cases
│   ├── processed/              # Intermediate data
│   └── results/                # Analysis outputs
├── logs/                       # Execution logs
├── docs/                       # Documentation
├── main.py                     # Entry point
├── pyproject.toml              # Project & Dependency Config
├── .env.template               # Environment Variable Template
└── README.md                   # Project Documentation
```

## 🚀 Quick Start

### 1. Installation
Install the package in editable mode to ensure imports work correctly:
```bash
pip install -e .
```

### 2. Configuration
Copy the template and set your credentials:
```bash
cp .env.template .env
# Edit .env with your keys
```

### 3. Running the Pipeline
Execute the main automated testing pipeline:
```bash
python main.py
```

## ✨ SOTA Features

- **Modern Packaging**: Uses `pyproject.toml` for configuration and dependencies.
- **Src-Layout**: Prevents import errors and separates source code from tests/docs.
- **Relocatable Logging**: All logs are centralized in `logs/` to keep the workspace clean.
- **Modular Design**: Core logic is split into `client`, `analyst`, and `orchestrator` modules for better maintainability.
