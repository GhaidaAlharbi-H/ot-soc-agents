# Failure cases

## FC-1: Brute-force writes judged false positive (L2.3, 13 Nov 2026)
- Alert: 15,302 FC5 writes .3 -> .4 in 10 h, mostly coil 1, 8,528 exception code 3.
- Verdict: false_positive, low, confidence 0.9 (truth: real_attack, T0806 Brute Force I/O).
- Causes: looked up only .3 (ignored "look up every device"); treated rejected writes as harmless
  (~6,774 writes were not rejected); used the prompt rule "normal includes occasional writes"
  without a number (normal is ~20 writes per IED per 4.7 h).
- Fix planned: baseline tool with L1 numbers, check that every alert IP was looked up,
  quantitative prompt rule; later ATT&CK lookup (L3) and investigation skill (L4).

  - Result after fix (13 Nov 2026): 3/3 runs real_attack/high; normal-writes control
  correctly false_positive/low. Agent used the baseline numerically (~1,530 vs 4.7 writes/h).
- Code lookup check triggered in 2/4 runs: the model ignores "look up every device" about half the time.
- New issues: affected_ips is ambiguous (attacker included in some runs, not others);
  self-reported confidence is constant (0.9) and not informative.

  ## FC-2: Length manipulation judged false positive (L2.4, 13 Nov 2026)
- Alert A2: 4 reads .3 -> .5, header length 27 but 12 bytes sent. 1 of 2 runs: false_positive.
- Cause: agent saw the mismatch but explained it as packet loss/fragmentation; baseline had no
  length fact. Also stated a wrong protocol fact ("13-byte read request"; correct is 12).
- Fix: added header_length_mismatches: 0 to baseline (measured: 0 of 98,471 benign messages).
- Lessons: missing evidence lets the model pick an innocent explanation; protocol knowledge gap
  (L3/L4); L7 length features must use reassembled TCP streams.
- Design decision from L2.4: the model skipped device lookups in 10/10 runs, so in L5 the
  orchestrator looks up alert IPs in code before the agent starts.

  - After adding the baseline fact (A2 x3): 1/3 real_attack. The agent now saw the deviation but
  called it a "buggy HMI" and closed it as false_positive.
- Root cause: verdicts were never defined; the model treated "abnormal but maybe a fault" as
  false_positive. SOC distinction: false positive (activity normal) vs benign true positive
  (abnormal, harmless cause) vs true positive (malicious).
- Fix: verdict definitions in the triage prompt; abnormal activity must be 'uncertain', never
  'false_positive'. Scoring must separate missed attacks (false_positive) from escalations (uncertain).