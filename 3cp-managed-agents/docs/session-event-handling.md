# Session Event Handling — permission-policy flow

How a 3CP close session pauses on gated Xero calls and how you approve or deny
them. All examples assume the `managed-agents-2026-04-01` beta header (the SDK
and `ant beta:` prefix set it automatically).

## The flow

1. **Coordinator attempts a gated tool** (every `xero-3cp` tool on the
   coordinator is `always_ask` — including the three `create-*` draft tools).
2. The stream emits an `agent.tool_use` (or `agent.mcp_tool_use`) event with
   `evaluated_permission: "ask"`, then the session goes idle with
   `session.status_idle` whose `stop_reason` is:

   ```json
   {
     "type": "session.status_idle",
     "id": "sevt_456",
     "stop_reason": { "type": "requires_action", "event_ids": ["sevt_123"] }
   }
   ```

   `stop_reason.event_ids` lists every pending confirmation. **The ID you
   confirm with is the event ID (`sevt_...`), not a `toolu_...` ID.**
3. **You send `user.tool_confirmation`** — one per pending event — with
   `result: "allow"` or `"deny"` (deny may carry a `deny_message` the agent
   sees, so it can adjust).
4. The session resumes `running`, executes (or skips) the tool, and continues.

## Approve / deny — curl

```bash
# Approve a pending Xero write
curl -s -X POST "https://api.anthropic.com/v1/sessions/$SESSION_ID/events" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: managed-agents-2026-04-01" \
  -H "content-type: application/json" \
  -d '{
    "events": [
      { "type": "user.tool_confirmation",
        "tool_use_id": "sevt_123",
        "result": "allow" }
    ]
  }'

# Deny with guidance
curl -s -X POST "https://api.anthropic.com/v1/sessions/$SESSION_ID/events" \
  ... \
  -d '{
    "events": [
      { "type": "user.tool_confirmation",
        "tool_use_id": "sevt_123",
        "result": "deny",
        "deny_message": "Wrong period — re-prepare against June, not May." }
    ]
  }'
```

## Approve loop — Python SDK

```python
import anthropic

client = anthropic.Anthropic()
SESSION_ID = "sesn_..."

pending = {}  # event_id -> event (for showing the user what they're approving)

with client.beta.sessions.events.stream(session_id=SESSION_ID) as stream:
    for event in stream:
        # A gated tool call — remember it so we can display tool name + input.
        if event.type in ("agent.tool_use", "agent.mcp_tool_use") and \
           getattr(event, "evaluated_permission", None) == "ask":
            pending[event.id] = event

        elif event.type == "session.status_idle":
            sr = event.stop_reason
            if sr.type == "requires_action":
                confirmations = []
                for eid in sr.event_ids:
                    ev = pending.get(eid)
                    print(f"PENDING {eid}: {getattr(ev, 'name', '?')} "
                          f"input={getattr(ev, 'input', {})}")
                    answer = input("allow/deny> ").strip()
                    c = {"type": "user.tool_confirmation",
                         "tool_use_id": eid,
                         "result": "allow" if answer == "allow" else "deny"}
                    # Sub-agent-originated confirmations are cross-posted to the
                    # primary thread with a session_thread_id — echo it back.
                    tid = getattr(ev, "session_thread_id", None)
                    if tid:
                        c["session_thread_id"] = tid
                    confirmations.append(c)
                client.beta.sessions.events.send(
                    session_id=SESSION_ID, events=confirmations)
                continue          # session resumes; keep streaming
            break                 # end_turn / retries_exhausted — terminal

        elif event.type == "session.status_terminated":
            break
```

## Gotchas that will bite in production

- **Don't break on the first `status_idle`.** The session idles transiently
  while awaiting confirmations and custom-tool results. Break only when
  `stop_reason.type` is `end_turn` or `retries_exhausted`, or on
  `session.status_terminated`.
- **Stream-first.** Open the stream **before** sending the kickoff message —
  the stream has no replay; events emitted before it opens are only visible
  via `events.list`.
- **Reconnect with consolidation.** If your stream drops while a confirmation
  is pending, the session deadlocks waiting for you. On every (re)connect:
  open the stream, then `GET /v1/sessions/{id}/events` (paginated), dedupe by
  event `id`, answer anything still pending, then tail live.
- **Multiagent cross-posting.** When a *sub-agent* hits a gate (none do in
  this design — sub-agents are `always_allow` on narrow read allowlists — but
  it applies if you tighten them), the `agent.tool_use` is cross-posted to the
  primary session stream carrying `session_thread_id`. Echo that field on your
  confirmation, as in the Python example.
- **Sub-agent drill-down for audit.** The primary stream shows a condensed
  view of sub-agent activity. For the full per-module trace:
  `GET /v1/sessions/{sid}/threads` to list thread IDs, then
  `GET /v1/sessions/{sid}/threads/{tid}/events` — or in the Console session
  view. Thread event history is the audit trail for each module's journal.
- **Steering mid-run.** You can send `user.message` at any time (queued, in
  order). `{"type": "user.interrupt"}` jumps the queue and halts at a safe
  boundary — use for "stop, wrong month".
