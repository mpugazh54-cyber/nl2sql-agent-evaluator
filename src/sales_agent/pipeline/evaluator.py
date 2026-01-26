"""Step 4: Result Evaluation logic."""
import json

def evaluate(client_openai, model, question, expected, actual):
    system_prompt = (
        "Compare Agent Answer against Ground Truth. Focus on Dimensions and Filters. "
        "Return JSON: {'similarity_score': 0-100, 'grade': 'PASS'/'FAIL', 'reason': '...'}"
    )
    user_input = f"Q: {question}\nExpected: {expected}\nActual: {actual}"
    try:
        resp = client_openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(resp.choices[0].message.content)
    except Exception as e:
        return {"similarity_score": 0, "grade": "ERROR", "reason": str(e)}
