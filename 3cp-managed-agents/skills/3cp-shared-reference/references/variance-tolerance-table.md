# Variance Tolerance Table (feeds the orchestrator's Variance Flag)

Defined bands per account, set once and reused every close — not improvised monthly. A flag fires
when an account's month-on-month movement breaches its band. "Basis" records why the band is what
it is, so it can be revisited deliberately rather than drifting by habit.

## Fixed/contractual — near-zero tolerance
| Account | Band | Basis |
|---|---|---|
| 411 Accountancy (Cornerstone) | ±0% | Fixed HK$36,000/month contract |
| 412CC Compliance (Peak) | ±0% | Fixed HK$12,000/month contract |
| 402 Audit fee | ±0% | HK$28,500/year ÷ 12 = 2,375.00 |
| 461 Printing & Stationery (printer leases) | ±0% for the lease lines; small variance ok for ad-hoc printing | Mitsubishi 398 + HP 194.10 fixed monthly leases (<12mo, expensed) |
| 469/470/471 Rent, rates, A/C | ±0% within a quarter's rate | Fixed lease schedule (PP5); changes only at rent review or rates re-bill. From Jul-26 also carries wine-vault amortisation 3,467.50/mo |
| 477 Salary | Flag if any change | Headcount changes are known events (new hire, leaver, RA change) — should never move silently |
| 802 MPF Payable | Tied to salary + statutory rate | Moves in lockstep with 477/475 |

## Variable but bounded — confirmed bands (existing)
| Account | Band | Basis |
|---|---|---|
| 413ITSP IT Service Provider | 4,746 – 84,293 | Historical range, confirmed prior sessions |
| 489 Tel & Internet | 221 – 4,388 | Historical range |
| 413SAAS SaaS Subscriptions | 60,286 – 80,081 | Historical range |
| Electricity (direct) | 1,261 – 1,858 | Historical range |

## Judgement-required — flag for review, no hard band
| Account | Rule | Basis |
|---|---|---|
| 420 Entertainment | Flag if >HK$20,000 in a month OR >2× trailing 3-month average | No natural ceiling; June 2026 hit 54,309.56 with no prior baseline — flagged, unresolved |
| 479 Staff Welfare - Other | Flag if >HK$15,000 | Ad hoc by nature |
| 476 Bonus | Flag on ANY occurrence outside December | Crystallisation events, not routine — always investigate context (June 2026 Austin Su case) |
| 622 / 200 Revenue | Flag if >10% variance from Addepar AUM-implied expectation | New vehicles or AUM swings should have an external explanation |
| 220 Performance fee income | Flag on ANY occurrence | Not accrued/routine — only recognised on crystallisation/invoicing (e.g. GP I Ltd 36,015.21, Jun-26) |
| MTM (498-1) | No flag — market-driven, expected to vary | Never treat as an error; sanity-check sign vs. market direction only |

## Application rule
Bands apply to the CURRENT month's balance vs. the SAME account last month, using the
control-account tie-out figures where available (not sheet totals) so the comparison is apples-to-
apples. Update this table when a contract changes (new rent review, new headcount baseline) —
changing a band is a deliberate edit here, never a silent adjustment inside a single month's
variance tab.
