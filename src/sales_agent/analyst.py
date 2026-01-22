import os
from typing import List, Dict, Optional
from dataclasses import dataclass, field
import json
from openai import OpenAI
from .client import FabricDataAgentClient

def log_response_to_file(agent_name: str, response: str):
    with open("agent_responses.log", "a") as f:
        f.write(f"--- {agent_name} Response ---\n")
        f.write(response + "\n")
        f.write("-" * 30 + "\n\n")

@dataclass
class AnalysisStep:
    step_id: int
    question: str
    answer: str
    thought_process: Optional[str] = None
    analysis: Optional[str] = None

@dataclass
class AnalysisContext:
    goal: str
    schema_info: str
    steps: List[AnalysisStep] = field(default_factory=list)
    
    def get_history_text(self) -> str:
        history = ""
        for step in self.steps:
            history += f"\nStep {step.step_id}:\n"
            history += f"Question: {step.question}\n"
            history += f"Answer: {step.answer}\n"
            if step.analysis:
                history += f"Analysis: {step.analysis}\n"
        return history

class BaseAgent:
    def __init__(self, client: OpenAI, model: str = "gpt-5-nano"):
        self.client = client
        self.model = model

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
        )
        content = response.choices[0].message.content
        log_response_to_file(self.__class__.__name__, content)
        return content

class SalesManagerAgent(BaseAgent):
    def generate_goals(self, schema_info: str) -> List[str]:
        system_prompt = """You are a Senior Sales Manager. Your job is to drive revenue, hit targets, and manage the sales pipeline.
        
        Guidelines:
        1. Review the available data schema.
        2. Define 10 distinct high-level business objectives focusing STRICTLY on **Shipment** and **Backlog** analysis.
        3. Do NOT ask about budget, costs, or other metrics unless they directly relate to analyzing shipments or backlog.
        4. Each goal should sound like a strategic directive (e.g., "Analyze our shipment trends vs backlog growth to identify delivery risks").
        5. Output ONLY a JSON list of strings, e.g. ["Goal 1", "Goal 2", ...].
        """
        
        user_prompt = f"""Available Data Schema:
        {schema_info}
        
        Define 10 strategic sales analysis goals based on this data. Return a JSON list of strings.
        """
        
        response = self._call_llm(system_prompt, user_prompt).strip()
        try:
            # Clean up potential markdown code blocks
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            goals = json.loads(response)
            if isinstance(goals, list):
                return [str(g) for g in goals]
            return [response] # Fallback
        except Exception as e:
            print(f"Error parsing goals: {e}")
            return [f"Default Goal: Analyze shipments and backlog based on {schema_info[:50]}..."]

    def determine_next_step(self, context: AnalysisContext) -> Dict[str, str]:
        system_prompt = """You are a Senior Sales Manager investigating **Shipments** (Invoiced Sales) and **Backlog** (Open Orders) using a Data Agent.

### Style & Constraints

* Direct, business-focused, natural language.
* Every NEXT question **must be only about Shipments or Backlog**.
* Each question must be **simple** (one clear request, no multi-part logic).
* When formulating the next question, provide **calculation_steps** describing how the Data Agent should compute the answer.
* **Each step must be something that can be done using ONE SQL query**.
* Steps must be written in **natural language**, not SQL.
* Steps may include: filtering, grouping, aggregating, joining, or computing a single metric—but each step must correspond to a single SQL query.

### CRITICAL: Review Data Agent Responses

**BEFORE formulating your next question, you MUST:**

1. **Review the "Filter applied" section** in the Data Agent's previous response to verify it correctly understood your request
2. **Check for data availability issues** - If the Data Agent reports:
   - "No data found"
   - "No shipment data exists for this period"
   - "Unable to complete" 
   - "Data does not overlap"
   - Or similar issues indicating missing/misaligned data
   
   Then you MUST **change your approach** rather than asking a similar question.

3. **Adaptive Strategy** - When encountering data issues:
   - Try a different time period (e.g., if latest month has no shipments, ask for "most recent month WITH shipment data")
   - Simplify the question (e.g., ask for shipments only first, then backlog separately)
   - Change dimensions (e.g., if region-level fails, try brand-level or aggregate)
   - Ask the Data Agent to first identify what data IS available before requesting analysis

4. **Avoid Loops** - If you've asked 2+ similar questions and gotten similar "no data" responses, you MUST pivot to a completely different approach or mark the analysis as complete.

### Responsibilities

1. **FIRST**: Review the Data Agent's previous response, especially the "Filter applied" section and any error messages.
2. Analyze the previous Data Agent answer from a business perspective (risks & opportunities).
3. Formulate the NEXT question + calculation_steps (adapting if data issues were found).
4. Decide whether the investigation is complete.

### Required JSON Output

```
{
  "thought_process": "Internal business reasoning. MUST include review of Data Agent's filter application if there was a previous response.",
  "analysis": "Business commentary on the previous data AND assessment of whether Data Agent correctly understood the request.",
  "next_question": "Natural-language question to the Data Agent, or 'COMPLETE'.",
  "calculation_steps": [
    "1. Natural-language description of a calculation that can be performed by a single SQL query.",
    "2. Next step, also something that can be computed with one SQL query.",
    "..."
  ],
  "is_complete": true|false
}
```

### Additional Rules for `calculation_steps`

* Describe **one SQL-query-worth of work** per step.

  * Example: "Calculate total Shipments by month for the last 6 months." (valid)
  * Example: "Calculate MoM % change by comparing this month to last month." (not valid in one step → must be split into two steps)
* If a calculation needs comparison, deltas, or percentage changes, break them into multiple SQL-sized steps.
* **Do not** show SQL. Only describe the logic in business-friendly natural language.
* Use explicit time ranges, customer groups, or product scopes.

        """
        
        user_prompt = f"""Goal: {context.goal}
        
        Schema Information:
        {context.schema_info}
        
        Analysis History:
        {context.get_history_text()}
        
        What is your next move, Manager? Return JSON.
        """
        
        response = self._call_llm(system_prompt, user_prompt)
        try:
            # Clean up potential markdown code blocks
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            return json.loads(response.strip())
        except Exception as e:
            return {
                "thought_process": f"Error parsing response: {e}",
                "analysis": "None",
                "next_question": "Error generating question",
                "is_complete": True
            }
    
    def _detect_repetitive_pattern(self, context: AnalysisContext, new_question: str) -> bool:
        """Detect if the new question is too similar to recent questions, indicating a loop."""
        if len(context.steps) < 2:
            return False
        
        # Check last 2 questions for similarity
        recent_questions = [step.question.lower() for step in context.steps[-2:]]
        new_q_lower = new_question.lower()
        
        # Simple keyword-based similarity check
        keywords = ['backlog', 'shipment', 'region', 'month', 'ratio', 'top 5', 'most recent']
        
        for recent_q in recent_questions:
            # Count matching keywords
            matches = sum(1 for kw in keywords if kw in recent_q and kw in new_q_lower)
            # If 4+ keywords match, likely repetitive
            if matches >= 4:
                return True
        
        return False

