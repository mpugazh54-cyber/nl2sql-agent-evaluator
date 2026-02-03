# QA Failure Analysis Deep Dive
**Date:** 2026-02-03
**Scope:** Re-evaluation of 10 failed items from Step 3 re-run.

## Executive Summary
The primary driver of the high failure rate (90%) is a **Systemic Mismatch in Data Window Constraints**.
- **The Ground Truth Generator** is strictly instructed to reject any query beyond **October 2025** (Hardcoded in `src/.../ground_truth_gen.py`).
- **The Agent** has **no knowledge** of this constraint (Instructions in `prompts/agent/data_instructions.md` do not mention a cutoff).
- **The Database** appears to contain synthetic data for **November and December 2025**, leading the Agent to correctly answer questions that the Ground Truth rejects.

## Root Cause Analysis

### 1. The "Oct 2025" Time Window Trap (80% of Failures)
Items ID 2, 4, 5, 6, 7, 8, 9, 10 all failed because the Agent provided data for Nov/Dec 2025, while the Ground Truth refused or restricted the scope.

| Component | Instruction / Behavior | Source |
| :--- | :--- | :--- |
| **Ground Truth Generator** | `2. DATE RANGE: The available data range is strictly from '2022-01' to '2025-10'.` | `src/sales_agent/pipeline/ground_truth_gen.py` (Lines 9-11) |
| **Sales Agent** | No mentioned end date. Sample values go up to `2025-01`. | `prompts/agent/data_instructions.md` |
| **Database** | Contains data for `2025-11` and `2025-12`. | Evidenced by Agent returning specific numeric results (e.g., `60.82%` share). |

**Impact**: The Agent is being "punished" for being helpful and using available data, because the Ground Truth simulator is operating under a stricter (and hidden) rule set.

### 2. Logic & Schema Gaps (20% of Failures)
Two items failed due to genuine logic distinctions that should be addressed in Agent Instructions.

#### A. "Distribution" Channel Ambiguity (ID 1)
- **Problem**: User asked for "Distribution channel". Agent used `ILIKE '%Distribution%'` on customer columns. GT says "Dimension does not exist".
- **Insight**: The schema mentions "Channels (g7)" but not "Distribution" explicitly as a column. The Agent's search strategy was reasonable but incorrect per the GT's strict schema adherence.
- **Fix**: Add explicit mapping for "Distribution" queries (e.g., "If user asks for Distribution, use `g7 IN ('AVNET', 'ARROW'...)`" or explicitly state it's unavailable).

#### B. Grouping Rigor (ID 2)
- **Problem**: User asked for Top 5 Customers. Agent grouped by `customer_parent`. GT grouped by `COALESCE(customer_parent, local_assembler, final_customer)`.
- **Insight**: The Agent Instruction (Section 5, Entity Linkage) says "Search across all 3 columns" but doesn't explicitly mandate "Consolidate/Coalesce results by the merged key".
- **Fix**: Update Agent Instructions to mandate `COALESCE` when ranking "Customers" generally.

## Recommendations

### Option A: Unshackle the Ground Truth (Recommended)
Allow the Ground Truth to see the full 2025 year if the data exists.
- **Action**: Update `src/sales_agent/pipeline/ground_truth_gen.py` to extend date range to `2025-12`.

### Option B: Constrain the Agent
Force the Agent to ignore Nov/Dec data.
- **Action**: Update `prompts/agent/data_instructions.md` to explicitly state: "Current Simulation Date: Oct 31, 2025. Data beyond this date is invalid/projection."

### Option C: Fix Logic Gaps
Regardless of Option A/B, these fixes improve Agent quality:
- Update **Section 5** of Agent Instructions to clarify "Distribution" channel queries (use `g7`).
- Update **Section 4.1** of Agent Instructions to require `COALESCE(parent, assembler, final)` when grouping by "Customer".
