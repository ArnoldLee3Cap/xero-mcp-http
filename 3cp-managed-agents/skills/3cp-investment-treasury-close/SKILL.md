---
name: 3cp-investment-treasury-close
description: Prepare 3 Capital Partners' month-end BANK and BROKER (securities) treasury close as DRAFT entries in USD (reconciliation + broker valuation/income journal). Use whenever the user is doing the monthly close and provides bank statements (DBS / CCB, HKD and USD), time-deposit advices, or an Interactive Brokers (IBKR) activity statement, and wants cash/broker balances reconciled and investment valuation/income journals prepared. Triggers include treasury close, reconcile the bank accounts, IBKR / Interactive Brokers statement, mark-to-market the portfolio, book the unrealised P&L / dividends / broker interest, securities valuation, or month-end tasks on the firm cash, time deposits, or proprietary investment account. Prepares USD entries (Xero applies FX on posting); shows indicative HKD at 7.80. Does NOT compute FX translation, revaluation, or realised FX (Xero owns these), and does NOT post to Xero (preparation only). Do NOT use for Expensify, lease, depreciation, prepayments, or supplier-invoice expenses.
---

# 3CP Investment & Treasury Close (preparation)

> **Important**: Preparation only; not financial advice. Every entry is a DRAFT for a qualified accountant to review and approve in Xero before it is final.

> **Precondition — orchestrator gate**: Before preparing treasury journals for a period, check
> whether `3cp-close-orchestrator` (Mode 1) has been run for that period this session. If it
> hasn't, say so and offer to run it first. If the user explicitly says to skip it and proceed
> anyway, proceed — this is a workflow recommendation, not a hard block.

Reconcile the firm's bank, time-deposit, and Interactive Brokers (IBKR) balances to source statements, and prepare the month-end **broker valuation & income journal in USD**. This skill prepares; it does not post (a separate posting skill pushes drafts to Xero) and it does not compute FX (Xero's multicurrency engine owns translation, revaluation, and realised FX).

## Scope — what this skill does and does NOT do

**Prepares (USD draft entries, from the IBKR statement):**
- Securities mark-to-market — the period unrealised P&L movement.
- Broker interest income (accrued).
- Dividends, withholding tax, commissions, and realised securities P&L **when they arise** (nil months are stated as nil).

**Reconciles (in original currency, no entry needed):**
- Each bank account and time deposit → its statement.
- IBKR NAV → statement (cash + securities at MV + interest accruals).