class Orchestrator:
    def __init__(self, fabric_client: FabricDataAgentClient, openai_client: OpenAI, model: str = "gpt-5-nano"):
        self.fabric_client = fabric_client
        self.manager = SalesManagerAgent(openai_client, model)
        
    def load_schema(self, file_path: str = "data_source_instruction.txt") -> str:
        try:
            with open(file_path, "r") as f:
                return f.read()
        except Exception as e:
            print(f"⚠️ Could not load schema from {file_path}: {e}")
            return "No schema information available."

    def run_analysis(self, max_steps: int = 5) -> AnalysisContext:
        # 1. Load Schema
        schema_info = self.load_schema()
        print("📚 Schema loaded.")
        
        # 2. Generate Goals
        print("🎯 Generating Sales Analysis Goals...")
        goals = self.manager.generate_goals(schema_info)
        
        print("\nSelect a goal to pursue:")
        for idx, g in enumerate(goals):
            print(f"{idx + 1}. {g}")
            
        while True:
            try:
                choice = input("\nEnter the number of the goal to choose: ")
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(goals):
                    goal = goals[choice_idx]
                    break
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")
                
        print(f"🚀 Selected Goal: {goal}")
        
        context = AnalysisContext(goal=goal, schema_info=schema_info)
        
        for i in range(1, max_steps + 1):
            print(f"\n--- Step {i} ---")
            
            # 3. Manager determines next step
            step_decision = self.manager.determine_next_step(context)
            
            question = step_decision.get("next_question")
            calculation_steps = step_decision.get("calculation_steps", [])
            is_complete = step_decision.get("is_complete", False)
            thought_process = step_decision.get("thought_process")
            analysis = step_decision.get("analysis")
            
            print(f"🧠 Manager Thought: {thought_process}")
            if analysis:
                print(f"🧐 Analysis of previous data: {analysis}")
            
            if is_complete or not question or question == "COMPLETE":
                print("✅ Analysis determined to be complete.")
                break
            
            # Check for repetitive patterns
            if self.manager._detect_repetitive_pattern(context, question):
                print("⚠️  WARNING: Detected repetitive question pattern. This may indicate a loop.")
                print("   The manager should adapt strategy or conclude the analysis.")
            
            # Combine question and calculation steps
            full_prompt = question
            if calculation_steps:
                full_prompt += "\n\nCalculation Steps:\n" + "\n".join(calculation_steps)
                
            print(f"🤖 Manager Question: {full_prompt}")
            
            # 4. Get Data (Data Agent as Tool)
            print(f"📡 Calling Data Agent...")
            try:
                # We use get_run_details to get data previews
                run_details = self.fabric_client.get_run_details(full_prompt)
                
                # Extract answer text (last message)
                messages = run_details.get('messages', {}).get('data', [])
                answer_text = "No text response."
                for msg in messages:
                    if msg.get('role') == 'assistant':
                        content = msg.get('content', [])
                        if content:
                            # Extract the value from the nested structure
                            # Expected format: {'text': {'annotations': [], 'value': '...'}, 'type': 'text'}
                            content_item = content[0]
                            if isinstance(content_item, dict) and 'text' in content_item:
                                answer_text = content_item['text'].get('value', str(content_item))
                            else:
                                answer_text = str(content_item)
                
                print(f"💡 Data Agent Result: {answer_text[:100]}...")
                log_response_to_file("DataAgent", f"Question: {full_prompt}\nResult: {answer_text}")
                
            except Exception as e:
                print(f"❌ Data Agent Error: {e}")
                answer_text = f"Error: {e}"

            # 5. Update Context
            step = AnalysisStep(
                step_id=i,
                question=full_prompt,
                answer=answer_text,
                thought_process=thought_process,
                analysis=analysis
            )
            context.steps.append(step)
            
        return context
