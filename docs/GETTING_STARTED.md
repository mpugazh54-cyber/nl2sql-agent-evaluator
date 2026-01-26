# Getting Started Guide

Follow these steps to set up and run the Sales Agent project.

## Prerequisites
- Python 3.10+
- Azure CLI (Authenticated)
- `.env` file with necessary API keys and Fabric endpoints.

## Step 1: Data Preparation
Generate sample data files from your Fabric warehouse.
```bash
python scripts/01_prepare_data.py
```

## Step 2: Agent Publishing
Deploy latest instructions and configurations to the Fabric Data Agent.
```bash
python scripts/02_deploy_agent.py
```

## Step 3: QA Execution
Run the full testing pipeline to verify agent performance.
```bash
python scripts/03_run_qa.py
```

---
For more details on the testing methodology, refer to [docs/QA_PIPELINE.md](QA_PIPELINE.md).
The QA step-by-step results are stored in `data/qa/`.
