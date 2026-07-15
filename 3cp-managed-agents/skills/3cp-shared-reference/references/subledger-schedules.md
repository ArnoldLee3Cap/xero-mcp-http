# Subledger Schedules (rolled forward every close — the memory between months)

These schedules persist the balance-sheet detail that each month's close needs from the prior
month. UPDATE THIS FILE AT EVERY CLOSE and repackage the skill — a schedule left inside a
workpaper dies with it. The control-account tie-out (orchestrator Mode 2) checks Xero balances
against THESE schedules. State below = close of June 2026 (pipeline test basis; updated 9-Jul with
Arnold's Direct Payments resolutions).

## 620 Prepayments
| Item | Coverage | Monthly | Booked | Amortised to date | Balance 30-Jun-26 |
|---|---|---|---|---|---|
| Government rates (LSE-05) | Quarterly, billed on quarter's 2nd-month rent bill | 7,033.33 | 21,100/qtr | Apr–Jun cycle complete | 0 (new 21,600−500 cycle billed on HEN0006067 for Jul–Sep) |
| Adobe annual ×4 | May-26 → Apr-27 | 752.00 | 9,024.00 | 1,504.00 (May–Jun) | 7,520.00 |
| Allianz JS insurance | 27-Jan-26 → 26-Jan-27 | 2,518.33 | 30,220.00 | 15,110.00 (Jan–Jun) | 15,110.00 (Jul–Dec) |
| Orient Logistics wine vault | Jul-26 → Jun-27 | 3,467.50 | 41,610.00 (booked to 620, Jun-26) | 0 (coverage not started) | 41,610.00 — amortise to **469 Rent** from JULY, 3,467.50/mo × 12 |
| Addepar subscription (USD) | 14-May-26 → 13-Aug-26 | 5,500.00 | 16,500.00 | 8,250.00 (half-May + Jun) | 8,250.00 (Jul + half-Aug) — expense to 413SAAS |
Expected 620 balance: HKD 7,520 + 15,110 + 41,610 = 64,240.00 plus USD 8,250 (Addepar) (+ any rates cycle in progress).
Policy: HK$5,000/item floor; below → expense immediately (LexisNexis 1,992 expensed under this rule, Jun-26).

## Fixed-asset additions awaiting Xero register entry
| Asset | Cost | Purchase | Rate | Monthly | Accum. to Jun-26 |
|---|---|---|---|---|---|
| Apple Mac Mini (J. Shelley) | 13,599 | Apr-26 | 25% SL | 283.31 | 849.94 |
| Lenovo ThinkPad x13 G6 | 16,990 | Apr-26 | 25% SL | 353.96 | 1,061.88 |
| Lenovo X1 G14 (Alex, incl. 500 deposit) | 20,590 | May-26 | 25% SL | 428.96 | 857.92 |
Add to Xero FA register (manual); from July these depreciate inside the normal register run.

## AMEX Clearing roll-forward
| Month | Opening | + Statement charges | − Autopay (~19th, clears PRIOR month) | Closing |
|---|---|---|---|---|
| Jun-26 | 28,593.44 (May stmts) | 115,331.49 | (28,593.44) 19-Jun | 115,331.49 → settles ~19-Jul |
Rule: closing balance must equal the CURRENT month's statement total exactly.

## AMEX Unsubmitted Suspense composition
| Movement | Amount |
|---|---|
| Opening — to be SEEDED by the one-time migration reclass of the per-card AMEX account balances (see poster checklist §F); until then unknown | TBD |
| + June-statement charges not yet through approval gate | 100,734.01 |
| − Releases: prior-stmt items now recognised (Part B) | (28,677.84) |
| − Releases: Mac Mini capitalised | (13,599.00) |
| − Releases: Adobe/Zoom/Litera | (13,612.03) |
| Net June movement | +44,845.14 |
Rule: suspense must never go negative; releases must exist in opening composition.

## 622 accrual vs invoice true-up ledger (USD)
| Stream | Frequency | Jun-26 monthly accrual | Cumulative since last invoice | Next true-up |
|---|---|---|---|---|
| Addepar clients | Monthly | 241,066.95 | per client (Addepar exports) | Q2 invoices |
| SP1 / SP2 / SP3 | Quarterly | 58,904.58 / 10,231.15 / 5,861.82 | 1 month each | Q2 invoices |
| PP GP I Ltd | Annual | 29,845.00 | 1 month | annual invoice |
| **GP I Ltd** | **QUARTERLY (corrected 9-Jul — Q4-25 invoice confirms)** | **6,546.74** (was 1,414.91 on wrong ÷12 basis) | 1 month | next quarterly invoice |
| Private Program I LP | Annual | 14,097.52 | 1 month | annual invoice |
Rule at invoicing: recognise (invoice − cumulative accrual) difference in the invoice month.
Confirmed 9-Jul-26 (GP I Ltd Q4-2025 receipt, INV GP1_20251231): management-fee true-up 2,661.34
(19,640.22 actual vs 16,978.88 estimate) recognised in June 2026; performance fee 36,015.21 booked
entirely in 2026 (no 2025 accrual, per prudence policy — correct as applied).

## Short-term liabilities expected states
| Acct | Expected after each close | Jun-26 |
|---|---|---|
| 802 MPF Payable | current month's MPF only (prior settled 1st–2nd) | 31,341.67 |
| 835 Accruals | current accruals only (prior auto-reversed) | 40,233.39 (IT) |


## Entity-specific due-from accounts (confirmed 9-Jul-26)
Invoices that NAME a specific vehicle route to that vehicle's due-from account; Expensify
PEP-tagged costs (vehicle unknown at submission) stay in general 657 until allocated.
| Acct | Entity |
|---|---|
| 657 | General PEP receivable (Expensify-tagged, unallocated) |
| 658 | 3 Capital Partners PEP SMA-II LP |
| 659 | 3 Capital Partners PEP SMA LP |
| 660 | 3 Capital Partners Holdings Ltd (parent) |
| 663 | 3 Capital Partners Private Program II LP |
| 666 | 3 Capital Partners PEP SMA-III LP |
| 667 | 3 Capital Partners PEP SMA GP II Ltd |
| 665 | 3 Capital Partners PEP SMA GP III Ltd (confirmed 9-Jul) |
