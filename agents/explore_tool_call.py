import json
from core.llm import chat
from agents.tools import GET_ASSET_SCHEMA, TOOLS

def show(label, obj):
    print(f"\n===== {label} =====")
    print(json.dumps(obj, indent=2, ensure_ascii=False))

messages = [
    {"role": "system", "content": "You are an OT SOC assistant for an electrical substation. "
                                  "Use tools to look up devices; never guess device facts."},
    {"role": "user", "content": "What device is 185.175.0.5, and is it safe to isolate it?"},
]
show("1-2. What we send", messages)

# Round 1: the model decides whether to call a tool
msg = chat(messages, tools=[GET_ASSET_SCHEMA])
show("3. Model reply (round 1)", {"content": msg.content, "tool_calls": [
    {"id": tc.id, "name": tc.function.name, "arguments": tc.function.arguments}
    for tc in (msg.tool_calls or [])
]})

if not msg.tool_calls:
    print("\nThe model answered without calling a tool.")
    raise SystemExit

# Record the model's request in the conversation, exactly as it asked
messages.append({
    "role": "assistant",
    "content": msg.content or "",
    "tool_calls": [
        {"id": tc.id, "type": "function",
         "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
        for tc in msg.tool_calls
    ],
})

# OUR code runs the tool. The model only asked.
for tc in msg.tool_calls:
    func = TOOLS.get(tc.function.name)
    args = json.loads(tc.function.arguments)
    result = func(**args) if func else json.dumps({"error": "unknown tool"})
    messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
    show(f"4. Tool result sent back ({tc.function.name})", json.loads(result))

# Round 2: the model answers, now with the tool's result
final = chat(messages, tools=[GET_ASSET_SCHEMA])
show("5. Final answer", {"content": final.content})
show("FULL MESSAGE LIST", messages)