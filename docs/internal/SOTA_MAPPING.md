# SOTA Structure Mapping

| Component | New Path | Description |
| :--- | :--- | :--- |
| **Logger** | `src/sales_agent/utils/logger.py` | Shared logging utility |
| **Agent Client** | `src/sales_agent/client.py` | Unified Fabric API client |
| **QA Gen** | `src/sales_agent/pipeline/question_gen.py` | Step 1 logic |
| **GT Gen** | `src/sales_agent/pipeline/ground_truth_gen.py` | Step 2 logic |
| **Executor** | `src/sales_agent/pipeline/executor.py` | Step 3 logic |
| **Evaluator** | `src/sales_agent/pipeline/evaluator.py` | Step 4 logic |
| **Orchestrator**| `scripts/run_pipeline.py` | Main entry point |