**Explicitly OUT of scope — owned by Xero's multicurrency engine:**
- FX translation of foreign-currency transactions (Xero books each at its daily rate).
- Period-end revaluation of foreign-currency balances (Xero's "Bank Revaluations" / unrealised currency lines).
- Realised FX on conversions/settlements (Xero computes from its lot subledger).
- **The skill never fetches a live FX rate.** See the FX boundary below.

## The FX boundary (read before building)

The firm's books (Xero) carry foreign-currency balances on **spot, dated lots** (XE.com month-end rate; April 2026 ≈ 7.833859) — confirmed from the Xero export, not a fixed rate. Therefore:

1. **Post/prepare entries in USD.** Xero applies the rate on posting, so the cash/bank/broker FX is handled by the platform — the skill needs no rate for the actual entries.
2. **HKD is shown only as an indicative reference at 7.80.** Every HKD figure on the workpaper is labelled "indicative @ 7.80 — not posted; Xero applies spot." It is a sanity-check column for materiality, never the booked amount, and never part of the posting payload. Because it never touches the GL, its difference from Xero's spot is immaterial by design.
3. **No live rate fetching, ever.** Rates are inputs from the system of record (statement advices for conversions; Xero for booked rates), recovered from documents — never scraped. If a rate is genuinely needed for a reconciliation reference, read it from the Xero export (HKD ÷ original-currency on any line) rather than sourcing it externally.

## Usage

```
/3cp-investment-treasury-close <period> [--bank --broker]
```

- `period` — accounting period (e.g. `2026-04`); period end is the last calendar day.
- module flags *(optional)* — run only the named module; default is every module for which a source document is supplied.

### Modules

| Flag | Module | Produces |
|---|---|---|
| `--bank` | Bank & cash reconciliation | Reconciliation to statements; time-deposit interest accrual (USD) if applicable |
| `--broker` | IBKR valuation & income | USD draft journal: MTM, interest, dividends/WHT/commissions/realised P&L when they arise |

Read the relevant reference before building: `references/bank-cash.md`, `references/broker-valuation.md`.

## Posting boundary (handoff to the future posting skill)

This skill **prepares**; it does not post. Structure the journal output so the separate posting skill can push it to Xero cleanly:
- **USD amounts only** (no HKD in the payload), against the correct multicurrency accounts.
- **Unique reference per journal**, e.g. `3CP-TRES-2026-04-MTM`, `-INT`, so re-runs are idempotent.
- **Draft status** — never auto-approved; a human approves in Xero.
- The posting skill (not this one) owns the Xero API/MCP connection and authorization.

### Fund investments / redemptions (TRS-07) and the principal sweep (TRS-08) — added Jul 2026

- **Fund subscription** (e.g. SP1 TriBridge 651 top-up): a **SPEND bank transaction** from the
  paying bank account — DR the investment code (651 or the relevant 65x) for the subscription
  amount; any wire fee (CHGS / BK CHG lines) goes to 404 on the same transaction. Reference
  `INV-<vehicle>-<period>`. Not a transfer (the counterparty is the fund, not an own account) and
  not a manual journal (it must reconcile against the bank statement line). **Redemption** is the
  mirror RECEIVE: CR the investment code; realised gain/loss handling is a year-end valuation
  matter, not this entry.
- **Time-deposit interest legs** (e.g. CCB "MM DEPOSIT - IS"): RECEIVE bank transaction, CR 270 —
  do NOT fold interest into the principal transfer; principal (MA/ST legs) is a bank transfer,
  interest is income. Jun-26 lesson: the IS leg (USD 834.17) was missed while the MA/ST transfers
  were posted.
- **Principal-movement sweep (TRS-08), every close**: scan ALL bank statements for movements ≥
  material threshold into TDs, funds, or between own accounts, and confirm each is captured as a
  transfer (same-currency → `create-bank-transfer`), an investment SPEND/RECEIVE (this section),
  or a Xero-UI cross-currency transfer. This sweep exists because the first Jun-26 pass missed
  exactly these.

### Inter-account transfers (own accounts) — added Jul 2026

The poster now exposes **`create-bank-transfer`** for movements between two of the firm's own bank accounts. When the statements show such a movement (e.g. funding or maturing a time deposit, DBS savings → DBS current, a same-bank sweep):

- **Same currency** (HKD→HKD, USD→USD): prepare it as a **bank-transfer instruction**, not a manual journal and not a Spend/Receive pair — one movement, one object. Payload fields: from-account, to-account, amount (in that currency), date, and a unique reference (`TFR-<from>-<to>-<period>`, e.g. `TFR-DBS-TD-JUN26`). Note on the workpaper that the transfer will post **live (AUTHORISED)** — no draft state — and reconciles as a transfer-out line and a transfer-in line on the two statements.
- **Cross-currency** (e.g. DBS HKD → Business Savings USD conversion): **Xero's API does not support cross-currency transfers.** List these on the workpaper as a **manual Xero UI step** for the user (Xero prices the conversion there); never approximate one with two bank transactions or a manual journal — that would bypass Xero's FX lot subledger and corrupt realised-FX tracking (see the FX boundary above).
- Time-deposit **interest** remains a journal (accrual) as before; only the **principal movement** is a transfer.

## Shared conventions

1. **One workpaper** for the treasury close (bank + broker share the statement set and FX boundary). Tabs: `Cover` → `Bank & Cash Recon` → `IBKR Recon & Valuation` → `Draft Journal (USD)` → `Review Checklist`.
2. **USD is primary; HKD @ 7.80 is an indicative reference column, always labelled.**
3. **Reconcile in original currency** (rate-clean): statement balance ↔ GL/entry in USD.
4. **Account mapping** by Xero account name (e.g. `Financial assets at FV through P/L`, `Amount due from a broker - Interactive Brokers`, `Unrealised P&L (IBKR)`, `Interest Income (Bank)`, `Dividend income (IBKR)`, `Commission (IBKR)`, `Withholding Tax (IBKR)`); numeric codes TBD — flag, don't invent.
5. **Balance discipline** — every draft entry balances; expose a balance check.
6. **Draft + sign-off** — mark `DRAFT — for accountant review`; never imply posted/final.
7. **Flag, don't fix** — unsupported balances, NAV bridge breaks, classification questions go to a Review section.
8. **Output formatting** — Calibri; navy title bands (`1F3864`); light-blue subtotals (`D9E1F2`); yellow (`FFFF00`) for attention; HKD format `_($* #,##0.00_);_($* (#,##0.00);_($* "-"??_);_(@_)`; build with the `xlsx` skill, run `recalc.py`, confirm zero formula errors, share via `present_files`.

## Workflow

1. Resolve period and modules; read the bank/TD statements and the IBKR activity statement, plus the Xero export for reconciliation.
2. Read the module reference file(s). Validate the IBKR NAV bridge with `scripts/ibkr_nav_check.py`.
3. Reconcile balances to statements in USD; prepare the USD draft journal for the broker valuation/income items (and any TD interest accrual).
4. Add the indicative HKD @ 7.80 column (labelled).
5. Build the workpaper; recalc; verify zero errors.
6. Present; summarise the entries (USD), the reconciliations, and any flags. Note the journal is DRAFT and FX is Xero's.

## Standing notes

- **No financial advice; no live FX rates; preparation only.**
- **Non-monetary securities** — IBKR holdings are FVTPL: the whole change in fair value runs through P&L; the FX component is part of that fair-value movement (IAS 21), handled via Xero's translation, not a separate currency-revaluation entry. Flag for reviewer; do not separately revalue securities as a monetary item.
- **Boundary with other skills** — Expensify, lease, depreciation, prepayments, direct supplier expenses each have their own skill. On the bank statement, AMEX settlement and "EXPENSE CLAIM" autopays belong to Expensify; supplier-invoice payments belong to `3cp-monthly-journals` (direct expenses) — not here.

## Output 3 — Xero ManualJournal import CSV (alongside the workpaper)

In addition to the review workpaper (.xlsx, ALWAYS produced — the human-review artifact) and the contract payload (JSON), emit the **Xero ManualJournal import CSV** the user uploads into Xero (Business > Manual Journals > Import, or Advanced > Import):

```
python3 scripts/payload_to_xero_mj_csv.py --payload <draft_journals.json> --out <Period>_ManualJournal_Xero.csv [--rate <HKD per CCY>]
```

Rules the script enforces:
- One row per line; Xero groups rows into one journal by identical Narration+Date. Narration = `<reference> | <narration>` so the idempotency reference is visible in Xero.
- Amount signed (debit +, credit −); each journal balances to 0.00 after rounding (residual absorbed into the last line).
- **The MJ template has no currency column — imports post in HKD (base).** HKD journals pass straight through. **Non-HKD journals require `--rate` (the month-end Xero/XE rate, HKD per 1 unit)**; converted amounts carry the original-currency note in Description. Get the rate from the user — never fetch it.
- Account codes resolved from `references/chart-of-accounts.csv` (exact name, alias table, "Less "-prefix tolerance). A journal with any unresolvable account is **excluded and reported as an exception** — resolve by adding the code in Xero or extending the alias table; do not import a partial journal.
- GL account policy notes (622/623/624 usage, dividend gross-up, DBS/CCB interest rules, etc.) live in `/mnt/skills/user/3cp-shared-reference/references/gl-accounts.md` — the authoritative shared copy. Read this, not a local copy.
- TaxRate defaults to `Tax Exempt` (the org's no-VAT rate); if the Xero org rejects it, substitute the org's exact no-tax rate name via `--tax`.
- DRAFT journals only; HOLD journals are skipped and reported.

The CSV is the import artifact; the workpaper remains the review artifact. Import only after the workpaper is reviewed.

## Output 4 — Xero bank statement import CSV (CCB & IBKR only)

CCB and IBKR have **no automatic feed**, so also emit a Xero bank-statement import CSV for each (StatementImportTemplate) via `scripts/statement_to_xero_csv.py`. **DBS is auto-fed — never import a DBS statement** (but still journal DBS-paid transactions). Populate Payee/Description/Reference as specifically as the PDF allows so Xero auto-matches lines to the journals (matching Reference is key). See `references/bank-cash.md`. Amount is signed (in +, out −); date DD/MM/YYYY.

This same CSV doubles as the **statement-side input** for `3cp-bank-reconciliation-helper` (which pairs statement lines with the posted Spend/Receive transactions for reconciliation) — which is exactly why a consistent, specific Reference here matters: it drives clean matches at reconciliation, not just at import.
