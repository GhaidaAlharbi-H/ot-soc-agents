import json
import sys
import time
from pathlib import Path
from agents.triage import triage

HERE = Path(__file__).resolve().parent
alert_id = sys.argv[1]
runs = int(sys.argv[2]) if len(sys.argv) > 2 else 3
alerts = json.loads((HERE / "l2_alerts.json").read_text(encoding="utf-8"))
a = next(x for x in alerts if x["id"] == alert_id)

for r in range(1, runs + 1):
    result, run, missing = triage(a["text"])
    ok = result.verdict == a["expected_verdict"]
    print(f"{alert_id} run{r}: {result.verdict} {'OK' if ok else 'BAD'} sev={result.severity}")
    print(f"  reason: {result.reason}")
    time.sleep(20)