# 3 Capital Partners — Authoritative GL Account Codes
# Source of truth for all skill reference files. Update here first.
# Last verified: July 2026 (live Xero chart confirmed via list-accounts; 475/477 swap corrected, 478 added).
# Any skill referencing GL codes MUST cite this file — do not maintain separate copies.

## Revenue (200s)
| Code | Account Name | Notes |
|---|---|---|
| 200 | Revenue — Management Fees | CR on monthly accrual (DR 622 / CR 200) |
| 220 | Revenue — Performance Fee | CR on Dec crystallisation only; never accrued mid-year |
| 260 | Other Income | |
| 261 | Unrealised P&L (IBKR) — Exchange | FX component via Xero; do not manually revalue |
| 270 | Interest Income (Bank) | Bank + IBKR broker interest |
| 271 | Dividend Income (IBKR) | Always book gross; separate WHT entry to 506 |
| 498-1 | Unrealised P&L (IBKR) | MTM P&L on securities portfolio (DR/CR 872 ↔ 498-1) |
| 507 | Financial Assets at FV through P&L (TB) | |

## Current Assets / Receivables (600s)
| Code | Account Name | Notes |
|---|---|---|
| 610 | Trade Receivables (Accounts Receivable) | Billed/invoiced — Xero system AR; DR when invoice raised |
| 620 | Prepayments | Annual subscriptions, insurance premiums etc. |
| 622 | Management Fee Receivables | **Accrued, not yet invoiced.** DR monthly (DR 622 / CR 200). CR on invoice (DR 610 / CR 622). |
| 623 | Performance Fee Receivables | New account (2026). DR on perf fee invoicing (DR 623 / CR 220). Do NOT confuse with 624. |
| 624 | Employee Receivables | Renamed from 623 (2026). Non-reimbursable staff charges. |
| 625 | Rental & Utility Deposits | |
| 640 | Amount due from Interactive Brokers | Cash + interest/dividend accruals held at IBKR |
| 651 | Investment in SP1 (TriBridge Funds SPC – Sustainable) | **Added July 2026.** Fund investment carried at fair value; revalued at YEAR-END ONLY (no monthly MTM). DR 651 / CR DBS USD on funding. Distinct from the TriBridge revenue carve-out — 3CP both invests in and earns fees from TriBridge vehicles; do not conflate. |
| 664 | Private Equity Program Expense Receivables | PEP expense fronted by 3CP, reimbursed by PEP fund |

## AMEX / Expense Clearing
| Code | Account Name | Notes |
|---|---|---|
| 135 | AMEX Clearing Account | HKD; clears when AMEX statement is paid |
| 801 | Unpaid Expense Claims | Expensify approved, not yet paid |
| 855 | AMEX Suspense | P-card late submissions; reverses out of 855 (not current-period clearing) |
| 6990 | AMEX Suspense (operating) | Transitional suspense plug — clear monthly |

## Fixed Assets (700s)
| Code | Account Name | Notes |
|---|---|---|
| 700 | Asset Right-of-Use (cost) | HKFRS 16 ROU asset |
| 705 | Accumulated Depreciation — ROU | Contra to 700 |
| 710 | Furniture & Fixtures (cost) | |
| 711 | Accumulated Depreciation — F&F | |
| 720 | Office Equipment (cost) | |
| 721 | Accumulated Depreciation — Office Equipment | |
| 730 | Leasehold Improvements (cost) | |
| 731 | Accumulated Depreciation — L/H Improvements | |
| 740 | Computer Equipment (cost) | |
| 741 | Accumulated Depreciation — Computer Equipment | |

## Depreciation Expense (P&L) by asset class
**Added July 2026** — found missing during the June close Demo posting test; the June workpaper
had been using these codes for months, but they were never captured here. Each pairs with its
BS contra account above (e.g. 417 depreciation expense clears to 711 accumulated depreciation).
| Code | Account Name | Notes |
|---|---|---|
| 415 | Depreciation — Right of Use Asset | HKFRS 16; DR monthly (DR 415 / CR 705) |
| 416 | Depreciation — Leasehold Improvements | Pairs with 731 |
| 417 | Depreciation — Furniture & Fixtures | Pairs with 711 |
| 418 | Depreciation — Office Equipment | Pairs with 721 |
| 440 | Depreciation — Computer Equipment | Pairs with 741 |

