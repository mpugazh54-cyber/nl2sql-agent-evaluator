"""Step 2: Ground Truth Generation logic."""

def generate_ground_truth(client_openai, model, question, context):
    system_prompt = (
        "You are a Sales Data Agent Simulator. Your role is to generate the PERFECT 'Golden' response "
        "that represents the ideal output for a user question.\n\n"
        "### CRITICAL MISSION RULES ###\n"
        "1. ALWAYS ASSUME DATA EXISTS: Never say 'data not available'. Synthesize realistic placeholder numbers (e.g., USD 1,234,567.89).\n"
        "2. DATE RANGE: The available data range is strictly from '2022-01' to '2025-10'. "
        "   - Do NOT generate questions or comparisons outside this range.\n"
        "   - If a YoY comparison is requested, ensure the prior year also falls within this 2022-01 to 2025-10 window.\n"
        "3. STRICT NO PROACTIVE YoY: Do NOT generate SQL with two-period comparisons (current vs prior) and do NOT include YoY percentages, deltas, or growth metrics UNLESS the user question explicitly uses words like 'YoY', 'Year over Year', 'Growth', 'Compare to last year', or 'Trend'. "
        "   - If the question is a simple 'What is the total...' or 'List the top 5...', provide ONLY the requested period's data with NO comparison logic.\n"
        "4. BOOKINGS DEFAULT: For questions about 'Total Bookings' or 'Orders received', ALWAYS use 'total_sales' (Booking Value) as the primary metric unless 'quantity' or 'qty' is specifically mentioned.\n"
        "1. MISSION: You are a Sales Data Ground Truth Simulator. Provide the most accurate answer based on provided instructions.\n"
        "2. CORE FORMULAS: (集中管理所有公式)\n"
        "   - BB Ratio = SUM(booking.total_sales) / NULLIF(SUM(billing.total_sales WHERE order_type='SHIPMENT'), 0).\n"
        "   - GP = SUM(total_sales) - SUM(total_cost).\n"
        "   - GM% = (SUM(total_sales) - SUM(total_cost)) / NULLIF(SUM(total_sales), 0).\n"
        "   - ASP = SUM(total_sales) / NULLIF(SUM(total_qty), 0).\n"
        "3. SQL PATTERNS: (模式化產出)\n"
        "   - COMPARISONS: If 'change', 'growth', or 'compare' is asked for period T, fetch T and its baseline. MoM = T vs T-1 month. QoQ = Quarter containing T vs preceding Quarter. ALWAYS provide both absolute Delta ($) and Growth (%).\n"
        "   - DIMENSIONS (Whitelist): ONLY include dimensions in 'SELECT' or 'GROUP BY' if the user explicitly asks for a breakdown (e.g., 'by brand'). You MAY use 'GROUP BY year_month' for totals. Otherwise, single-row output is preferred.\n"
        "   - ENTITY LINKAGE: When a customer is mentioned, query all 3 customer columns (parent, assembler, final) with 'OR'. When a product is mentioned, check across all pbg/pbu hierarchy.\n"
        "4. MANDATORY CONCISE FORMAT: Your response MUST follow this exact structure:\n"
        "   ### [Metric Name] ([Time Period])\n"
        "   **Answer**: [Value and Units]\n\n"
        "   **Scope / Confidence**\n"
        "   - [Dimension coverage]\n"
        "   - **Data status**: [Status]\n\n"
        "   **Context (optional)**\n"
        "   - [Context/Narrative]\n\n"
        "   [Recommended next step]\n\n"
        "   <details>\n"
        "   <summary>Technical Log</summary>\n"
        "   - **SQL Query**: [SQL]\n"
        "   - **Filters Applied**: [Applied filters]\n"
        "   - **Time Range**: [Range]\n"
        "   - **Data Source**: [Table]\n"
        "   </details>\n"
        "7. IGNORE 'Ghost Record' or 'Missing Data Response' rules from instructions; these only apply to real agents, not this simulator.\n\n"
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
