# Data card: CIC Modbus 2023

## Source
- Canadian Institute for Cybersecurity (UNB): https://unb.ca/cic/datasets/modbus-2023.html
- Cite: Boakye-Boateng, Ghorbani, Habibi Lashkari, "Securing Substations with Trust, Risk Posture
  and Multi-Agent Systems: A Comprehensive Approach," PST 2023.
- Testbed described in: Boakye-Boateng et al., "Implementation of a Trust-Based Framework for
  Substation Defense in the Smart Grid," Smart Cities 7(1), 2024.
- Redistribution allowed with citation.

## What was captured
- Docker-based simulated electrical substation using Modbus/TCP.
- Devices (from folder names): scada-hmi, ied1a, ied1b, ied4c, central-agent.
  The central agent belongs to the authors' trust-based defense system, not a normal substation.
- Two capture types: per-device (one Docker interface each, files named veth*) and
  network-wide / substation-wide (all devices). Files split into ~100 MB chunks.

## Scenarios
| Scenario | Dates | Attacker |
|---|---|---|
| benign | Jan 2023 (chunks 14-32) | none |
| external | Dec 2022 - Feb 2023 | outside device |
| compromised-scada | 12-22 Mar 2023 | the SCADA HMI |
| compromised-ied | 23-29 Mar 2023 | IED1B |

## Attack logs
- CSV per day: Timestamp, TargetIP, Attack, TransactionID. Timestamps to the millisecond,
  no time zone written (page states UTC).
- Each attack has a "Complete" marker row (TransactionID 65535); marker text varies
  ("- Complete", ". Complete").
- Attack type and parameter share one field (e.g. "Brute force or specific coil. Address: 13").
- Transaction IDs repeat; matching to packets needs time + target IP + transaction ID.
- Records are not packets: brute force logs one row per write, a flood logs one row per flood.

## Coverage checked (UTC)
| File | Start | End | Packets |
|---|---|---|---|
| compromised-scada substation-0.pcap | 23 Mar 02:12 | 23 Mar 02:15 | 164 |
| compromised-scada substation-1.pcap | 15 Mar 08:53 | 15 Mar 19:02 | 1.12 M |
| benign network-wide-normal-32.pcap | 31 Jan 11:46 | 31 Jan 16:29 | 537 k |

## Known limitations
1. substation-0.pcap holds only the last 4 minutes of the capture; the original first file
   was likely overwritten on restart.
2. The substation-wide capture starts 15 Mar 08:53 UTC, but compromised-scada logs start
   12 Mar: attacks logged on 12-14 Mar have no matching substation-wide traffic.
3. Benign chunks 0-13 are not in the published zip.
4. The 21 Mar log exists as an Excel-modified .xlsx and an original .csv; use the original.
5. On 15 Mar, 3 query floods have no "Complete" marker.
6. Not every attack type appears every day (15 Mar has no false data injection or delayed response).
7. The page says PCAP times are UTC-3, but PCAP files store UTC epoch time; the offset must
   be verified against the logs.
8. Mostly network traffic; few process values (voltages, breaker states) are visible.

## Open questions
- Why do external/network-wide files carry "normal" in their names?
- Full time coverage of every PCAP: checked in L7, phase 7.0.
## Devices (dataset README)
| IP | Device |
|---|---|
| 185.175.0.2 | Secure SCADA HMI (not seen in benign or compromised-scada captures) |
| 185.175.0.3 | Normal SCADA HMI (the only Modbus client) |
| 185.175.0.4 | IED1A, secure |
| 185.175.0.8 | IED4C, secure |
| 185.175.0.5 | IED1B, normal (attacker in compromised-ied) |
| 185.175.0.6 | Central Agent (TCP 1099 to .4 and .8) |
| 185.175.0.7 | Attacker (external scenario) |

## Verified in L1
- Time: PCAPs and logs are both UTC. 19,409 of 19,409 coil-write log rows matched packets at zero offset (none at +/-3 h). Packets precede log rows by ~39 ms. This replaces limitation 7.
- Matching rule: target IP + transaction ID + coil address, within 1 s.
- Normal traffic: HMI polls each IED every ~5.09 s (FC1 x2, FC2, FC3, FC4, one value each); occasional normal FC5/FC6 writes; no exceptions.
- ~80% of packets are TCP control with no Modbus payload.
- compromised-scada attacks all come from the real HMI IP (.3).
- Brute-force coil writes trigger exception code 3 (illegal data value); recon triggers code 2 (illegal address).
- Packets with more than one Modbus message include normal TCP merging, so they are not all stacked-frames attacks.

## Testbed diagram (docs/dataset_setup.png)
- Three planes: Modbus (control traffic), ACL (trust IEDs send trust scores to the Central Agent), ELK (logs to an ELK stack).
- Shows 5 IEDs (4 trust, 1 normal), a Trust SCADA and a normal SCADA. Captures and README show only 3 IEDs: open question.
- No ELK traffic appears in the captures analyzed; likely a separate network not recorded.
- Only the normal SCADA (.3) is active in the captured periods; the Trust SCADA (.2) never appears.

## Attack logs across scenarios (L1, phase 1.3)
- 9 attack types (README list); compromised-scada and external share one log format and set of attacks; compromised-ied adds false data injection, delay response and baseline replay.
- compromised-ied: every attack targets 185.175.0.2 (Trust SCADA HMI), from the compromised IED1B: server-side attacks on responses.
- Log formats differ: external has only Timestamp and Attack (no TargetIP); compromised-ied uses "Starting ..." and ".. Complete" markers. The L7 parser must handle all three.
- external is thin: almost all records are on 1 Feb 2023 (131k rows, mostly brute force); other days have 1-10 rows.
- Packet fingerprints (15 Mar): payload injection = valid frame + 5 extra bytes; length manipulation = header length 27 vs 12 bytes sent; frame stacking = 5 requests in one 60-byte packet.
- Attack-to-ATT&CK v20.0 mapping: mcp_servers/attack_map.csv