## IBKR / Treasury Investment Accounts (800s–870s)
| Code | Account Name | Notes |
|---|---|---|
| 870 | Interest Accrual (IBKR) | Accrued interest receivable at IBKR |
| 871 | Dividend Accrual (IBKR) | Accrued dividend receivable (gross) at IBKR |
| 872 | Financial Assets at FV through P&L | Securities portfolio at fair value; paired with 498-1 |

## Expenses (400s–500s) — Key Codes
| Code | Account Name | Notes |
|---|---|---|
| 402 | Audit Fee | |
| 404 | Bank Fees | |
| 405 | Commission (IBKR) | |
| 411 | Accountancy Fees & Expenses | |
| 412 | Consultation Services | |
| 412CC | Compliance Consultant | |
| 413 | IT Equipment | |
| 413ITSP | IT Service Provider | |
| 413SAAS | SaaS Subscriptions | |
| 419 | Meal (Business Associate) | **Added July 2026** — Expensify category, found missing during Demo posting test |
| 420 | Entertainment | **Added July 2026** — Expensify category |
| 421 | Meal (OT) | **Added July 2026** — Expensify category |
| 422 | Meal (Business Trip) | **Added July 2026** — Expensify category |
| 424 | Meal (Colleagues) | **Added July 2026** — Expensify category |
| 427 | Office Events | **Added July 2026** — Expensify category |
| 428 | Office Grocery | **Added July 2026** — Expensify category |
| 430 | Gifts | **Added July 2026** — Expensify category |
| 475 | Salary - Rental Allowance | **Corrected July 2026** — previously mislabelled "Salary" in this file. Confirmed via live chart-of-accounts export used by 3 other skills. |
| 477 | Salary | **Corrected July 2026** — previously mislabelled "Rental Allowance / Bonus" in this file. Confirmed via live chart-of-accounts export. |
| 477CI | Consultants & Interns | |
| 477EI | Employee Insurance | Includes Allianz D&O/PI; Bolttech medical |
| 478 | Mandatory Provident Fund (MPF) | **Added July 2026** — was missing from this file entirely; live code confirmed via chart-of-accounts export and cross-checked with Arnold. |
| 479 | Staff Welfare - Other | **Added July 2026** — Expensify category, found missing during Demo posting test |
| 485 | Media Subscriptions | **Added July 2026** — Expensify category |
| 433 | Insurance | Straight-line amortisation from 620 (DR 433 / CR 620) |
| 437 | Interest Expense | |
| 438 | Interest on Lease Liabilities | HKFRS 16; DR monthly (DR 438 / CR 899) |
| 441 | Legal & Professional Fees | |
| 445 | Electricity, Gas & Water | |
| 468 | Building Management Fee | |
| 469 | Rent | Full landlord invoice posts here; lease reclass moves base rent to 899. After reclass, 469 should net to ~zero — A/C charge goes to 471, rates to 470 |
| 470 | Government Rates | **Added July 2026** (Arnold created in Xero) — quarterly/monthly government rates on the office (e.g. 7,033.33 Jun 2026, Boom View/Swire invoice) |
| 471 | Air-Conditioning Charges | **Added July 2026** (Arnold created in Xero) — monthly Swire A/C charge on the office lease invoice (37,500/mo from Jun 2026); service component, kept out of 469 and the lease liability |
| 476 | Recruitment Fees | |
| 489 | Tel & Internet | |
| 493 | Transport — Local | |
| 493OT | Transport — Local (OT) | **Added July 2026** — Expensify category, found missing during Demo posting test |
| 494 | Transport — Overseas | |
| 495 | Travel Accommodation | |
| 505 | HK Profits Tax | |
| 506 | Withholding Tax (IBKR) | Always DR when dividend WHT is deducted |

## Liabilities (800s–900s)
| Code | Account Name | Notes |
|---|---|---|
| 800 | Accounts Payable | |
| 802 | MPF Payable | **Added July 2026** (Arnold created in Xero) — month-end MPF owed to Sun Life (employee withheld + employer portion); settles 1st–2nd of following month |
| 803 | Wages Payable | |
| 830 | Income Tax Payable | |
| 835 | Accruals | Year-end bonus, unpaid expenses |
| 850 | Suspense | |
| 880 | Expenses to be Reimbursed | |
| 893 | Deferred Bonus | |
| 899 | Lease Liability | HKFRS 16; DR principal portion (DR 899 / CR 469 net) |

