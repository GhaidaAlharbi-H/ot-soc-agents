from pydantic import ValidationError
from agents.triage import TriageResult, triage

# 1. Deliberately broken output: must be caught WITHOUT calling the LLM
bad = ('{"verdict": "probably_attack", "severity": "high", "confidence": 1.7, '
       '"affected_ips": ["185.175.0.999"], "evidence": [], "reason": "x"}')
try:
    TriageResult.model_validate_json(bad)
    print("BROKEN OUTPUT WAS ACCEPTED - check the model")
except ValidationError as e:
    print(f"Caught {e.error_count()} errors in the broken output:")
    for err in e.errors():
        print(" -", err["loc"], err["msg"])

# 2. A real alert, based on the L1 brute-force fingerprint
alert = ("Alert: 15,302 Modbus FC5 (write single coil) requests from 185.175.0.3 to "
         "185.175.0.4 in 10 hours, almost all to coil address 1, which normal polling "
         "never uses. 8,528 replies were exception code 3 (illegal data value).")
result, run = triage(alert)
print(f"\nsteps={run.steps}  stopped={run.stopped_reason}")
print(result.model_dump_json(indent=2))