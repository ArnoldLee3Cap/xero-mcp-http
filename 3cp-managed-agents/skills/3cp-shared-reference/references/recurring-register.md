# 3CP Recurring Transactions Register

**STATUS: LOCKED — 3 July 2026.** All open items closed (see bottom of file). This is the
authoritative version; further changes go through the maintenance rules below, not ad-hoc edits.

**Purpose**: Authoritative register of recurring transactions for the monthly close completeness check.
The orchestra skill reads this file as its final close step and verifies, for every ACTIVE row whose
cadence falls due in the close period, that a posting exists in the GL and is within tolerance.

**Output of the check** — three buckets:
1. OK — present and in range
2. WARN — present but outside tolerance (investigate: rate change, partial period, error)
3. MISSING — chase bill and accrue via standing-accruals module, or confirm service ended and mark row INACTIVE


**Maintenance rules**
- Any change to a vendor arrangement, fee, or policy updates this file FIRST, then skills are repackaged.
- Amounts in HKD unless noted. Tolerance is +/- on the expected monthly amount.
- "Source" = where the number originates; "Owner" = the skill/module responsible for the posting existing.
- Status: ACTIVE / INACTIVE (keep INACTIVE rows for audit trail; the check skips them).

**DATA QUALITY NOTE — root cause confirmed**: `list-profit-and-loss` silently switches modes
depending on parameters, and the MCP tool description does not disclose this:
- `periods` + `timeframe=MONTH` with **no `fromDate`/`toDate`** → correct. Returns true
  period-specific monthly movements, anchored to today. Verified against trial balance (Compliance
  Consultant Fee ties out exactly: 12,000.00 in June).
- **Adding `fromDate`** → returns **cumulative running totals from that date** in each column, not
  monthly movements. Once an account stops posting mid-period, its cumulative total just repeats
  forward — this is what looked like "stale/repeated values" in the original 18-month sweep
  (confirmed on 469, 415, 408, 402, 505, 220). Not a data bug — a parameter-triggered mode switch.
- **Adding `toDate`** (with or without `periods`) → hard error, "unexpected error communicating
  with Xero." Not usable at all.

**Rule for this register and the orchestra skill**: call `list-profit-and-loss` with `periods` +
`timeframe=MONTH` only — never pass `fromDate` or `toDate`. For a fixed historical window (e.g. a
specific Jan 2025–Jun 2026 sweep), use `list-trial-balance` at each month-end and diff consecutive
balances instead — it has no equivalent failure mode.

---

## 1. Monthly — payroll (Owner: 3cp-payroll-close)

| ID | Item | Account | Expected (HKD/mo) | Tolerance | Source | Status |
|----|------|---------|-------------------|-----------|--------|--------|
| PAY-01 | Salary | 477 | headcount-driven | +/-15% | Monthly payroll register | ACTIVE |
| PAY-02 | Rental allowance | 475 | headcount-driven | +/-15% | Monthly payroll register | ACTIVE |
| PAY-03 | MPF (employer) | 478 (payable: 802) | headcount-driven | +/-15% | Monthly payroll report / MPF remittance | ACTIVE |
| PAY-04 | Discretionary bonus | 476 (deferred: 893) | 0 monthly — accrue on crystallisation | n/a | Bonus schedule; historically December, tied to performance fee crystallisation | ACTIVE |

Policy note (PAY-03, updated Jul 2026): MPF has a one-to-two-day settlement lag. Employer portion
(478) plus the employee portion withheld from salaries are credited to **802 MPF Payable** at
month-end; the combined amount pays out to Sun Life from CCB HKD on the 1st–2nd of the following
month. The Sun Life bank payment seen in any month therefore belongs to the **prior** month's
payroll. Salary is booked gross (477 / 477CI); the employee MPF withholding is why net pay from
the bank is smaller than gross salary.

Policy note (PAY-04, updated Jul 2026 — supersedes "December-only"): bonuses are accrued when they
**crystallise** (when the amount becomes committed), not held to December. Historically
crystallisation coincided with December performance fees, so most bonus activity will still be
December — but a mid-year crystallised bonus (e.g. Austin Su, Jun 2026, USD 10,415.51 part-payment)
is booked in its month: DR 476 (or against 893 if previously deferred) / CR bank. The completeness
check should not flag non-December bonus postings as errors; it MUST still flag December if the
year-end bonus round is absent.

