# Xero Accounting API mapping & write-integration spec

This is what a **write-capable** Xero connection must expose for this skill to post. The currently connected MCP is read-only (`get_*` reporting tools only) and cannot do any of the below.

## Required scope & role
- OAuth2 scope: **`accounting.transactions`** (read+write manual journals). `accounting.settings` (read) is useful to pull the chart of accounts for code resolution.
- Xero user role permitting manual journals (Adviser, or Standard with the right).

## Manual journal lifecycle (maps to our two verbs)
- **create-draft** → `POST /api.xro/2.0/ManualJournals` with `Status: "DRAFT"`, a `Narration`, optional `Date`, optional `Reset` reversing date, and `JournalLines[]` of `{ AccountCode, LineAmount, Description, … }` (positive LineAmount = debit, negative = credit, per Xero convention).
- **promote** → `POST` (update) the same journal with `Status: "POSTED"`, identified by its `ManualJournalID`.
- **idempotency** → carry our `reference` in a stable field (e.g. `Narration` prefix or a tracking field) and query before create; map our reference ↔ Xero `ManualJournalID` after creation.

## Currency
Manual-journal lines may be HKD or a foreign currency. For a USD journal, send the **USD** amounts; Xero applies the org's exchange rate on posting (or accepts a supplied rate — we do **not** supply one). HKD is the base currency and posts as-is. One currency per journal (Option B) keeps each manual journal single-currency.

## Account resolution (names → codes)
Our payload carries account **names**; Xero needs `AccountCode` (or `AccountID`). Before the write call, resolve each name via the chart of accounts (`GET /Accounts`, or a maintained mapping). If a name has no code, **stop and report** — never guess.

Maintain a mapping table, e.g.:

| Payload account name | Xero AccountCode |
|---|---|
| Interest on Lease Liabilities | TBD |
| Lease Liability | TBD |
| Depn - Right of Use Asset | TBD |
| Accumulated Depreciation Right-of-use of Asset | TBD |
| Depn - Computer Equipment / F&F / L&I / Office Equipment | TBD |
| Accumulated Depreciation on … (each class) | TBD |

(3CP to supply the codes once; they are stable month to month.)

## Minimal tool surface a write MCP must offer
1. `create_manual_journal(reference, date, narration, currency, status, lines[], reversal_date?)` → returns `ManualJournalID`.
2. `update_manual_journal_status(manual_journal_id | reference, status)` → for promote.
3. `find_manual_journal_by_reference(reference)` → for idempotency / re-verify.
4. `list_accounts()` → for code resolution.
5. (read, already present) `list-trial-balance`, `list-profit-and-loss`, `list-report-balance-sheet` → reconcile-before-post.

Items 1–4 are the gap in the current read-only connector.
