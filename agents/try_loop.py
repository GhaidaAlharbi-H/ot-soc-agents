from agents.base_agent import run_agent
from agents.tools import GET_ASSET_SCHEMA, TOOLS

SYSTEM = ("You are an OT SOC assistant for an electrical substation. "
          "Use tools to look up devices; never guess device facts. Keep answers short.")

CASES = [
    ("one tool call", "What device is 185.175.0.5?", 8),
    ("two devices", "Which of 185.175.0.4 and 185.175.0.5 reports to the central agent?", 8),
    ("unknown device", "What device is 185.175.0.99?", 8),
    ("step limit", "Which of 185.175.0.4 and 185.175.0.5 reports to the central agent?", 1),
]

for label, question, max_steps in CASES:
    run = run_agent(SYSTEM, question, [GET_ASSET_SCHEMA], TOOLS, max_steps=max_steps)
    calls = [tc["function"]["arguments"]
             for m in run.messages if m["role"] == "assistant"
             for tc in m.get("tool_calls", [])]
    print(f"\n=== {label} ===")
    print(f"steps={run.steps}  stopped={run.stopped_reason}  tool_calls={calls}")
    print(run.final_text[:500] or "(no answer)")