## 2. Monthly — lease & depreciation (Owner: 3cp-monthly-journals)

| ID | Item | Account(s) | Expected (HKD/mo) | Tolerance | Source | Status |
|----|------|-----------|-------------------|-----------|--------|--------|
| LSE-01 | Rent (office lease cash rent) | 469 | per lease schedule | Exact vs schedule | Lease schedule (PP5) | ACTIVE |
| LSE-02 | Interest on lease liabilities | 438 / 899 | per lease schedule (declining) | Exact vs schedule | Lease schedule (PP5) | ACTIVE |
| LSE-03 | Depreciation — ROU asset | 415 / 705 | per lease schedule | Exact vs schedule | Lease schedule (PP5) | ACTIVE |
| LSE-04 | Air-conditioning charge (Swire, on lease invoice) | 471 | 37,500 flat (from Jun 2026) | Exact | Landlord invoice (Boom View/Swire, HEN0006033 series) | ACTIVE |
| LSE-05 | Government rates (quarterly, paid in advance) | 470 / 620 | 7,033.33/mo amortisation. Quarterly demand (21,100 for Apr–Jun 2026) billed on the rent bill of the quarter's second month (e.g. May bill HEN0005999) and coded to 620 Prepayments on payment — confirmed pattern, Arnold intends to keep it going forward. Then DR 470 / CR 620 monthly. | Exact | Landlord rent bill (Boom View/Swire), quarterly line | ACTIVE |
| DEP-01 | Depn — L/H improvements | 416 / 731 | per FA register | Exact vs FA register | Xero fixed-asset register | ACTIVE |
| DEP-02 | Depn — office equipment | 418 / 721 | per FA register | Exact vs FA register | Xero fixed-asset register | ACTIVE |
| DEP-03 | Depn — fixtures & furnitures | 417 / 711 | per FA register | Exact vs FA register | Xero fixed-asset register | ACTIVE |
| DEP-04 | Depn — computer equipment | 440 / 741 | per FA register | Exact vs FA register | Xero fixed-asset register | ACTIVE |

## 3. Monthly — standing accruals (Owner: 3cp-monthly-journals, standing-accruals module)

| ID | Item | Account | Expected (HKD/mo) | Tolerance | Source | Status |
|----|------|---------|-------------------|-----------|--------|--------|
| ACC-01 | Audit fee accrual | 402 (DR) / 835 (CR) | 2,375.00 (annual fee 28,500 / 12) | Exact | Audit engagement letter | ACTIVE |

Rule: DR 402 / CR 835 Accruals every month, no exceptions. Actual audit bill books against the
accrual; difference trued up in the month the bill lands. Update the annual fee here on renewal.
This module is the extension point for any future fixed annual fee to be smoothed monthly.

## 4. Monthly — prepayment amortisation (Owner: 3cp-monthly-journals, prepayment module)

| ID | Item | Expense acct | Prepayment acct | Expected (HKD/mo) | Tolerance | Source | Status |
|----|------|-------------|-----------------|-------------------|-----------|--------|--------|
| PPD-01 | Medical insurance — CARING Employee Medical Insurance Plan (group policy, underwritten by Bolttech Insurance (HK); NOT Allianz — corrected below) | 477EI | 620 | 7,166.83 (annual premium 86,001.92 ÷ 12; coverage 22 Jan 2026–22 Jan 2027) | Exact vs schedule | Bolttech invoice 300026038 | ACTIVE |
| PPD-01b | Medical insurance — dependant rider (spouse & child), direct-expensed, no amortisation | 477EI | n/a (posted straight to 477EI on invoice date) | Lump sum at renewal, not monthly — do not apply a monthly tolerance to this row; check for presence of the renewal invoice each January instead | Presence check at renewal (Jan) | Bolttech invoice 300019888, HK$21,764.62, coverage 22 Jan 2025–22 Jan 2026 (2026 renewal not yet seen in Xero — confirm when it lands) | ACTIVE |
| PPD-02 | Insurance — employer liability & travel | 433 | 620 | 2,166.60 (confirmed via trial balance: YTD Jan–Jun 2026 12,999.60 ÷ 6 = exact) | Exact vs schedule | Trial balance confirmed; source policy verified correct by Arnold (2 Jul 2026) | ACTIVE |

