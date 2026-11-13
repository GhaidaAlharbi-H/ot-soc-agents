import ipaddress
import json
import re
from typing import Literal
from pydantic import BaseModel, ConfigDict, field_validator
from agents.base_agent import run_agent, finalize
from agents.tools import TOOL_SCHEMAS, TOOLS
from core.tracing import log_event

class Evidence(BaseModel):
    model_config = ConfigDict(extra="forbid")
    fact: str
    source: Literal["alert", "observed", "assumed"]

class TriageResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    verdict: Literal["real_attack", "false_positive", "uncertain"]
    severity: Literal["low", "medium", "high", "critical"]
    confidence: float
    affected_ips: list[str]
    evidence: list[Evidence]
    reason: str

    @field_validator("confidence")
    @classmethod
    def confidence_range(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("confidence must be between 0 and 1")
        return v

    @field_validator("affected_ips")
    @classmethod
    def real_ips(cls, v):
        for ip in v:
            ipaddress.ip_address(ip)
        return v

SYSTEM = """You are the Triage agent in an OT SOC for an electrical substation (Modbus/TCP).
Decide whether an alert is a real attack or a false positive, and how severe it is.
Rules:
- Look up every device in the alert with get_asset. Never guess device facts.
- Compare the alert with normal behaviour from get_baseline before judging. Activity far
  outside the baseline (much higher rate, unused addresses, exception replies) is not normal.
- Severity follows physical consequence (device role and criticality), not data sensitivity.
- Use as few tool calls as needed. Keep answers short."""

FINAL = ("Give your final triage verdict as JSON. For each evidence item set source to "
         "'alert' (stated in the alert), 'observed' (asset or baseline facts that are observed) or "
         "'assumed' (asset facts under assumed).")

IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

def looked_up_ips(messages):
    """IPs the agent actually passed to get_asset."""
    ips = set()
    for m in messages:
        if m["role"] != "assistant":
            continue
        for tc in m.get("tool_calls", []):
            if tc["function"]["name"] == "get_asset":
                try:
                    ips.add(json.loads(tc["function"]["arguments"]).get("ip"))
                except json.JSONDecodeError:
                    pass
    return ips

def triage(alert_text, max_steps=6):
    run = run_agent(SYSTEM, alert_text, TOOL_SCHEMAS, TOOLS, max_steps=max_steps)

    # Fix 2: verify in code that every device in the alert was looked up
    missing = sorted(set(IP_RE.findall(alert_text)) - looked_up_ips(run.messages))
    if missing:
        log_event("incomplete_lookup", missing=missing)
        correction = {"role": "user", "content":
                      f"Before concluding, look up these devices with get_asset: {', '.join(missing)}."}
        run = run_agent(None, None, TOOL_SCHEMAS, TOOLS, max_steps=3,
                        messages=run.messages + [correction])

    return finalize(run, TriageResult, FINAL), run, missing