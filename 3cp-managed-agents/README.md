# 3CP Managed Agents — Month-End Close Orchestrator

Complete Anthropic Managed Agents configuration for 3 Capital Partners
Limited's month-end close: a coordinator + five module sub-agents, provisioned
from version-controlled YAML via the `ant` CLI, triggered on demand through a
paused deployment's manual-run endpoint. Beta header everywhere:
`managed-agents-2026-04-01` (set automatically by `ant beta:` and the SDKs).

## Layout

```
environment/3cp-close.environment.yaml   shared container template (limited egress)
agents/3cp-close-coordinator.agent.yaml  Opus 4.8 · multiagent roster · always_ask Xero gate
agents/3cp-payroll-close.agent.yaml      Opus 4.8 · file+bash only · no MCP
agents/3cp-treasury-close.agent.yaml     Opus 4.8 · reads: list-accounts, list-trial-balance
agents/3cp-revenue-close.agent.yaml      Opus 4.8 · reads: invoices, aged AR, contacts, TB
agents/3cp-expense-close.agent.yaml      Opus 4.8 · reads: TB, manual journals, accounts
agents/3cp-bank-recon.agent.yaml         Haiku 4.5 · reads: list-bank-transactions only
setup.sh                                 one-time provisioning (skills→env→vault→agents→deployment)
run-close.sh                             day-of-close: mode1 / mode2 / outputs
docs/session-event-handling.md           requires_action → user.tool_confirmation flow (curl + Python)
docs/versioning.md                       skill→sub-agent→roster→deployment version bumps, rollback
docs/runbook.md                          day-of-close procedure + failure table
```

## Order of operations

1. Package each 3CP skill folder (SKILL.md at root) as a zip.
2. `export XERO_MCP_URL=... XERO_MCP_TOKEN=... SKILLS_SRC_DIR=...`
3. `./setup.sh` — writes all IDs to `3cp-close.ids.env`.
4. Day of close: `source 3cp-close.ids.env && ./run-close.sh mode1`, then
   `./run-close.sh mode2` (see `docs/runbook.md`).

## Permission model (summary of the decisions commented in each YAML)

| Layer | Policy | Why |
|---|---|---|
| Built-in toolset (all agents) | `always_allow` | Acts only inside the sandboxed, limited-egress container; gating file reads makes runs un-drivable. |
| Payroll agent web tools | **disabled** | Most sensitive data in the close; no legitimate network use. |
| Sub-agent Xero tools | Narrow read-only allowlists, `always_allow`, deny-by-default | Reads can't mutate the ledger; auto-allow keeps the 5-way parallel fan-out unattended. Every `create-*` tool is unavailable to sub-agents. |
| Coordinator Xero tools | Reads **and** 3 `create-*` draft tools, all `always_ask` | Conservative gate: every ledger touch at orchestration level produces a `requires_action` pause + human confirmation in the event audit trail. |
| Xero credential | Vault, attached per-session via `vault_ids` | Injected at Anthropic's egress proxy; never enters the container. |

## Design decisions & deviations from the build prompt

1. **Coordinator "read-only" vs the runbook's draft posting.** The prompt says
   the coordinator has read-only Xero tools, but its own runbook has approved
   `requires_action` events posting draft journals. Resolution: the three
   draft `create-*` tools are enabled on the coordinator but `always_ask` —
   nothing writes without a per-call approval. To make it strictly read-only,
   delete those three lines and post via a separate manual session.
2. **Mode 1's "document audit sub-agent"** isn't defined in the spec. The
   roster includes `{type: "self"}` and the coordinator carries the
   `3cp-close-orchestrator` skill, so Mode 1 spawns a self-copy for the audit.
3. **Coordinator skills.** Spec said "none directly", but the completeness
   checklist (`3cp-shared-reference`), Mode 1 (`3cp-close-orchestrator`) and
   draft-posting contract (`3cp-xero-journal-poster`) require the three skills
   attached. All five sub-agents also carry `3cp-shared-reference`.
4. **Deployment with no cron.** The API requires a schedule on create, so the
   deployment carries a placeholder monthly cron and is **paused immediately**
   — paused deployments never fire on schedule but still accept manual runs
   (`POST /v1/deployments/{id}/run`), which matches the "manual on-demand"
   trigger in the spec.
5. **The spec's "four sub-agents"** is a miscount — it defines five; all five
   are rostered and named in the Mode 2 initial message.

## ⚠️ Go-live blockers — status

1. **xero-3cp MCP endpoint URL — SCAFFOLDED, deploy pending.** The current
   xero-3cp is the official `@xeroapi/xero-mcp-server` v0.0.16 running locally
   over stdio (`Documents\xero-mcp-server`, Xero Custom Connection). Xero has
   no hosted remote MCP (confirmed July 2026), so `xero-mcp-http/` wraps it as
   a bearer-gated Streamable-HTTP endpoint (supergateway + Caddy). Pick a host
   (local+cloudflared / small cloud container / custom-tools fallback) — see
   `xero-mcp-http/README.md` — then set `XERO_MCP_URL` + `XERO_MCP_TOKEN`.
2. **Skill zips — DONE.** All eight skills are packaged in `skills/*.zip`
   (copied from the locally-synced claude.ai skill store). Upload happens in
   setup.sh step 1 once auth exists; set `SKILLS_SRC_DIR=./skills`.
3. **`ant` CLI — NOT INSTALLED (user action).** Install from
   github.com/anthropics/anthropic-cli/releases (windows_amd64) or
   `go install github.com/anthropics/anthropic-cli/cmd/ant@latest`, then run
   `ant auth login` (interactive browser OAuth — must be run by a human).
   No-CLI fallback: create a Console API key and `export ANTHROPIC_API_KEY`;
   run-close.sh's curl paths work with it, and setup.sh's ant calls can be
   ported to raw HTTP on request. Deployments support: check
   `ant beta:deployments --help` after install; raw-HTTP fallback included.
4. **Browser automation (`3cp-xero-ui-operator`).** Browser sessions are not
   part of the Managed Agents toolset — statement CSV imports, reconcile-tab
   clicking, and draft→Posted promotion remain Claude Code / manual steps
   (runbook step 5). Placeholder for future integration.
5. **Document delivery into sessions.** Mode 1/Mode 2 sources must be attached
   as session `resources` (Files API upload → `{type: file, file_id,
   mount_path}`) or added via the Console. If you want the deployment's manual
   run to include the month's files automatically, add a small pre-step that
   uploads them and recreates the deployment's `resources` — or switch Mode 2
   to an ad-hoc session like mode1 and pass `--resource` flags.

## Test in demo before running live

Run the whole stack once against the **Demo Xero org** first:

1. Duplicate the vault with a credential pointing at a demo-org MCP endpoint
   (or the same server scoped to the demo org); create a second deployment
   `3CP close (DEMO)` referencing the same coordinator version + demo vault.
2. Safe to test end-to-end in demo: the 5-way parallel fan-out, workpaper +
   completeness synthesis, the halt-on-ambiguity behavior (feed it a truncated
   payee on purpose), and the full `requires_action` → allow → draft-created
   loop — drafts in the demo org are disposable.
3. Also testable with **no Xero at all**: payroll (no MCP) and the synthesis
   formatting — upload sample documents and run Mode 2 with the vault omitted;
   MCP-dependent modules will flag auth errors but the orchestration paths
   still exercise.
4. Only after the demo run ties out: point the vault credential at production
   and do the first live month with a human watching the stream throughout.
