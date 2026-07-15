# Module: Bank & Cash Reconciliation (`--bank`)

Reconcile every bank account and time deposit to its statement **in original currency**, and prepare a time-deposit interest accrual (USD) if the firm accrues it. FX translation/revaluation is Xero's — not prepared here.

## Inputs

- **Bank statements** — DBS and CCB, HKD and USD accounts (current, savings, multi-currency), period-end balances.
- **Time-deposit advices** — placement confirmations (principal, rate, value/maturity dates, anticipated interest).
- **Xero export** — for reconciliation of each bank/TD account.

## Procedure

1. List each account (Xero name), currency, period-end balance per statement, and the Xero carrying balance. Tie **in original currency** (USD accounts tie in USD; HKD accounts tie exactly).
2. The HKD difference on USD accounts is the Xero spot-vs-7.80 gap — **expected, not a reconciling error**. Show an indicative HKD @ 7.80 column (labelled) for context only.
3. Confirm time-deposit principals, rates, and maturities against the advices; note new placements and rollovers.

## Entries (USD draft, when applicable)

- **Time-deposit interest accrual** (`3CP-TRES-<period>-TDINT`) — if the firm accrues TD interest to period-end (rather than only on receipt): accrue days elapsed × rate on each open TD.
  `DR Interest accrual (receivable)  /  CR Interest Income (Bank)`, in USD. Confirm the firm's accrual policy before booking; flag if uncertain.
- Bank interest already credited on the statement is normally captured by the bank feed — reconcile, don't re-book.

## Out of scope (Xero owns)

- FX translation, period-end revaluation ("Bank Revaluations"), and realised FX on conversions. The bank statements show conversion rates (e.g. a USD→HKD transfer prints its rate) — these feed Xero's FX engine; this skill does not recompute them.

## Flags

- **No statement supplied:** if an account has no month-to-month movement, 3CP does not always provide a statement. In that case **assume no change and carry the prior balance forward** unchanged — do not flag it as missing. Only query an account where a statement is expected (i.e. there was activity) but absent.
- Conversions in the period (USD↔HKD) — note them; realised FX is Xero's, but flag large conversions for the reviewer.
- Numeric GL codes TBD.

## Bank statement import to Xero — feeds vs manual CSV

**DBS = automatic bank feed.** DBS statement lines flow into Xero automatically — **do NOT import a DBS statement CSV**. We still create the manual journals for DBS-paid transactions (e.g. paying a supplier bill from DBS x1627 = `DR expense / CR 110`); Xero reconciliation then matches the auto-feed line to that journal.

**CCB and IBKR = NO feed → import the statement manually** via the Xero bank-statement CSV (StatementImportTemplate: `*Date,*Amount,Payee,Description,Reference,Check Number`). Produce it with `scripts/statement_to_xero_csv.py` from the parsed PDF statement:

```
python3 scripts/statement_to_xero_csv.py --txns parsed_txns.json --out <Acct>_StatementImport_Xero.csv
```

Conventions:
- **Date** DD/MM/YYYY. **Amount** is a single signed column: money **into** the account = positive, **out** = negative.
- One row per statement transaction. (A time-deposit roll appears as separate maturity / interest / re-placement lines that net to the cash movement — e.g. CCB USD Apr-26: +282,924.31 maturity, +808.85 interest, −283,733.16 placement = net 0.)

**Fill Payee / Description / Reference as specifically as the statement allows** — Xero matches imported lines to existing journals and learns on Payee + Reference, so detail here is what makes reconciliation efficient:
- **Payee** = counterparty (e.g. "CCB (Asia) Time Deposit", "IBKR - dividend USD").
- **Description** = clear narrative of the line.
- **Reference** = a stable id that *also appears on the matching journal* (account no., TD confirmation no., IBKR activity id). Matching References between the statement line and the journal is the single biggest driver of clean auto-reconciliation.

The statement-import CSV is the **bank side**; the ManualJournal CSV (income/valuation) is the **ledger side** — Xero reconciliation matches the two.