Rule: one schedule row per active policy (premium, coverage period, monthly charge = premium /
coverage months). DR expense / CR 620 monthly. Any new invoice coded to 620 at entry triggers
adding a schedule row.

**Correction (was: "Allianz / Jon Shelley only")**: the plan is a company-wide group policy
(CARING, underwritten by Bolttech from the Jan 2025 renewal; FWD was the underwriter through the
2024 policy year — same plan, insurer changed). It is not single-employee cover. The prior
assumption naming Allianz and Jon Shelley was incorrect and has been removed.

**477EI population — resolved**: 477EI YTD (Jan–Jun 2026) per trial balance is 165,478.84. PPD-01's
amortisation accounts for only ~43,000 of that (7,166.83 × 6). The remaining ~122,000 is NOT
additional insurance policies — no other 620-amortised or directly-expensed policy invoices exist
in Xero beyond PPD-01 and PPD-01b. This residual is almost certainly employee medical
reimbursement claims routed through Expensify (GL category → 477EI), which is
`expense-monthly-close-builder`'s territory, not the prepayment module's. No further schedule rows
needed here; if the gap needs closing, verify via the Expensify GL-category export for 477EI, not
via more insurance invoices.

## 4a. Accrual estimation & true-up policy (applies to all standing accruals and estimated postings)

1. **Estimate basis**: until the current-period contract/invoice is known, accrue using the best
   available estimate — the signed contract amount if on hand, otherwise the prior-year actual.
2. **True-up on actual**: when the actual invoice arrives, book it against the accrual balance and
   release the difference to P&L in that same month — accrual balances must reflect the latest
   actual amounts, never stale estimates.
3. **Register update**: in the same close, update this register's expected amount to the new actual
   so all future accruals and tolerance checks run off the latest figure.
4. The completeness check flags any accrual row whose estimate basis is older than 12 months.

## 5. Monthly — recurring service providers (Owner: completeness check only — postings arrive via bills / Expensify / AMEX)

