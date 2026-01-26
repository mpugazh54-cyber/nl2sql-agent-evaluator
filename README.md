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

## 🛠️ Getting Started

### Prerequisites
- Python 3.10+
- Azure CLI (Authenticated)
- `.env` file with necessary API keys and Fabric endpoints.

### Quick Start
```bash
# Step 1: Prepare data
python scripts/01_prepare_data.py

# Step 2: Deploy agent
python scripts/02_deploy_agent.py

# Step 3: Run QA tests
python scripts/03_run_qa.py
```

## 🔬 QA Pipeline Deep Dive

The testing pipeline is split into 4 modular steps:

1.  **Step 1: Question Generation** (`src/sales_agent/pipeline/question_gen.py`)
    - Uses level-specific prompts in `prompts/qa/` to create realistic test questions.
2.  **Step 2: Ground Truth Generation** (`src/sales_agent/pipeline/ground_truth_gen.py`)
    - Generates expected natural language answers based on business rules and data schema.
3.  **Step 3: Agent Execution** (`src/sales_agent/pipeline/executor.py`)
    - Calls the Fabric Data Agent via its REST API and captures responses.
4.  **Step 4: Result Evaluation** (`src/sales_agent/pipeline/evaluator.py`)
    - Compares agent answers against ground truth using AI for scoring.

## 📂 Project Structure

- `src/sales_agent/`: Core Python package (client, logic, utils).
- `scripts/`: Entry point scripts for the three main activities.
- `scripts/platform/`: Scripts intended for remote platforms (e.g., Fabric).
- `prompts/`: Functional AI instructions (Agent schema, QA levels).
- `data/`: Sample data (`data/sample/`), agent artifacts (`data/agent/`), and QA results (`data/qa/`).
- `logs/`: Application logs (`logs/`) and remote/sync logs (`logs/remote/`).
