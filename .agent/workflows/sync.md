---
description: Sync Data Agent instructions to published folder
---

This workflow synchronizes the human-readable instructions in `docs/da_instructions` to the machine-readable JSON files in the `published` directory.

// turbo
1. Run the sync script:
   `python scripts/sync_instructions.py`

2. Verify the changes in:
   - `published/stage_config.json`
   - `published/data-warehouse-DATAAGENT_WH/datasource.json`
   - `published/data-warehouse-DATAAGENT_WH/fewshots.json`