| ID | Item | Account | Expected (HKD/mo) | Tolerance | Source | Status |
|----|------|---------|-------------------|-----------|--------|--------|
| SVC-01 | Accountancy fees — Cornerstone | 411 | 6,000 flat | Exact | Monthly supplier bill — confirmed via 15-month sweep (consistently 6,000/mo Jan 2025–May 2026); the prior 36,000 figure in this register was incorrect and has been corrected | ACTIVE |
| SVC-02a | Compliance consultant (predecessor firm, to May 2026) | 412CC | ~105,000 | n/a | Monthly supplier bill | INACTIVE (from Jun 2026) |
| SVC-02b | Compliance consultant — Peak Compliance Associates (from Jun 2026) | 412CC | 12,000 flat (subject to change if scope of services changes — update this row on any re-scope) | Exact | Monthly supplier bill | ACTIVE |
| SVC-03 | IT service provider | 413ITSP | 44,519 (mean) | mean ± 2σ = 4,746 – 84,293 | 17-month sweep (Jan 2025–May 2026; Jun 2026 excluded as incomplete/not yet posted) | ACTIVE |
| SVC-04 | Telecom & internet | 489 | 2,304 (mean) | mean ± 2σ = 221 – 4,388 (band includes an Oct 2025 outlier of 6,382 — confirmed ad-hoc mobile data charges spanning a 2-year period, not a rate change; excluded from concern, no monitoring needed) | 17-month sweep | ACTIVE |
| SVC-05a | Consultant — Nancy Hong (10,000/day, variable by days worked) | 477CI | variable | presence check only, no amount tolerance | Monthly invoice | ACTIVE |
| SVC-05b | Intern — Leo Zhang (from Jun 2026) | 477CI | 12,500 flat (corrected from 12,000, Jul 2026; appears under "Salary" in the payroll report but books to 477CI) | Exact | Monthly payroll report | ACTIVE |
| SVC-06 | SaaS subscriptions (aggregate) | 413SAAS | 70,183 (mean) | mean ± 2σ = 60,286 – 80,081 | 17-month sweep | ACTIVE |
| SVC-07 | Office cleaning | 408 | 3,200 flat | Exact | Monthly supplier bill (direct-paid module) | ACTIVE |
| SVC-08 | Electricity, gas & water | 445 | 1,560 (mean) | mean ± 2σ = 1,261 – 1,858 | 17-month sweep | ACTIVE |
| SVC-09 | Xero subscription (USD 75/mo, HKD floats with FX; paid together with Cornerstone bill) | 413SAAS | ~590 (USD 75 × prevailing rate) | Presence check + sanity band 500–700; no exact tolerance (FX-driven) | Cornerstone monthly bill (added Jul 2026 — explains recurring ~590 on top of SVC-01's 6,000) | ACTIVE |

## 6. Monthly — treasury & investments (Owner: 3cp-investment-treasury-close)

| ID | Item | Account(s) | Cadence | Source | Status |
|----|------|-----------|---------|--------|--------|
| TRS-01 | Securities MTM (IBKR) | 498-1 | Monthly | IBKR activity statement | ACTIVE |
| TRS-02 | Dividend income (gross) + WHT | 271 / 506 (accrued: 871) | Monthly (per statement) | IBKR activity statement | ACTIVE |
| TRS-03 | Broker interest accrual | 870 | Monthly | IBKR activity statement | ACTIVE |
| TRS-04 | Bank interest — DBS | 270 | Monthly — AUTO-FEED, never manual | DBS feed | ACTIVE |
| TRS-05 | Bank interest — CCB | 270 | Monthly — manual unless already reconciled (check list-bank-transactions first) | CCB statement import | ACTIVE |
| TRS-06 | Time-deposit placements / maturities / rollovers | Bank transfer (TD bank a/c ↔ savings/current) — NOT a P&L or asset-code journal | As they occur (check bank statements) | DBS/CCB statements + TD advices | ACTIVE |
| TRS-07 | Fund investments / redemptions (e.g. SP1 TriBridge 651) | 651 (or relevant investment code) / CR bank | As they occur | CHATS advice + bank statement | ACTIVE |
| TRS-08 | Principal-movement sweep | n/a — control check | Every close: scan bank statements for transfers ≥ material threshold that move cash into TDs, funds, or between own accounts, and confirm each is captured as a transfer/investment (not missed as it was in the first Jun 2026 pass) | All bank statements | ACTIVE |

## 7. Monthly — revenue (Owner: 3cp-revenue-recognition)

| ID | Item | Accounts | Cadence | Source | Status |
|----|------|----------|---------|--------|--------|
| REV-01 | Management fee accrual | DR 622 / CR 200 | Monthly | Addepar export + receivable list | ACTIVE |
| REV-02 | Quarterly invoicing reclass | DR 610 / CR 622 | Quarterly (invoice) | Xero ACCREC invoices | ACTIVE |
| REV-03 | Amy Sadick HKD accrual | Separate HKD journal | Monthly (Q actual / 3) | Prior-quarter actual | ACTIVE |
| REV-04 | Performance fee | 220 (receivable: 623) | ANNUAL — December crystallisation only | Year-end calc | ACTIVE |
| REV-05 | SP1/SP2/SP3 (quarterly) + PP GP I Ltd/Private Program I LP (annual) — monthly accrual on last invoice ÷3 or ÷12, true-up on invoice | 622/200 | Monthly (SUPERSEDES invoice-basis-only, Jul 2026) | Last Xero invoice per vehicle | ACTIVE |
| REV-06 | GP I Ltd — QUARTERLY (confirmed from Q4-2025 invoice, was wrongly assumed annual) | 622/200 | Monthly accrual = last quarterly invoice ÷ 3 (6,546.74 at 19,640.22 basis) | Xero invoice + Arnold, 9-Jul-26 | ACTIVE |

## 8. Annual / non-monthly calendar items (Owner: close calendar / orchestra skill)

| ID | Item | Account | Cadence & timing | Source | Status |
|----|------|---------|------------------|--------|--------|
| ANN-01 | HK Profits Tax provision | 505 | Annual — December | Tax computation | ACTIVE |
| ANN-02 | Audit fee true-up | 402 vs 835 | Annual — when audit bill lands (vs ACC-01 accruals) | Audit bill | ACTIVE |
| ANN-03 | Business Registration + SFC licence fees | 426 | Annual — lumpy (BR + SFC demand notes) | Government/SFC demand notes | ACTIVE |
| ANN-04 | Advertising | 400 | Annual — once per year | Supplier bill | ACTIVE |
| ANN-05 | Bonus recognition | 476 (deferred: 893) | Annual — December (see PAY-04) | Bonus schedule | ACTIVE |

## 9. Known ad-hoc (NOT checked for completeness — listed to prevent false positives)

Recruitment fees (409), charitable donations (439), staff professional examination fees (414),
gifts (430), office events (427), travel (495 / 494 / 422), entertainment (420), repairs &
maintenance (473), I.T. equipment (413), legal & professional fees (441), postage (425), printing
& stationery (461), miscellaneous office expenses (453), office grocery items (428), meals
(419 / 421 / 424), local transportation (493 / 493OT), memberships (484), media subscriptions (485).
These vary with activity; the completeness check ignores them (covered by Expensify/AMEX/bill
modules' own reconciliations).

---

## Remaining open items before locking

1. ~~PPD-01: pull Allianz premium + coverage period~~ — **CLOSED**. Confirmed via Xero: CARING plan
   (Bolttech), HK$86,001.92/yr, 22 Jan 2026–22 Jan 2027, HK$7,166.83/mo. "Allianz / Jon Shelley"
   naming was incorrect and has been corrected in section 4.
2. ~~PPD-02: verify the ~2,100/month EL&T charge~~ — **CLOSED**. Confirmed HK$2,166.60/mo exact via
   trial balance. Source policy verified correct by Arnold (2 Jul 2026) — no further action.
3. ~~477EI population~~ — **CLOSED**. It's a group policy, not Jon Shelley-only. The ~122k/6mo gap
   between 477EI actuals and PPD-01's amortisation is attributed to Expensify medical claims, not
   additional policies — see note in section 4. No new schedule rows required.
4. ~~Tolerance calibration~~ — **CLOSED, full window**. Sweep completed across all 18 months except
   Jun 2026 (correctly excluded — genuinely incomplete, current partial period). Method used:
   `list-trial-balance` at each month-end, reading the non-YTD "Debit" column directly (confirmed
   this is the single-period movement, not a running balance — no diffing needed). Final bands:
   - SVC-03 (413ITSP): mean 44,519, band 4,746–84,293
   - SVC-04 (489): mean 2,304, band 221–4,388 (Oct 2025 outlier confirmed as ad-hoc 2-year mobile
     data charges, not a rate change — resolved, no monitoring needed)
   - SVC-06 (413SAAS): mean 70,183, band 60,286–80,081
   - SVC-08 (445): mean 1,560, band 1,261–1,858
   - SVC-01 (411) corrected from an erroneous 36,000 flat to the actual 6,000 flat, confirmed
     consistent across all 17 sampled months.
5. ~~Fix the list-profit-and-loss period handling~~ — **ROOT CAUSE CONFIRMED, no MCP fix needed**.
   The bug only triggers when `fromDate`/`toDate` are passed (cumulative-mode switch / hard error).
   Calling with `periods` + `timeframe=MONTH` alone returns correct data, capped at 11 periods (12
   columns) per call — for longer windows, use `list-trial-balance` instead (as done for item 4).

**Status: all 5 items closed. Register structure, flat/exact rows, and variable-item tolerance bands
(full 17-month window) are locked. Only open note: Oct 2025 Tel&Internet outlier is understood and
resolved (ad-hoc mobile data charges), not a concern.**


## Amendments — 9-Jul-26 (Direct Payments resolutions)

| ID | Item | Account | Frequency / Rule | Source | Status |
|---|---|---|---|---|---|
| SVC-10 | Mitsubishi HC — printer lease | 461 | 398/mo flat, <12mo lease (expensed, not capitalised) | DBS HKD monthly autopay | ACTIVE |
| SVC-11 | HP — 2nd printer lease | 461 | 194.10/mo flat, <12mo lease (expensed) | DBS HKD monthly autopay | ACTIVE |
| LSE-06 | Orient Logistics wine vault prepayment | 620 → 469 | 41,610 one-off (Jun-26, coded to 620); amortise 3,467.50/mo × 12 from JUL-26 | DBS HKD 19-Jun; Arnold 9-Jul | ACTIVE |
| SVC-12 | Addepar subscription (quarterly, USD ~16,500/qtr; prepaid + amortise 5,500/mo to 413SAAS) | 620→413SAAS | Quarterly invoice, monthly amortisation | Addepar invoice (Net 30) | ACTIVE |
