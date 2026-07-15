# xero-3cp as a Streamable-HTTP MCP endpoint

Solves README blocker #1. Xero does **not** offer a hosted remote MCP server
(confirmed against their AI toolkit docs, July 2026 — the official
`@xeroapi/xero-mcp-server` is local/stdio only), so we expose your existing
server ourselves: `supergateway` wraps stdio → Streamable HTTP, and a Caddy
sidecar enforces a bearer token that matches the vault's `static_bearer`
credential.

```
Anthropic session (managed agents)
   │  Authorization: Bearer <MCP_BEARER_TOKEN>   ← injected from vault at egress
   ▼
Caddy :9000  ── 401 anything without the exact token
   ▼
supergateway :8000  ── stdio bridge
   ▼
@xeroapi/xero-mcp-server (Xero Custom Connection creds in env)
```

The "locked-down, writes-gated" property of your old setup is preserved by
**two independent layers** in the new design: (1) the OAuth scopes on the Xero
Custom Connection (unchanged), and (2) the deny-by-default per-agent tool
allowlists + `always_ask` gates in `../agents/*.yaml` — sub-agents physically
cannot see any `create-*` tool, and the coordinator can't call one without a
per-call human approval.

## Where to run it — pick one

**A. This PC + Cloudflare Tunnel (fastest to working, $0).**
Good enough for v1 since close runs are attended anyway (you're online
approving `requires_action` events).

```bash
cp .env.example .env    # fill creds; openssl rand -hex 32 for MCP_BEARER_TOKEN
docker compose up -d
cloudflared tunnel --url http://localhost:9000     # quick tunnel, or a named
                                                   # tunnel + your own domain
# → XERO_MCP_URL = https://<tunnel-host>/mcp
```

Caveats: the PC must be on during a close; quick-tunnel URLs change per run
(a named tunnel on a domain you own gives a stable URL — needed because the
vault credential is keyed to the exact URL).

**B. Small cloud container (recommended steady state).**
Fly.io / Azure Container Apps / Cloud Run — deploy the same image, set the
three Xero vars + `MCP_BEARER_TOKEN` as platform secrets, put the platform's
TLS in front (then Caddy can even be dropped and its check moved to the
platform gateway). Stable HTTPS URL → `XERO_MCP_URL`.

**C. No hosting at all — custom-tools bridge (fallback).**
Replace `mcp_toolset` in the agent YAMLs with `custom` tool declarations and
run a small orchestrator on this PC that holds the Xero credential, executes
each `agent.custom_tool_use` against the local stdio server, and replies with
`user.custom_tool_result`. Zero exposed endpoints, but an extra process that
must stay attached to the session stream every close. Choose this only if
exposing any endpoint is unacceptable.

## Wire it into the deployment

```bash
export XERO_MCP_URL="https://<your-host>/mcp"
export XERO_MCP_TOKEN="<the MCP_BEARER_TOKEN value>"
./setup.sh    # creates the vault static_bearer credential keyed to this URL
```

Smoke-test before the first close run:

```bash
curl -s -X POST "$XERO_MCP_URL" \
  -H "Authorization: Bearer $XERO_MCP_TOKEN" \
  -H "content-type: application/json" -H "accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | head -c 400
# expect a tools list; then repeat WITHOUT the header and expect 401
```

## Security notes (do these)

1. **Rotate the Xero client secret** at developer.xero.com after migrating —
   it currently sits in plaintext in `claude_desktop_config.json` on this PC
   (as does the Expensify partner secret; consider moving both).
2. `MCP_BEARER_TOKEN` and the Xero secret live only in `.env` (gitignored)
   and the Anthropic vault. Never in the agent YAMLs or session messages.
3. In the environment YAML, `allow_mcp_servers: true` already permits egress
   to this host; if you later switch to an `allowed_hosts` list, add it there.
4. If the endpoint URL ever changes, the vault credential must be re-created
   (credentials are keyed to the exact MCP server URL) and the agents'
   `mcp_servers[].url` updated → new agent versions.
