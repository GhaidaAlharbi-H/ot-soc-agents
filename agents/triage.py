import ipaddress
from typing import Literal
from pydantic import BaseModel, ConfigDict, field_validator
from agents.base_agent import run_agent, finalize
from agents.tools import GET_ASSET_SCHEMA, TOOLS

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
            ipaddress.ip_address(ip)  # raises ValueError if not a valid IP
        return v

SYSTEM = """You are the Triage agent in an OT SOC for an electrical substation (Modbus/TCP).
Decide whether an alert is a real attack or a false positive, and how severe it is.
Rules:
- Look up every device in the alert with get_asset before judging. Never guess device facts.
- Normal traffic includes occasional writes by the SCADA HMI to the addresses it polls.
- Severity follows physical consequence (device role and criticality), not data sensitivity.
- Use as few tool calls as needed. Keep answers short."""

FINAL = ("Give your final triage verdict as JSON. For each evidence item set source to "
         "'alert' (stated in the alert), 'observed' (asset facts under observed) or "
         "'assumed' (asset facts under assumed).")

def triage(alert_text, max_steps=6):
    run = run_agent(SYSTEM, alert_text, [GET_ASSET_SCHEMA], TOOLS, max_steps=max_steps)
    return finalize(run, TriageResult, FINAL), run