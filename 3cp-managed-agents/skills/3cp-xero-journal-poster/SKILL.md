---
name: 3cp-xero-journal-poster
description: Post 3 Capital Partners' prepared month-end journals to Xero, consuming the common contract payload produced by the prep skills (3cp-monthly-journals, 3cp-investment-treasury-close, expense-monthly-close-builder). One write operation — create entries in Xero as DRAFT (manual journals, ACCREC sales invoices, ACCPAY bills, bank transactions) via the locked-down xero-3cp MCP server; promotion to Posted is a human step in Xero, not a skill action. Draft-first and idempotent (dedupes on each journal's unique reference); reconcile-before-post using Xero read tools; never auto-approves and never writes to the live ledger without a named, per-batch instruction. Use when the user wants to push prepared entries to Xero as drafts for review. Requires the xero-3cp connection (locked-down Xero MCP server) exposing the create-* tools; module skills never post.
---

# 3CP Xero Journal Poster

> **Important**: This skill **writes to your accounting system**. It is **draft-first for the entry types that support a Draft state** — manual journals and invoices (ACCREC/ACCPAY) are created as **DRAFT** for you to review and approve in Xero. **Bank transactions are the exception: Xero has no Draft state for them, so `create-bank-transaction` posts as `AUTHORISED` (live).** These are not drafts — verify each one and, if wrong, **void it in the Xero UI** (there is no delete/void tool in this skill). The skill does not provide financial advice, never auto-approves manual journals/invoices, and never writes without your named, per-batch instruction. It is the single consumer of the common journal contract emitted by the prep skills.

## What this skill is (and is not)

- **Is:** the one mechanical posting layer for every prep skill. All prep skills emit the **same contract payload** (reference, period, currency, lines), so this skill consumes one shape regardless of source. There is deliberately **one** poster, not one per module — the posting job is identical across domains; only the prep thinking differs.
- **Is not:** a preparer. It computes nothing, classifies nothing, fetches no FX rate. It validates, previews, and posts what the prep skills produced.

## Connection (write-capable via the 3CP minimal MCP server)

This skill posts through the **`xero-3cp`** connection — a locked-down build of the official Xero MCP server (the `tool-factory.ts` allowlist overlay, v2 July 2026). It exposes exactly **21 tools**; the only writes are the **create** tools below. Manual journals and invoices are created as **DRAFT**; **bank transactions post `AUTHORISED`** (Xero has no Draft state for them — see the Important note above):

- **Writes:** `create-manual-journal` (DRAFT), `create-invoice` (ACCREC sales invoices + ACCPAY bills, DRAFT), `create-bank-transaction` (**AUTHORISED — live, not draft**), `create-bank-transfer` (**AUTHORISED — live; same-currency account-to-account movements only**, added Jul 2026), `create-repeating-invoice` (**ACCREC templates ONLY — see constraint below**; `approve=false` default = DRAFT template that generates nothing), `create-contact`, `create-attachment` (attach a supporting document to a manual journal or bank transaction).
- **Reads (resolve + reconcile-before-post / dedupe):** `list-accounts`, `list-contacts`, `list-invoices`, `list-manual-journals`, `list-bank-transactions`, `list-bank-transfers` (added Jul 2026 — verification/dedupe for transfers), `list-repeating-invoices` (added Jul 2026 — verify/dedupe repeating templates, including UI-built bill templates), `list-organisation-details`, `list-tax-rates`.
- **Reads (reporting — used by 3cp-close-orchestrator Mode 2 and the FRR workflow):** `list-trial-balance`, `list-profit-and-loss`, `list-report-balance-sheet`, `list-aged-receivables-by-contact`, `list-aged-payables-by-contact`.

**`create-repeating-invoice` constraint (verified against tool schema, Jul 2026):** Xero's API only supports creating **ACCREC** (sales) repeating templates. **ACCPAY repeating BILLS are rejected** by Xero with "not of valid type for creation" and must be set up in the **Xero UI** (Business → Bills → Repeating — automatable via **`3cp-xero-ui-operator`** Op 5, same End-Date/dedupe rules). Do NOT work around this with zero-total ACCREC templates — it pollutes the sales ledger. Rules when this tool is used:
1. **Dedupe first:** always call `list-repeating-invoices` and abort if a template with a matching reference/contact/schedule already exists (there is no update/delete tool for templates — fixes are UI-only).
2. **End-Date validation:** `endDate` MUST be after `nextScheduledDate` — validate before calling (a near-miss in Jul 2026 almost shipped an end date before the next bill date).
3. **DRAFT default:** never pass `approve=true` without a named, per-template instruction; DRAFT templates generate nothing until a human arms them in Xero.