## Policy Notes (standing)
- **622 vs 623:** 622 = management fee accrued/unbilled (cleared by quarterly invoice coded to 622). 623 = performance fee invoiced (Dec only). Never use 623 for management fees.
- **624 ≠ 623:** 624 is employee receivables (renamed from 623 in 2026). Any skill file referencing "623 = Employee Receivables" is stale.
- **Dividends always gross:** book full gross to 271/871; separate DR 506 for WHT. Never net.
- **DBS auto-feed:** DBS bank interest posts automatically — never prepare a manual 270 entry for DBS. CCB has no auto-feed; check via list-bank-transactions before booking CCB interest.
- **Time deposits are BANK ACCOUNTS in Xero, not asset codes** (confirmed Jul 2026 from CCB – Time Deposit 2 ledger). Placements, maturities and rollovers are booked as **bank transfers between the TD account and the source savings/current account**, never as manual journals to an investment code. **Posting route (Jul 2026): same-currency transfer legs can be posted via the xero-3cp `create-bank-transfer` tool (posts live/AUTHORISED, verify via `list-bank-transfers`); cross-currency legs remain a Xero UI step — the Xero API rejects multi-currency bank transfers.** Each monthly cycle has three legs: MA (maturity — principal returns), IS (interest credited), ST (new placement). Interest (IS) still needs recognising to income (270); principal legs (MA/ST) are transfers only, no P&L. TD accounts (e.g. "CCB – Time Deposit 1/2") have no auto-feed — generate the statement-import lines. A DBS-side TD placement (e.g. "Dr. Tran for funding A/c …600019") is the same: a transfer DBS USD → the TD bank account.
- **FX conversions between own accounts are single cross-currency TRANSFERS** (confirmed Jul 2026 from a DBS USD→HKD example, ref 1513RF4409260: USD 205,000 → HKD 1,602,278.57 as one Xero Transfer at 1 HKD = 0.127943 USD). Book as one transfer between the USD and HKD bank accounts — Xero records the rate and computes FX gain/loss itself. **This is a Xero UI step only: the API (and therefore the xero-3cp `create-bank-transfer` tool) does not support cross-currency transfers.** No FX-clearing account, no manual translation. "FX MARKET - MAB" (USD out) pairs with "FX MARKET - MAS" (HKD in) as the two sides of one transfer.
- **TaxRate:** Sales invoices (ACCREC, client management-fee invoices) use **`OUTPUT`** — confirmed from actual posted Q1 2026 invoices (INV-0603, INV-0604, INV-0609). Manual journals use the **"Tax Exempt" rate, whose API code in the 3CP org is `NONE`** (verified via list-tax-rates, July 2026). Posted 2026 journals (lease, FX) showing TaxType `NONE` are therefore CORRECT — `NONE` is not a missing tax rate, it IS Tax Exempt. RESOLVED July 2026; decision: no historical changes, `taxType: "NONE"` + `lineAmountTypes: "NO_TAX"` going forward.
- **taxType API field:** use code value (e.g. "NONE", "OUTPUT") not display label.
- **SP / TriBridge / "3 Capital Partners" vehicles:** invoice-basis recognition only — no 622 accrual. Standing open item: move to accrual basis in future.
- **Payroll bank routing (475/477/478/802):** Salary and rental allowance pay out of **DBS HKD** on/around month-end (net of employee MPF withheld). MPF — employer portion (478) **plus** employee portion withheld from salaries — is credited to **802 MPF Payable** at month-end and settles to Sun Life from **CCB HKD** on the 1st–2nd of the following month (confirmed Jul 2026; the routing may migrate to DBS in future). DBS is auto-fed (journal only, never import a statement); CCB has no feed (journal plus CCB statement-import CSV, same pattern as `3cp-investment-treasury-close`).

- **AMEX convention (decided 9-Jul-26):** clearing + unsubmitted-suspense model is the go-forward
  treatment; the historical per-card AMEX bank-account model (Expensify Spend Money per card, per-card
  payment transfers, no suspense) is DEPRECATED. One-time migration required: reclass card balances
  into suspense, reconfigure/disable Expensify auto-posting, archive card accounts (poster checklist §F).
- **Entity due-from accounts:** 657 general PEP (Expensify-tagged, vehicle unknown) | 658 SMA-II LP |
  659 PEP SMA LP | 660 3CP Holdings Ltd | 663 PP II LP | 665 SMA GP III Ltd | 666 SMA-III LP |
  667 SMA GP II Ltd. Invoices naming a vehicle → direct entity account; Expensify PEP tag → 657.
