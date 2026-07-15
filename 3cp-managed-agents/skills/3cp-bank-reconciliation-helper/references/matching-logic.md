# Matching logic — detail, confidence tiers, and edge cases

## The two sides

Xero reconciliation pairs **statement lines** (the bank's record) with **account
transactions** (the ledger record — the Spend/Receive Money the poster created).
This skill reads both and proposes the pairing; the user confirms each in Xero.

- **Statement side** comes from the **source document**, never from Xero:
  - **DBS** — parsed from the DBS statement PDF (DBS auto-feeds Xero, but the
    `xero-3cp` surface has **no tool to read statement lines back out**, so the
    statement side must come from the PDF).
  - **CCB** — from the Xero **statement-import CSV** the treasury skill emits
    (`statement_to_xero_csv.py`, `StatementImportTemplate` shape), or the parsed
    CCB statement. This is the same file the user imports into Xero.
  - **IBKR** — from the Xero **statement-import CSV** produced from the IBKR
    activity statement, or the parsed activity statement directly. Imported into
    Xero the same way as CCB. Note: IBKR entries are typically **net-movement**
    figures (see the IBKR section below), not individual sub-components.
- **Transaction side** comes from **`xero-3cp:list-bank-transactions`** for the
  account, filtered to `Unreconciled` (already-reconciled ones need no match).

## Amount + reference, never date

Match on **signed amount within one currency** plus **reference overlap**. Do
**not** match on date. Value-date-vs-post-date differences and weekend
roll-forwards mean a line dated month-end can post a day or two later; the engine
uses date only as a tiebreaker and reports a `date_gap_days` for the user's eye.

**Sign convention:** statement `amount` is signed — money **into** the account
`+`, money **out** `−`. A transaction's signed amount is `RECEIVE = +`,
`SPEND = −`. A statement OUT line matches a SPEND; a statement IN line matches a
RECEIVE. The engine will not cross a debit with a credit.

**Currency:** only same-currency lines match. If either side omits currency the
engine won't block on it, but flag mixed-currency accounts (DBS USD, CCB USD,
IBKR) so the user checks the currency column.

## Confidence tiers

| Tier | Condition | What the user should do |
|---|---|---|
| **HIGH** | Amount matches **and** reference overlaps (shared token, e.g. an invoice/account no. on both sides), and the reference uniquely picks one candidate | Confirm — strong pair |
| **MEDIUM** | Amount matches **uniquely** but there's no reference to confirm (common for DBS, whose feed reference is bank-generated) | Confirm after a quick payee/date sanity check |
| **AMBIGUOUS** | Several transactions share the same amount and reference doesn't disambiguate | **Pick the right one in Xero** — the engine will not guess |
| **GROUPED** | One statement line equals the **sum** of several transactions, or one transaction equals the sum of several statement lines | Confirm the split (Xero supports one-to-many reconciliation) |
| **POSSIBLE FEE** | Amounts differ by a small amount (≤ `--fee-max`, default 60, or ≤ `--fee-pct`, default 0.5%) | Check whether a wire/bank fee sits inside one side but not the other |
| **UNMATCHED (line)** | A statement line with no posted transaction | Either the entry was never posted (route to the poster) or it's a genuinely new item |
| **UNMATCHED (txn)** | A posted transaction with no statement line | Usually **timing** (settles next period, e.g. MPF on the 1st–2nd) — leave unreconciled until the line arrives; or a wrong/duplicate post to void in Xero |

## Reference matching

References are normalised to uppercase alphanumeric tokens of length ≥ 3;
overlap is the share of the smaller token set that appears in both. This tolerates
formatting noise ("INV-7073639" vs "Ogier 7073639") while still keying on the
stable identifier. For CCB/IBKR the treasury skill deliberately writes a
Reference on the import CSV that mirrors the posted transaction — that is what
produces HIGH matches. DBS feed references are bank-generated, so DBS pairs are
usually MEDIUM (amount-unique) and rely on the payee/date sanity check.

## Edge cases the engine handles

- **Batched wire booked as several transactions** (e.g. a single bank debit that
  the poster split per payee) → 1-to-many GROUPED.
- **Principal + separate fee line** on the statement against one posted
  transaction that folded the fee in → many-to-1 GROUPED.
- **Duplicate amounts** (two different bills for the same figure) → AMBIGUOUS,
  listed together for the user to pick.
- **Timing** → UNMATCHED transaction, flagged as likely next-period settlement.

## IBKR — multi-line Receive/Spend Money entries

IBKR is a bank-type account in Xero. The treasury close posts account
transactions against it just like DBS and CCB — typically a single Receive Money
(or Spend Money) with **multiple line items** covering MTM adjustment, interest
income, change in interest accruals, dividends, WHT, change in dividend accruals,
commissions, and FX translations. The **transaction total** is the net of all
these lines (e.g. June 2026: (93,797.65) net = (95,260.05) MTM + 1,327.42
interest + 45.66 accrual Δ + 417.89 dividends − 125.37 WHT − 203.20 div
accrual Δ + 0 commissions + 0 FX).

For matching:
- The engine matches the **transaction total** against the statement's net
  movement, not individual line items.
- The statement-side JSON should express each period's activity as the net cash
  or NAV movement that corresponds to this total — not broken into
  sub-components. The treasury skill's import CSV already does this.
- IBKR statements may also carry **discrete cash movements** (funding inflows,
  withdrawal outflows, dividend cash receipts as separate settlement lines) — each
  of these is a separate statement line and matches separately from the
  valuation-journal entry.

## Bank transfers (inter-account movements)

Cash transfers between accounts (e.g. DBS USD → IBKR funding, CCB USD → DBS HKD
via FX conversion) appear as:
- A **withdrawal** on the source account's statement.
- A **deposit** on the destination account's statement.
- A **Xero bank transfer** (not a Spend/Receive Money), which creates one account
  transaction on each side.

For matching:
- Each side is matched **independently** within its own account's proposal.
- The withdrawal on the source matches the bank-transfer debit; the deposit on
  the destination matches the bank-transfer credit.
- A common diagnostic pattern: an UNMATCHED line on one account may be the other
  leg of a cross-account transfer. **Flag these to the user** when the
  description/payee suggests an internal movement — keywords: "transfer",
  "funding", "FX MARKET", the firm's own name as payee, or a reference that
  appears on another account's statement.
- The `xero-3cp` surface has a **`create-bank-transfer` tool (added Jul 2026,
  same-currency only)**; cross-currency transfers are still created manually in
  the Xero UI (API unsupported). Posted transfers are visible via
  `list-bank-transfers`, and their legs still need reconciling.

FX conversions (e.g. CCB USD → CCB HKD via "FX MARKET - MAB / MAS") produce
two statement lines on two different currency sub-accounts — a debit in the
source currency and a credit in the destination currency. In Xero these are
either a bank transfer between the two currency accounts or, if the accounts
are sub-accounts of the same multicurrency account, a single FX conversion.
Either way the engine matches each leg independently within its account.

## What the engine deliberately does NOT do

- It never confirms a reconciliation (no reconcile/match write tool exists).
- It never posts, edits, or voids anything in Xero.
- It never forces a clean result — an UNMATCHED item is a valid, important
  output, not a failure. Surface it rather than stretching a match to hide it.
