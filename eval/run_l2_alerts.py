import json
import time
from pathlib import Path
from agents.triage import triage

HERE = Path(__file__).resolve().parent
ALERTS = json.loads((HERE / "l2_alerts.json").read_text(encoding="utf-8"))
RUNS = 2

rows = []
for a in ALERTS:
    for r in range(1, RUNS + 1):
        result, run, missing = triage(a["text"])
        row = {
            "id": a["id"], "run": r,
            "verdict": result.verdict, "severity": result.severity,
            "source_ips": sorted(result.source_ips), "target_ips": sorted(result.target_ips),
            "verdict_ok": result.verdict == a["expected_verdict"],
            "ips_ok": (sorted(result.source_ips) == sorted(a["expected_source_ips"])
                       and sorted(result.target_ips) == sorted(a["expected_target_ips"])),
            "lookup_corrected": bool(missing),
            "reason": result.reason,
        }
        rows.append(row)
        print(f"{a['id']:<12} run{r}: {row['verdict']:<15} {'OK ' if row['verdict_ok'] else 'BAD'} "
              f"sev={row['severity']:<8} ips={'OK' if row['ips_ok'] else 'BAD'} "
              f"corrected={row['lookup_corrected']}")
        time.sleep(30)

n = len(rows)
consistent = sum(1 for a in ALERTS
                 if len({r["verdict"] for r in rows if r["id"] == a["id"]}) == 1)
print(f"\nVerdict correct:        {sum(r['verdict_ok'] for r in rows)}/{n}")
print(f"Source/target correct:  {sum(r['ips_ok'] for r in rows)}/{n}")
print(f"Consistent across runs: {consistent}/{len(ALERTS)} alerts")
print(f"Lookup corrections:     {sum(r['lookup_corrected'] for r in rows)}/{n}")
(HERE / "l2_results.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
print("Saved eval/l2_results.json")