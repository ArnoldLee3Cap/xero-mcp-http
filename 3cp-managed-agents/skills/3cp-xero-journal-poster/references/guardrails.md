# Guardrails — detail & failure handling

## 1. Draft where the type allows; verify where it doesn't
Manual journals and invoices are created `Status = DRAFT`; the user promotes them to Posted in Xero (no promote/update tool exists in the skill). **Bank transactions are the exception — Xero has no Draft state for them, so they post `AUTHORISED` (live).** Treat every bank transaction as a live entry: verify it, and if wrong, **void it in the Xero UI**. There is no delete/void tool in the skill.

## 1a. Accounts must be ACTIVE
Before posting, confirm every account code on an entry is **`ACTIVE`** in `list-accounts`. An **archived** account causes Xero to reject the write with a generic *"An unexpected error occurred"* — easily mistaken for a connection fault. If archived, stop and ask the user to restore it (Settings → Chart of Accounts → Archived → Restore) or give an active substitute; never guess a replacement code.

## 1b. Timeout ≠ failure — Timeout Recovery Protocol (field-verified Jul 2026)
A `create-*` call can time out yet still succeed on Xero's side — or never reach the server at all (relay-channel drop; the server process is usually healthy). Protocol on any create timeout:
1. **Verify, never blind-retry:** check the matching `list-*` tool for the entry's unique reference / contact name. Absent → re-issue once. Present → record the ID, continue. Blind retry risks a permanent duplicate with no tool to undo it.
2. **Independent check (optional):** if Desktop Commander/Filesystem is connected, the server log (`%APPDATA%\Claude\logs\mcp-server-xero-3cp.log`) shows whether the request ever arrived (`Message from client: tools/call`). For transfers, the matching read is `list-bank-transfers` (dedupe on reference, or amount + date).
3. **Two consecutive timeouts → stop.** The relay channel is wedged; ask the user to restart Claude Desktop, then re-run the Step-0 canary read (a cheap read such as `list-tax-rates`) before resuming writes. Channels wedge per-server — a responsive sibling MCP server does not prove the Xero channel is healthy.
4. **Sequential writes, unique reference each** — a timeout then leaves exactly one ambiguous entry, findable in step 1.

**Step-0 canary (prevention):** open every posting session — and every resumption after an app restart / machine wake — with a zero-risk read and get a response before the first write. The relay drops requests during channel re-establishment windows (post-restart, post-wake, proxy node switch); the first call after such an event is the likeliest to vanish. Burn that risk on a read.

## 1c. Supporting documents need a LOCAL path
`create-attachment` reads `filePath` from the machine running the MCP server (the user's computer). Chat-sandbox paths (`/mnt/user-data/uploads/...`) are invisible to it and fail with `File not found`. Always ask the user for the document and its **local** file path; require an exact filename match.

## 2. Idempotency (the reference is the key)
- **Before create:** query Xero for a manual journal carrying the same `reference`. If found → **skip, report** ("already exists as <status>"). Never create a second.
- **Before promote:** if the named reference is already `POSTED` → **skip, report**. So re-running "post the April batch" cannot double-post.
- Because the reference is deterministic per period/module/segment/currency, a re-run of a prep skill produces the same references, and the poster recognises them.

## 3. Reconcile-before-post
Eligible = `status == DRAFT` **and** balances within currency. Excluded:
- `HOLD` items (e.g. items still under classification review, or unmatched suspense) — report with their `hold_reason`, never post.
- Anything flagged for review in the source workpaper.
Before creating, use read tools (`list-trial-balance`, `list-profit-and-loss`, `list-report-balance-sheet`) to sanity-check the affected GL areas; if a balance looks inconsistent with the entry, surface it rather than posting blindly.

## 4. Promote only by explicit name
`promote` operates solely on references the user names (or a named batch the user identifies). Never promote all drafts; never infer the set. No automatic promotion after `create-draft`.

## 5. Re-verify before promote
For each named reference, re-read the draft from Xero and confirm it still balances and still matches the payload that created it. If a draft was edited in Xero since creation → **stop, report the difference**, do not promote. This prevents posting something other than what was reviewed.

## 6. Dry-run gate
No write occurs without a prior dry-run preview and explicit user approval. `scripts/dryrun.py` makes no Xero calls and is safe to run anytime.

## Failure handling
- **No write tools available** → run dry-run, deliver preview, report the write connection as the gate. Never simulate a successful post.
- **Account code unresolved** → stop for that journal, report which account name has no mapping; do not guess a code.
- **Account archived** ("An unexpected error occurred" on an otherwise valid line) → stop, name the archived account, ask the user to restore it or supply an active substitute.
- **Timeout on create** → do not retry blindly; verify with `list-*` first (see 1b). If it landed, move on; if not, retry once, then ask for an MCP restart.
- **Attachment `File not found`** → the path/filename is wrong or the file was never saved locally; ask the user to confirm the local path and exact filename. This is a real error, not a timeout.
- **Out-of-balance journal** → never send; report which journal and the residual.
- **Partial batch failure on create** → report exactly which references were created and which were not; the idempotency check makes a safe re-run possible.
