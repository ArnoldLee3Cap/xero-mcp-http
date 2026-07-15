---
name: 3cp-bank-reconciliation-helper
description: >-
  Read-only helper that proposes how 3 Capital Partners' bank STATEMENT lines
  pair with the posted ACCOUNT TRANSACTIONS (Spend/Receive Money) so the user
  confirms each match in Xero's Reconcile tab. Use whenever bank transactions
  have been posted and the user wants to reconcile them against the statement —
  DBS (auto-fed), CCB, or IBKR (imported via the Xero template) — or asks to
  "match the statement," "help me reconcile," "prep the reconciliation," or
  "reconcile the DBS/CCB/IBKR account." Reads the statement side from the source document (DBS PDF, or the
  CCB/IBKR import CSV) and the transaction side from xero-3cp:list-bank-transactions,
  then outputs proposed matches (on amount + reference, never date) with
  confidence tiers plus unmatched lists. Does NOT reconcile itself (no
  reconcile/match tool — the user clicks OK, or 3cp-xero-ui-operator
  clicks HIGH-tier matches), and does NOT
  post/void/edit or prepare journals. Not the poster (3cp-xero-journal-poster)
  or the completeness checker (3cp-close-orchestrator).
---

# 3CP Bank Reconciliation Helper

> **Important**: This skill is **read-only**. It proposes matches between bank
> statement lines and posted account transactions so you can reconcile faster in
> Xero. It **cannot reconcile for you** — the actual match-and-confirm is a human
> step in Xero's Reconcile tab (the `xero-3cp` server has no reconcile/match tool).
> It never posts, edits, or voids anything, and it gives no financial advice.
> **Handoff:** HIGH-tier proposals can be executed by **`3cp-xero-ui-operator`**
> (Op 2 — clicks OK only where Xero's own suggestion AND this skill's HIGH tier
> agree, per-batch approved); all other tiers remain the user's manual clicks.

## What it is (and is not)

