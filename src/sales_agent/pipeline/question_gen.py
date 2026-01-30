"""Step 1: Question Generation logic."""
import os
import json
import csv
import time

def load_prompt(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def generate_questions(client_openai, model, schema_context, prompt_dir, metrics, dimensions, target_level=None, count=2):
    level_files = {
        "L1": "l1_atomic.md",
        "L2": "l2_filtering.md",
        "L3": "l3_grouping.md",
        "L4": "l4_ratios.md",
        "L5": "l5_time_series.md"
    }
    
    results = []
    # If target_level is a list (from CLI), process each. If string, wrap in list.
    target_levels = [target_level] if isinstance(target_level, str) else target_level
    
    items_to_process = {}
    if target_levels:
        for lvl in target_levels:
            if lvl in level_files:
                items_to_process[lvl] = level_files[lvl]
    else:
        items_to_process = level_files

    for level, filename in items_to_process.items():
        print(f"Generating {count} questions for {level}...")
        prompt = load_prompt(os.path.join(prompt_dir, filename))
        if not prompt: continue
        
        if level == "L1":
            # L1: Sequential coverage of metrics. 
            if count >= len(metrics):
                target_metrics = metrics
            else:
                target_metrics = metrics[:count]
            intents = [f"Analyze {m}" for m in target_metrics]
        elif level == "L2":
            # L2: Cycle through all dimensions to ensure coverage.
            # EXCLUDE time-based dimensions from the primary rotation, because we now force
            # a time-filter into EVERY question as a secondary condition.
            # Asking "What is sales in 2024?" (pure time) is now redundant/too simple.
            dim_keys = [k for k in dimensions.keys() if k not in ["year_month", "year_quarter", "calendar_year"]]
            
            # We want to iterate through dimensions. If count > len(dims), we cycle.
            intents = []
            import random
            
            # Create a long list of dimensions to pop from
            extended_dims = []
            while len(extended_dims) < count:
                # Append keys in strict order (no shuffle) to cycle through them
                extended_dims.extend(dim_keys)
                
            # Slice to exact count
            target_dims = extended_dims[:count]
            
            for md in target_dims:
                # Pick a random metric to go with the dimension
                m = random.choice(metrics)
                
                # Hyper-Natural Intent: Act like a business user.
                # Strictly enforce FILTER-ONLY, NO GROUPING/BREAKDOWN.
                
                if md == "order_type":
                    # Special handling for order_type to ensure natural phrasing
                    req = (
                                f"I'm looking for {m} figures for a specific order type. "
                                f"IMPORTANT MAPPING: "
                                f"If excluding/including 'SHIPMENT', say 'shipments' or 'shipped qty'. "
                                f"For 'BOOKING', say 'bookings' or 'booked orders'. "
                                f"For 'PAST DUE', say 'past due orders'. "
                                f"Do NOT use technical terms like 'order_type = ...'. "
                                f"Include a specific month/quarter/year."
                            )
                else:
                    req = (
                        f"I'm looking for the {m} data for a specific {md}. "
                        f"CRITICAL: This MUST be a FILTER question, NOT a breakdown/grouping. "
                        f"Use a specific value from the schema (e.g. if dimension is 'brand', use 'YAGEO'). "
                        f"Do NOT say 'by {md}' or 'for each {md}'. "
                        f"Include a specific month/quarter/year. Ask naturally as a Sales Manager would."
                    )

                intents.append({
                    "metric": m,
                    "dimension": md,
                    "natural_request": req
                })
        else:
            # L3+: Random selection for diversity
            import random
            intents = [{"metric": random.choice(metrics), "dimension": "N/A", "natural_request": f"Analyze {random.choice(metrics)}"} for _ in range(count)]
        
        for i, intent_data in enumerate(intents, 1):
            if isinstance(intent_data, dict):
                metric_name = intent_data["metric"]
                dim_name = intent_data["dimension"]
                user_msg = intent_data["natural_request"]
                display_intent = f"Natural Request: {metric_name} | {dim_name}"
            else:
                display_intent = intent_data
                user_msg = f"Generate one QA for: {display_intent}"

            print(f"  [{i}/{len(intents)}] {display_intent}...")
            try:
                resp = client_openai.chat.completions.create(
                    model=model,
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": f"{prompt}\n\nSCHEMA:\n{schema_context}\n\nDATE_CONSTRAINT: Data range is '2022-01' to '2025-10'. Do NOT generate questions outside this range."},
                        {"role": "user", "content": user_msg}
                    ]
                )
                data = json.loads(resp.choices[0].message.content)
                
                # --- LOGIC SELF-CORRECTION PASS ---
                verify_resp = client_openai.chat.completions.create(
                    model=model,
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": "You are a Logic Quality Controller for Sales Data QA.\n"
                            "CRITICAL RULES:\n"
                            "1. QoQ (Quarter-over-Quarter) MUST use a Quarter time grain (e.g., 'Q3 2024'). It is ILLOGICAL to ask for QoQ using a single month (e.g., '2024-04').\n"
                            "2. MoM (Month-over-Month) MUST use a specific month (YYYY-MM).\n"
                            "3. If a question is logically flawed, REWRITE it while keeping the original intent. Return the final corrected JSON structure."},
                        {"role": "user", "content": f"Review and fix if necessary: {json.dumps(data)}"}
                    ]
                )
                data = json.loads(verify_resp.choices[0].message.content)
                # ----------------------------------

                results.append({
                    "difficulty": data.get("difficulty", level),
                    "question": data.get("question", ""),
                    "metric": data.get("metric", "N/A"),
                    "dimension": data.get("dimension", "N/A")
                })
                time.sleep(0.5)
            except Exception as e:
                print(f"Error in {level}: {e}")
    return results
