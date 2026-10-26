import os
import time
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
from core.tracing import log_event

load_dotenv()

MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-20b")
_client = OpenAI(
    api_key=os.environ["LLM_API_KEY"],
    base_url=os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1"),
)

def _log(kind, kwargs, resp, t0):
    log_event(
        kind,
        model=MODEL,
        messages=kwargs["messages"],
        tools=[t["function"]["name"] for t in kwargs.get("tools", [])],
        output=resp.choices[0].message.model_dump(),
        prompt_tokens=resp.usage.prompt_tokens,
        completion_tokens=resp.usage.completion_tokens,
        latency_s=round(time.perf_counter() - t0, 3),
    )

def chat(messages, tools=None, temperature=0.2):
    """Free-form call. May return text OR tool calls (used from L2)."""
    kwargs = {"model": MODEL, "messages": messages, "temperature": temperature}
    if tools:
        kwargs["tools"] = tools
    t0 = time.perf_counter()
    resp = _client.chat.completions.create(**kwargs)
    _log("llm_chat", kwargs, resp, t0)
    return resp.choices[0].message

def chat_structured(messages, schema: type[BaseModel], temperature=0.2):
    """Call that MUST return JSON matching `schema`, then validated by Pydantic."""
    kwargs = {
        "model": MODEL,
        "messages": messages,
        "temperature": temperature,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": schema.__name__,
                "strict": True,
                "schema": schema.model_json_schema(),
            },
        },
    }
    t0 = time.perf_counter()
    resp = _client.chat.completions.create(**kwargs)
    _log("llm_structured", kwargs, resp, t0)
    return schema.model_validate_json(resp.choices[0].message.content)