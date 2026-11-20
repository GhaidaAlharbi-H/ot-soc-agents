import os
import sys
import time
from dotenv import load_dotenv
from openai import OpenAI, RateLimitError
from pydantic import BaseModel
from core.tracing import log_event

load_dotenv()

MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-20b")
_client = OpenAI(
    api_key=os.environ["LLM_API_KEY"],
    base_url=os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1"),
)

_WAITS = [5, 10, 20, 40, 60]  # seconds between retries on the per-minute limit


def _create(kwargs):
    """Call the API; on a per-minute rate limit wait and retry, on a daily limit stop."""
    for attempt, default_wait in enumerate(_WAITS + [None]):
        try:
            return _client.chat.completions.create(**kwargs)
        except RateLimitError as e:
            msg = str(e).lower()
            if "per day" in msg or default_wait is None:
                raise  # daily limit, or retries used up: waiting won't help
            wait = default_wait
            try:
                wait = min(float(e.response.headers.get("retry-after", wait)), 60)
            except (TypeError, ValueError, AttributeError):
                pass
            print(f"[llm] rate limited, waiting {wait:.0f}s (retry {attempt + 1})",
                  file=sys.stderr)
            log_event("rate_limited", model=MODEL, wait_s=wait, attempt=attempt + 1)
            time.sleep(wait)


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
    resp = _create(kwargs)
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
    resp = _create(kwargs)
    _log("llm_structured", kwargs, resp, t0)
    return schema.model_validate_json(resp.choices[0].message.content)