There is deliberately **no update/delete/post/void tool**, so this skill cannot flip a manual-journal/invoice draft to Posted, nor delete or void an AUTHORISED bank transaction — both are **human steps in Xero, executable with `3cp-xero-ui-operator`** (the sole browser-writer skill: draft promotion runs as a batch-approved op; voids run per-item confirmed). If the `xero-3cp` connection is absent, run dry-run only (validate + preview) and report the connection as the gate.

**The module skills never post.** `3cp-revenue-recognition`, `3cp-investment-treasury-close`, `3cp-monthly-journals`, and `expense-monthly-close-builder` only prepare drafts (workpapers + import CSVs + contract payloads). This poster is the single skill that touches Xero.

## The posting operation (create only)

| Verb | Action | State on create | Reversible? |
|---|---|---|---|
| **create-draft** | manual journal / invoice contract payload → Xero entry | **DRAFT** | Yes — delete the draft in Xero |
| **create-bank-txn** | direct bank movement → Xero bank transaction | **AUTHORISED (live)** | Only by **voiding in the Xero UI** — no void tool here |
| **create-bank-transfer** | same-currency movement between two of the firm's own bank accounts | **AUTHORISED (live)** | Only by **deleting in the Xero UI** — no delete tool here |

Manual journals and invoices are created **DRAFT**; the user promotes them to Posted in Xero (the minimal server exposes no update/post tool, so draft-first is enforced structurally for these). **Bank transactions cannot be created as Draft — Xero posts them AUTHORISED.** Treat every bank transaction as a live entry: verify it, and if it is wrong, **void it in the Xero UI**. Because there is no void/delete tool, a wrong or duplicate bank transaction is a manual clean-up — see the timeout guardrail below.

Payload → tool mapping:
- **Manual journals** (treasury, monthly-journals, expense recognition) → `create-manual-journal`: `narration` = `"<reference> | <narration>"`; `manualJournalLines` = one per line `{ lineAmount: debit − credit, accountCode, taxType: "NONE" }`; `date` (YYYY-MM-DD); `lineAmountTypes: "NO_TAX"`; `status: "DRAFT"`. **TaxType note (verified via `list-tax-rates`, July 2026):** in the 3CP Xero org the tax rate *named* "Tax Exempt" has API code **`NONE`** — so `taxType: "NONE"` IS the Tax Exempt rate. Journals showing `TaxType: NONE` in Xero are correct, not a discrepancy. Always pass the API code (`NONE`), never the display label ("Tax Exempt") in `taxType`.
- **Revenue** (SalesInvoice payload) → `create-invoice` `type: "ACCREC"` (contact via `list-contacts`/`create-contact`). **Line coding: `accountCode 622` (Management Fee Receivables) — NOT 200.** Coding to 622 makes Xero auto-reclass the accrued receivable (DR 610 / CR 622); coding to 200 would recognise revenue a second time on top of the monthly accruals (the exact double-count the 622 process eliminates). `taxType: "OUTPUT"` — confirmed from posted Q1 2026 invoices; invoices use OUTPUT, manual journals use NONE. DRAFT by default.
- **Expense bills** (payment step) → `create-invoice` `type: "ACCPAY"` coded to 801/135; DRAFT by default.
- **Direct bank movements** → `create-bank-transaction` (SPEND/RECEIVE). **Posts `AUTHORISED` (live) — no Draft state exists for bank transactions.** One contact per transaction; if a single wire covers multiple payees (e.g. a batched remittance), split into one transaction per contact.
- **Inter-account transfers (own accounts, SAME currency)** → `create-bank-transfer` (added Jul 2026): `fromBankAccountId` + `toBankAccountId` (both resolved via `list-accounts`, Type BANK, ACTIVE), `amount`, `date`, unique `reference` (e.g. `TFR-DBS-CCB-JUN26`). **Posts `AUTHORISED` (live).** Creates a transfer-out and transfer-in side that each reconcile against their own statement lines. **Cross-currency movements (e.g. DBS HKD → Business Savings USD) are NOT supported by Xero's API** — route those to **`3cp-xero-ui-operator`** (Op 8: UI Transfer Money form, per-transfer approved, bank-actual amounts both legs); never approximate a cross-currency transfer with two bank transactions. Do not book an own-account transfer as a Spend/Receive pair or a manual journal — one movement, one object.
  - **DBS-fed accounts do NOT duplicate.** The DBS auto-feed imports **statement lines only** (raw bank data); it does not create the account transaction. The Spend/Receive this skill creates is the *counterpart* that the feed's statement line reconciles against in the Xero UI. A freshly created bank transaction correctly shows `Unreconciled` until Arnold matches it to the feed line. Duplication only arises if the *same* expense is booked twice — e.g. once as a GL-only manual journal **and** again as a Spend Money. Book each direct-payment item through **one** object (the Spend/Receive), not both.
  - Non-fed accounts (CCB, IBKR) work identically — Spend/Receive is the correct object; there is simply no auto-feed, so the statement is imported manually.
  - **Hand-off:** once bank transactions are posted, matching them to the statement lines for reconciliation is a separate read-only step — use **`3cp-bank-reconciliation-helper`** to produce the statement-line ↔ transaction match proposal, which the user then confirms in Xero's Reconcile tab. This poster never reconciles.

