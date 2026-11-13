import json
from dataclasses import dataclass
import openai
from pydantic import ValidationError
from core.llm import chat, chat_structured
from core.tracing import log_event

MAX_TOOL_RESULT_CHARS = 4000

@dataclass
class AgentRun:
    final_text: str
    messages: list
    steps: int
    stopped_reason: str  # "answered" or "max_steps"

def _run_tool(name, raw_args, tools_map):
    """Run one requested tool safely. Returns (result_text, ok)."""
    if name not in tools_map:
        return json.dumps({"error": f"tool '{name}' is not allowed"}), False
    try:
        args = json.loads(raw_args or "{}")
    except json.JSONDecodeError:
        return json.dumps({"error": "arguments were not valid JSON"}), False
    if not isinstance(args, dict):
        return json.dumps({"error": "arguments must be a JSON object"}), False
    try:
        result = tools_map[name](**args)
    except TypeError as e:
        return json.dumps({"error": f"bad arguments for {name}: {e}"}), False
    except Exception as e:
        return json.dumps({"error": f"{name} failed: {type(e).__name__}"}), False
    if not isinstance(result, str):
        result = json.dumps(result)
    if len(result) > MAX_TOOL_RESULT_CHARS:
        result = result[:MAX_TOOL_RESULT_CHARS] + " ...[truncated]"
    return result, True

def run_agent(system_prompt, user_content, tool_schemas, tools_map, max_steps=8, messages=None):
    """LLM + tools + loop. Pass `messages` to continue an earlier conversation."""
    if messages is None:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]
    else:
        messages = list(messages)  # copy, so the caller's list is not changed

    for step in range(1, max_steps + 1):
        msg = chat(messages, tools=tool_schemas)

        if not msg.tool_calls:
            text = msg.content or ""
            messages.append({"role": "assistant", "content": text})
            return AgentRun(text, messages, step, "answered")

        messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [
                {"id": tc.id, "type": "function",
                 "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                for tc in msg.tool_calls
            ],
        })
        for tc in msg.tool_calls:
            result, ok = _run_tool(tc.function.name, tc.function.arguments, tools_map)
            log_event("tool_call", step=step, name=tc.function.name,
                      arguments=tc.function.arguments, ok=ok, result_chars=len(result))
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

    log_event("agent_stopped", reason="max_steps", steps=max_steps)
    return AgentRun("", messages, max_steps, "max_steps")

def finalize(run, schema, instruction, retries=1):
    """After the tool loop, force the conclusion into `schema`. Retry once if invalid."""
    msgs = run.messages + [{"role": "user", "content": instruction}]
    for attempt in range(retries + 1):
        try:
            return chat_structured(msgs, schema)
        except (ValidationError, openai.BadRequestError) as e:
            log_event("structured_failed", attempt=attempt, error=str(e)[:300])
            msgs = msgs + [{"role": "user", "content":
                            f"Your last output was invalid: {str(e)[:300]}. "
                            "Return valid JSON matching the schema."}]
    raise RuntimeError(f"No valid {schema.__name__} after {retries + 1} attempts")