- **Is:** the matching layer between the **statement side** (the bank's record)
  and the **ledger side** (the Spend/Receive Money the poster created). It reads
  both, proposes the pairing, and shows you exactly what to confirm in Xero.
- **Is not:** the reconciliation itself (Xero + you own the confirm click); the
  **poster** (`3cp-xero-journal-poster` creates the transactions); or the
  **completeness checker** (`3cp-close-orchestrator` matches items against the
  recurring register at account level, a different question).

## Where the two sides come from

| Side | DBS | CCB | IBKR |
|---|---|---|---|
| **Statement** (bank/broker record) | Parse the **DBS statement PDF**. DBS auto-feeds Xero, but the `xero-3cp` surface has no tool to read fed statement lines back, so the PDF is the source. | The **Xero statement-import CSV** the treasury skill emits (`statement_to_xero_csv.py`), or the parsed CCB statement — the same file imported into Xero. | The **Xero statement-import CSV** from the parsed IBKR activity statement, or the parsed statement directly. Imported into Xero the same way as CCB. |
| **Transaction** (ledger record) | `xero-3cp:list-bank-transactions` for the account, `Unreconciled` only. | Same. | Same. |

All accounts reconcile through the **same** Xero Reconcile tab. The only
difference is how statement lines arrive (DBS auto-feed vs manual CSV import for
CCB and IBKR) — the matching logic is identical.

### IBKR note — multi-line entries and net-movement matching

IBKR account transactions are typically posted as a **single Receive Money or
Spend Money with multiple line items** — e.g. one Receive Money carrying MTM
adjustment, interest income, change in interest accruals, dividends, WHT, change
in dividend accruals, commissions, and FX translations as separate lines, all
summing to a **net NAV change** (see the June 2026 screenshot: total (93,797.65)).
For matching purposes, the relevant amount is **the transaction total** (the net),
not individual line items. The statement side should likewise be expressed as net
cash/NAV movements per period, not broken into sub-components — the engine matches
at the transaction level, not the line-item level.

### Bank transfers (DBS ↔ CCB ↔ IBKR inter-account movements)

Cash transfers between accounts (e.g. DBS USD → IBKR funding, CCB USD → DBS HKD
via FX conversion) appear as a **withdrawal on the source account** and a
**deposit on the destination account** — two statement lines on two different
accounts. In Xero these are recorded as **bank transfers**, not Spend/Receive
Money. A bank transfer creates an account transaction on each side.

For matching:
- Each side is matched independently within its own account's proposal — the
  withdrawal on the source account matches the bank-transfer debit; the deposit
  on the destination matches the bank-transfer credit.
- A common pattern is an UNMATCHED line on one account that is actually the other
  leg of a cross-account transfer. **Flag these to the user** ("this looks like an
  inter-account transfer — check whether the other leg exists on [other account]")
  rather than silently leaving them unmatched, when the description/payee suggests
  an internal transfer (keywords: "transfer", "funding", "FX MARKET", the firm's
  own name as payee, or a reference that appears on another account's statement).
- The `xero-3cp` surface has a **`create-bank-transfer` tool (added Jul 2026) for
  SAME-currency transfers only**; cross-currency transfers (FX conversions, e.g.
  "FX MARKET" pairs) are still created manually in the Xero UI — the Xero API
  rejects them. Either way, the resulting transfer legs still need reconciling
  via this helper, and `list-bank-transfers` can be used to see posted transfers
  by reference/amount/date.

## Matching principle

Match on **signed amount (within one currency) + reference overlap — never date.**
Timing differences (value-date vs post-date, weekend roll-forward) mean dates
legitimately differ by a day or two; date is a tiebreaker only. See
`references/matching-logic.md` for sign convention, confidence tiers, reference
normalisation, and edge cases (batched wires, principal+fee, duplicate amounts,
timing). Read it before running.

## Workflow

1. **Identify the account and period** (e.g. "DBS HKD, June 2026"). Ask if unclear.
2. **Get the transaction side.** Call `xero-3cp:list-bank-transactions` for the
   account. Keep only `Unreconciled` entries. On a timeout, **verify with a repeat
   `list-bank-transactions` before assuming failure** (the connector can time out
   after the call already succeeded); two consecutive timeouts → ask the user to
   restart the `xero-3cp` MCP server.
3. **Get the statement side.** For CCB/IBKR, read the import CSV the user provides
   (or the treasury skill produced). For DBS, parse the statement PDF the user
   provides. For IBKR, express each period's activity as the **net movement**
   matching the posted transaction total, not broken into sub-component lines (see
   the IBKR note above). Normalise all to the engine's JSON shape (`date`, signed
   `amount`, `payee`, `description`, `reference`, `currency`) — see the script
   header.
4. **Run the matcher** (no Xero calls, safe anytime):
   ```
   python3 scripts/match_statement.py --statement stmt.json --transactions txns.json --out proposal.json
   ```
5. **Present the proposal** bottom-line-first: the count of clean (HIGH/MEDIUM)
   matches, then the items needing the user's eye — AMBIGUOUS (pick one), POSSIBLE
   FEE, and both UNMATCHED lists — each with amount, reference/payee, and the Xero
   transaction ID so the user can find it in the Reconcile tab. For MEDIUM matches,
   remind the user to sanity-check payee/date since there was no reference to confirm.
6. **Explain the unmatched.** An UNMATCHED **transaction** is usually timing
   (settles next period, e.g. MPF on the 1st–2nd) — leave it unreconciled until the
   line arrives; occasionally it's a wrong/duplicate post to **void in Xero**. An
   UNMATCHED **statement line** means no posted transaction — either it was never
   posted (route to `3cp-xero-journal-poster`) or it's a new item to book.
7. **Optional Excel artifact.** If the user wants a saved record, run `scripts/build_workbook.py` — it takes one or more `--account LABEL PROPOSAL_JSON CURRENCY` (repeatable, one sheet per account) and produces a Cover sheet (scope, matching basis, confidence-tier legend, summary table) plus one colour-coded, filterable sheet per account. **An account with a proposal but zero posted transactions still gets a sheet** — 100% unmatched statement lines is a correct, informative result, not an error, and it's often exactly where a mis-posted item (wrong account) surfaces. **An account genuinely not covered this run** (no statement available, or a workflow that doesn't apply — e.g. a time-deposit account with no bank transactions) must be named via `--out-of-scope "<reason>"` so it's a stated exclusion on the Cover sheet, never a silent omission. **All bank-type accounts in Xero** — DBS HKD, DBS USD, CCB HKD, CCB USD, and IBKR — should either appear as an `--account` sheet or be explicitly `--out-of-scope`.

## Guardrails

1. **Read-only, always.** Never call any `create-*` tool. Never reconcile, post,
   edit, or void. Output is a proposal the user acts on in Xero.
2. **Amount + reference, not date.** Never pair on date alone; report date gaps
   but don't let them drive or block a match.
3. **Same currency only.** Don't cross HKD with USD. Flag mixed-currency accounts.
4. **Never force a clean result.** UNMATCHED and AMBIGUOUS are valid, important
   outputs — surface them; do not stretch a match to make the numbers tie.
5. **Ambiguity → the user picks.** When several transactions share an amount and
   reference can't disambiguate, list all candidates; never auto-select.
6. **Timeout ≠ failure.** Verify with `list-bank-transactions` before re-calling.
7. **Flag likely inter-account transfers.** When an UNMATCHED line's payee or
   description suggests an internal movement (keywords: "transfer", "funding",
   "FX MARKET", the firm's own name, or a reference that appears on another
   account's statement), flag it as a probable bank-transfer leg rather than
   silently leaving it unmatched.

## Files

- `scripts/match_statement.py` — the matching engine (pure Python, no Xero calls).
- `scripts/build_workbook.py` — turns one or more match proposals into a single
  reviewable Excel workbook (Cover + one sheet per account); see step 7 above.
- `references/matching-logic.md` — sign convention, confidence tiers, reference
  normalisation, and edge-case handling. Read before running.
