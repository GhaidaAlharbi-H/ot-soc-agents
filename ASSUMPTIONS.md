# Assumptions

Facts the CIC Modbus 2023 dataset does not provide. Every safety result is conditional on these.

| # | Assumption | Basis | Status |
|---|---|---|---|
| A1 | IP-to-name mapping | Inferred from register maps | RESOLVED by dataset README: .4 IED1A, .8 IED4C, .5 IED1B (bay guess was wrong) |
| A2 | .4 and .8 secure, .5 normal | Traffic to central agent on TCP 1099 | CONFIRMED by dataset README and setup diagram |
| A3 | The normal HMI (.3) is the operators' control path; isolating it removes operator control | Only active HMI in the captured periods. The setup diagram also shows a Trust SCADA (.2), which never appears in the captures | Assumed; weaker basis since the diagram |
| A4 | Coils are breaker commands | Common substation practice | Assumed; not stated in the dataset |
| A5 | Criticality: HMIs critical, IEDs high, central agent medium | Team judgement | Assumed |
| A6 | Allowed/forbidden actions per role | OT incident-response guidance (cited in the safety skill, L4) | Assumed |
| A7 | The system models only the 3 IEDs seen in traffic | The setup diagram shows 5 IEDs; captures and README show 3 | Assumed; open question |