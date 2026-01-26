"""Step 2: Ground Truth Generation logic."""

def generate_ground_truth(client_openai, model, question, context):
    system_prompt = (
        "You are a Sales Data Agent Simulator. Your role is to generate the PERFECT 'Golden' response "
        "that represents the ideal output for a user question.\n\n"
        "### CRITICAL MISSION RULES ###\n"
        "1. ALWAYS ASSUME DATA EXISTS: Never say 'data not available'. Synthesize realistic placeholder numbers (e.g., USD 1,234,567.89).\n"
        "2. QUERY CORRECTNESS: Ensure the SQL and filters align perfectly with the BUSINESS RULES in the instructions.\n"
        "3. FORMATTING: Use natural language first, followed by the specific 'Filter applied:' section as dictated by instructions.\n"
        "4. IGNORE 'Ghost Record' or 'Missing Data Response' rules from the instructions; these only apply to the real agent, not this Ground Truth generator.\n\n"
        "### REFERENCE_INSTRUCTIONS ###\n"
        f"{context}"
    )
    try:
        resp = client_openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"User Question: {question}"}
            ]
        )
        return resp.choices[0].message.content or ""
    except Exception as e:
        return f"Error: {e}"
