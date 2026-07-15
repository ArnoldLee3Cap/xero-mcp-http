# Operational Runbook — day of close

Prereq (once per machine): `source ./3cp-close.ids.env`.

## 1. Document intake (Mode 1)

When the month's sources have arrived (payroll report, DBS/CCB statements,
time-deposit advices, IBKR activity statement, Addepar export + receivable
list, Expensify report, AMEX statement, CCB/IBKR import CSVs):

```bash
./run-close.sh mode1
```

Upload the documents as session resources (Files API → `resources.add`, or
drop them in the Console session view), then let the coordinator's
document-audit self-copy check them against `recurring-register.md`.

**Gate:** proceed to Mode 2 only when Mode 1 reports every register item
covered (or you've explicitly accepted the gaps).

## 2. Close execution (Mode 2)

```bash
./run-close.sh mode2
```

This fires a **manual deployment run** (the deployment is paused — it never
fires on cron). The run record carries the new `session_id`; the script prints
the Console trace URL and streams events. The coordinator fans out to all five
module sub-agents in parallel, then synthesizes the workpaper + completeness
report into `/mnt/session/outputs/`.

While it runs, keep the stream (or Console) open — see
`docs/session-event-handling.md` for the confirmation loop.

## 3. Review the workpaper / resolve flags

The session goes **idle** when the coordinator has open questions (e.g.
unidentified payee `YUEN H**`, a bonus in the payroll report, an unpriced
position, an invoice that doesn't tie to accruals). Answer in-session:

```bash
ant beta:sessions:events send --session-id "$SID" <<'YAML'
events:
  - type: user.message
    content:
      - type: text
        text: "YUEN H** is Yuen Hoi-man (staff receivable, not PEP). Bonus for K. Lau: accrue DR 476. Re-prepare the affected journals."
YAML
```

The coordinator re-delegates **only the affected module(s)** and returns to
the confirmation gate with a refreshed workpaper.

## 4. Approve Xero draft posting

When the workpaper is final, tell the coordinator to post. Each
`create-manual-journal` / `create-invoice` / `create-bank-transaction` call
pauses the session (`requires_action`); approve each pending event with
`user.tool_confirmation` (`allow`) — or `deny` with a message to correct
course. Every entry lands in Xero as **DRAFT**, deduped on its unique
reference (idempotent: an accidental re-run won't double-post).

Pull the deliverables:

```bash
./run-close.sh outputs "$SID"    # lists workpaper + completeness report file IDs
```

## 5. Promote drafts to Posted (separate, human step)

Outside this deployment entirely: review the drafts in Xero and promote via
the Xero UI — or run the `3cp-xero-ui-operator` skill in a Claude Code session
for batch promotion, statement CSV imports (CCB/IBKR), and reconcile-tab
clicking of the HIGH-tier matches proposed by the reconciliation sub-agent.

## 6. Wrap up

- Archive the session (routine cleanup — sessions are disposable; never
  archive the agents/environment):
  `ant beta:sessions archive --session-id "$SID"`
- File the workpaper + completeness report with the month's close records.
- Audit trail: the primary session events are the orchestration record;
  per-module detail lives in the session threads
  (`GET /v1/sessions/{sid}/threads/{tid}/events`) — export if your record-
  keeping policy requires local copies.

## If something goes wrong mid-run

| Symptom | Action |
|---|---|
| Wrong month / wrong documents | Send `{"type": "user.interrupt"}`, then a corrective `user.message`. |
| Sub-agent stuck or looping | Check its thread events; interrupt and re-instruct the coordinator to re-delegate that module. |
| MCP auth failure (`session.error` mentioning xero-3cp) | Session continues; fix/rotate the vault credential (`ant beta:vaults:credentials update`), auth retries on the next idle→running transition. |
| Deployment run failed (no session) | `GET /v1/deployment_runs?deployment_id=...&has_error=true` → `error.type` (`vault_not_found`, `environment_archived`, ...) and fix the referenced resource. |
| Stream dropped while approvals pending | Reconnect with the consolidation pattern (stream, then list, dedupe) — pending confirmations are still waiting. |
