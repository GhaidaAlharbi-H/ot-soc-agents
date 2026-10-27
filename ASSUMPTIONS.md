# Assumptions

Facts the CIC Modbus 2023 dataset does not provide. Every safety result is conditional on these.

| # | Assumption | Basis | Status |
|---|---|---|---|
| A1 | IP-to-name mapping | Inferred from register maps | RESOLVED by dataset README: .4 IED1A, .8 IED4C, .5 IED1B (bay guess was wrong) |
| A2 | .4 and .8 secure, .5 normal | Traffic to central agent on TCP 1099 | CONFIRMED by dataset README |
| A3 | The normal HMI (.3) is the operators' only view and control path | Only Modbus client in the captures | Assumed |
| A4 | Coils are breaker commands | Common substation practice | Assumed; not stated in the dataset |
| A5 | Criticality: HMIs critical, IEDs high, central agent medium | Team judgement | Assumed |
| A6 | Allowed/forbidden actions per role | OT incident-response guidance (cited in the safety skill, L4) | Assumed |