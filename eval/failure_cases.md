# Failure cases

## FC-1: Brute-force writes judged false positive (L2.3, 13 Nov 2026)
- Alert: 15,302 FC5 writes .3 -> .4 in 10 h, mostly coil 1, 8,528 exception code 3.
- Verdict: false_positive, low, confidence 0.9 (truth: real_attack, T0806 Brute Force I/O).
- Causes: looked up only .3 (ignored "look up every device"); treated rejected writes as harmless
  (~6,774 writes were not rejected); used the prompt rule "normal includes occasional writes"
  without a number (normal is ~20 writes per IED per 4.7 h).
- Fix planned: baseline tool with L1 numbers, check that every alert IP was looked up,
  quantitative prompt rule; later ATT&CK lookup (L3) and investigation skill (L4).