## Supporting documents (attach after every create)

Every manual journal and bank transaction should carry its **supporting document** (supplier invoice, debit note, statement, advice). After creating the entry, attach the source document with `create-attachment` (`entityType: "MANUAL_JOURNAL"` or `"BANK_TRANSACTION"`, the created entity's ID, a `fileName`, and `filePath`).

**Ask the user for the document and its file path before attaching — do not assume one exists on disk.** For each entry that needs support:
1. Ask which supporting document belongs to it (e.g. "which invoice supports DP-D-Ogier?").
2. Ask for its **local file path on the machine running the `xero-3cp` MCP server** — i.e. a path on the user's own computer such as `C:\Users\...\Month-end invoices\6. June 2026\Ogier_Inv_7073639.pdf`. **It must be a local file address.** Files uploaded into the chat live in a sandbox (`/mnt/user-data/uploads/...`) that the MCP server cannot see; those paths will fail with `File not found`. The user must save the file locally first and give that local path.
3. The `filePath` must point to a file that exists at that exact location, with an **exact filename match** (including case and spacing) — `File not found` means the path/name is wrong or the file was never saved there, not a connection fault.

If the user has no document for an item, note it as unsupported and move on — do not block the posting.

## Guardrails (every run)

1. **Draft where the type allows; verify where it doesn't.** Manual journals and invoices are created `Status = DRAFT` and promoted by the user in Xero. **Bank transactions post `AUTHORISED` (live) — Xero has no Draft state for them;** treat each as live, verify it, and void in the Xero UI if wrong.
2. **Idempotency on the reference.** Before creating, check no Xero entry already carries that **reference**; if it exists, **skip and report** (never double-create). This matters most for bank transactions, which cannot be deleted via the skill.
3. **Reconcile-before-post.** Only entries that **balance within their currency** are eligible. Anything marked `HOLD` (items under classification review or unmatched suspense) or sitting in a review state is excluded. Use the Xero **read tools** (`list-trial-balance`, `list-profit-and-loss`, `list-report-balance-sheet`) to sanity-check affected GL balances before creating.
4. **Accounts must be ACTIVE, not just present.** Before posting, confirm every account code on an entry is **`ACTIVE`** in `list-accounts` — an **archived** account will cause Xero to reject the write with a generic *"An unexpected error occurred"* (not a clear message). If an account is archived, stop and ask the user to restore it in Xero (Settings → Chart of Accounts → Archived → Restore) or supply an active substitute — do not guess a replacement.
5. **Timeout ≠ failure — verify before retrying (Timeout Recovery Protocol).** A `create-*` call can time out ("No result received…") yet still have **succeeded** on Xero's side — or (equally common, field-verified Jul 2026) never have reached the server at all. Never retry a write blind; there is **no delete/void tool** to undo a duplicate. On any `create-*` timeout:
   - **(a)** Verify with the matching `list-*` tool (`list-bank-transactions`, `list-manual-journals`, `list-invoices`, `list-contacts` with `searchTerm`) using the entry's **unique reference or contact name**. Absent → re-issue once. Present → record the returned ID and continue to the next entry.
   - **(b)** If Desktop Commander / Filesystem tools are connected, the server's own log (`%APPDATA%\Claude\logs\mcp-server-xero-3cp.log`) is an independent second check: if the request never shows a `Message from client: tools/call` entry, it never arrived and the create definitively did not happen. Conversely (field-verified Jul 2026), the log can show the call arrived AND the server returned a `result` within seconds while the chat still reported a 4-minute timeout — the failure is in the **Desktop-app relay**, not the server. In that case no restart is needed: for a **read**, simply retry; for a **write**, the log's `result` line means it succeeded — verify with the matching `list-*` tool and do NOT re-issue. After any Claude Desktop restart, expect the first call to possibly time out this way — treat the log as the source of truth on whether it executed.
   - **(c)** **Two consecutive timeouts → stop.** The relay channel to the server is wedged (the server process is usually fine); ask the user to restart Claude Desktop, then re-run the Step-0 canary read before resuming. Do not keep retrying into a wedged channel.
   - **(d)** Post writes **sequentially, one entry per call, each with a unique reference** — so any timeout leaves exactly one ambiguous entry, findable by its reference in step (a).
   - **(e)** Timed-out `create-bank-transfer` calls are verified with **`list-bank-transfers`** (added Jul 2026) — dedupe on the transfer's unique reference, or on amount + date if none.
   - Timeouts affect channels **per-server**: other MCP servers (e.g. Desktop Commander) may still respond while `xero-3cp` is wedged, and vice versa. A working sibling server does not mean the Xero channel is healthy.
6. **No promotion by the skill.** Manual-journal/invoice drafts are promoted to Posted by the **user in Xero**; bank transactions are already AUTHORISED and, if wrong, voided by the user. The skill has no update/post/void tool.
7. **Dry-run before any write.** Always produce the preview (`scripts/dryrun.py`) and get explicit approval before creating.
8. **Step-0 channel warm-up (canary read) — every posting session, and after every app restart.** Before the FIRST `create-*` of a session, issue a cheap zero-risk read (`list-tax-rates` or `list-organisation-details`) and get a response. Rationale (field-verified Jul 2026): the relay channel drops requests during its re-establishment window — right after a Claude Desktop restart, a machine wake, or a proxy node switch — so the first call after any of these events is the one most likely to vanish. Burn that risk on a read, never on a write. If the canary times out, retry it once; if it times out twice, ask the user to restart Claude Desktop and re-run the canary before posting anything.

## Contract consumed

The input is the prep skills' journal payload — see `references/contract.md`. Each journal: `reference`, `status`, `date`, `currency`, `narration`, `reversal`, and `lines` of `{account, debit, credit}`. One currency per journal (Option B). HKD posts as-is; non-base currencies (USD) post in their currency and **Xero applies its own FX rate on posting** — this skill never sends a rate.

## Account resolution

Payload lines carry **account names**; Xero manual journals reference accounts by **code/ID**. Resolve names → codes via the firm's chart-of-accounts mapping before the write call (the prep skills note "codes TBD"). The dry-run runs on names; the write step requires resolved codes. See `references/xero-mapping.md`.

## Workflow

1. Load the contract payload (a prep skill's JSON output).
2. Run `scripts/dryrun.py --payload <file>` — validates balances per currency, separates eligible vs held, and prints exactly what would be sent (reference, account, currency, debit/credit). Optionally pass `--existing-refs` to simulate idempotency.
3. Deliver the preview; get explicit approval.
4. **If `xero-3cp` is connected:** run the **Step-0 canary read** (guardrail 8) to confirm the channel is warm, then resolve account codes (`list-accounts`, confirming each is **ACTIVE**) and contacts (`list-contacts`/`create-contact`), dedupe against existing entries (`list-manual-journals` / `list-invoices` / `list-bank-transactions` on the reference), then create the eligible entries via the mapped tool — manual journals/invoices as DRAFT, bank transactions AUTHORISED — **sequentially, one per call**, reporting each reference created or skipped. On any timeout, apply the **Timeout Recovery Protocol** (guardrail 5). **If not connected:** stop and report the connection as the gate.
5. **Attach supporting documents.** For each entry, ask the user for the source document and its **local file path** (on the MCP-server machine), then `create-attachment`. See "Supporting documents" above.
6. **Review in Xero.** The user promotes manual-journal/invoice drafts (Draft → Posted) and verifies AUTHORISED bank transactions, voiding any that are wrong — either manually or via **`3cp-xero-ui-operator`** (Op 3 batch-approved promotion; Op 4 per-item void). The skill neither promotes nor voids. To reconcile the posted bank transactions against the statement, hand off to **`3cp-bank-reconciliation-helper`** (read-only match proposal → user confirms in Xero, or `3cp-xero-ui-operator` Op 2 clicks the double-confirmed HIGH-tier matches).

## References & scripts

- `references/contract.md` — the journal payload contract.
- `references/guardrails.md` — detailed guardrail logic and failure handling.
- `references/xero-mapping.md` — Xero Accounting API shape (manual journal DRAFT→POSTED), account-code resolution, and exactly what a write integration must expose to match this contract.
- `scripts/dryrun.py` — validate a payload and print the dry-run preview (no Xero calls; safe to run anytime).

## Demo → live migration gate (added Jul 2026)

Before the FIRST posting run against the live 3CP org, complete
`references/demo-to-live-migration.md` in full — connection verification, scripted COA diff,
opening-state verification, and a parallel run. The pipeline was validated on Demo Company; this
checklist is the bridge. Do not post live with any item unchecked.
