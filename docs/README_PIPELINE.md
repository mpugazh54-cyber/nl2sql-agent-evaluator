# Sales Agent Testing Pipeline (SOTA Modular Format)

This pipeline automates the generation, execution, and evaluation of sales data queries against the Fabric Data Agent.

## Architecture

The pipeline is split into 4 modular steps:

1.  **Step 1: Question Generation** (`src/sales_agent/pipeline/question_gen.py`)
    *   Uses level-specific prompts in `docs/qa_prompts/` to create realistic test questions.
2.  **Step 2: Ground Truth Generation** (`src/sales_agent/pipeline/ground_truth_gen.py`)
    *   Generates expected natural language answers based on business rules and data schema.
3.  **Step 3: Agent Execution** (`src/sales_agent/pipeline/executor.py`)
    *   Calls the Fabric Data Agent via its REST API and captures the answer and generated SQL.
4.  **Step 4: Result Evaluation** (`src/sales_agent/pipeline/evaluator.py`)
    *   Compares agent answers against ground truth using AI to score similarity and correctness.

## Usage

### Run the full pipeline
```bash
python scripts/run_pipeline.py
```

### Run individual steps
You can run specific steps independently. For steps after Step 1, you usually need to provide the output from the previous step as `--input`.

**Step 1: Question Generation**
```bash
# Generate for all levels (L1-L5), 2 questions each (default)
python scripts/run_pipeline.py --step 1

# Generate for specific levels with custom count
python scripts/run_pipeline.py --step 1 --level L1 L3 --count 5
```

**Step 2: Ground Truth Generation**
```bash
python scripts/run_pipeline.py --step 2 --input data/pipeline/step1_questions_XXX.csv
```

**Step 3: Agent Execution**
```bash
python scripts/run_pipeline.py --step 3 --input data/pipeline/step2_truth_XXX.csv
```

**Step 4: Result Evaluation**
```bash
python scripts/run_pipeline.py --step 4 --input data/pipeline/step3_results_XXX.csv
```

## Structure
*   `src/sales_agent/`: Core package containing the logic.
*   `scripts/`: Executable scripts including the orchestrator.
*   `config/`: Configuration files.
    *   `generation_config.json`: Central definition of metrics and dimensions.
*   `docs/qa_prompts/`: System instructions for different difficulty levels.
*   `data/pipeline/`: Output artifacts for each step.
