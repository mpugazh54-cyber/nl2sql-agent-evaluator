# Sales Agent Project

A State-Of-The-Art (SOTA) implementation of a Sales Data Agent using Azure Fabric and OpenAI.

## 🚀 Activity-Based Workflow

The project is organized into three primary activities:

1.  **[01] Data Preparation**
    - Script: `scripts/01_prepare_data.py`
    - Purpose: Fetch and sample data from Fabric SQL Endpoints to `data/sample/`.

2.  **[02] Agent Publishing**
    - Script: `scripts/02_deploy_agent.py`
    - Purpose: Compile agent instructions and upload configuration to Fabric OneLake.

3.  **[03] QA Execution**
    - Script: `scripts/03_run_qa.py`
    - Purpose: Execute the end-to-end QA pipeline (Generate -> GT -> Run -> Evaluate).

## 📂 Project Structure

- `src/sales_agent/`: Core Python package (client, logic, utils).
- `scripts/`: Entry point scripts for the three main activities.
- `scripts/platform/`: Scripts intended for remote platforms (e.g., Fabric).
- `docs/`: tiered documentation (Getting Started, QA Pipeline, Agent Prompts).
- `data/`: Sample data (`data/sample/`), agent artifacts (`data/agent/`), and QA inputs/results (`data/qa/`).
- `logs/`: Application logs (`logs/`) and remote/sync logs (`logs/remote/`).

---
See [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) for detailed setup and usage instructions.
