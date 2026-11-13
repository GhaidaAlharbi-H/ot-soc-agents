import time
from agents.triage import triage

ALERTS = [
    ("brute force (run 1)", "Alert: 15,302 Modbus FC5 (write single coil) requests from 185.175.0.3 to "
     "185.175.0.4 in 10 hours, almost all to coil address 1, which normal polling never uses. "
     "8,528 replies were exception code 3 (illegal data value)."),
    ("brute force (run 2)", None),
    ("brute force (run 3)", None),
    ("normal writes", "Alert: 4 Modbus FC5 (write single coil) requests from 185.175.0.3 to "
     "185.175.0.4 to coil 13 in the last hour. No exception replies."),
]

last = None
for label, alert in ALERTS:
    alert = alert or last
    last = alert
    result, run, missing = triage(alert)
    print(f"\n=== {label} ===")
    print(f"verdict={result.verdict}  severity={result.severity}  confidence={result.confidence}")
    print(f"affected={result.affected_ips}  missing_lookups={missing}")
    print(f"reason: {result.reason}")
    time.sleep(15)  # stay under the free tier's tokens-per-minute limit