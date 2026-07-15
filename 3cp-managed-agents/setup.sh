#!/usr/bin/env bash
# ============================================================================
# 3CP Managed Agents — one-time provisioning (control plane)
# ----------------------------------------------------------------------------
# Run ONCE (then use versioned updates — see docs/versioning.md).
# Requires: `ant` CLI authenticated (ant auth status), `envsubst` (ships with
# Git for Windows / gettext), and the beta header managed-agents-2026-04-01
# (the `ant beta:` prefix sets it automatically).
#
# BEFORE RUNNING, set:
#   export XERO_MCP_URL="https://<your-xero-mcp-host>/mcp"   # see README flag #1
#   export XERO_MCP_TOKEN="<bearer token for that server>"    # or use OAuth shape below
#   export SKILLS_SRC_DIR="/path/to/packaged-skill-zips"      # see step 1
# ============================================================================
set -euo pipefail
cd "$(dirname "$0")"

: "${XERO_MCP_URL:?Set XERO_MCP_URL to the xero-3cp MCP server endpoint (Streamable HTTP)}"

IDS_FILE="./3cp-close.ids.env"
echo "# Generated $(date -u +%Y-%m-%dT%H:%M:%SZ) — IDs for the 3CP close deployment" > "$IDS_FILE"
save() { echo "export $1=\"$2\"" >> "$IDS_FILE"; echo "  $1=$2"; }

# ----------------------------------------------------------------------------
# 1. SKILLS — upload each packaged 3CP skill to the Skills API.
# ----------------------------------------------------------------------------
# Each skill folder (SKILL.md at root + reference files) must be uploaded as a
# custom skill. Verify the exact create flags on your CLI build with:
#   ant beta:skills create --help
# Raw-HTTP fallback (multipart; one files[] entry per file, paths preserved):
#   curl -s https://api.anthropic.com/v1/skills \
#     -H "x-api-key: $ANTHROPIC_API_KEY" -H "anthropic-version: 2023-06-01" \
#     -H "anthropic-beta: skills-2025-10-02" \
#     -F "display_title=3cp-payroll-close" \
#     -F "files[]=@./3cp-payroll-close/SKILL.md;filename=3cp-payroll-close/SKILL.md"
echo "== 1. Uploading skills =="
create_skill() {  # $1 = skill folder name under $SKILLS_SRC_DIR
  ant beta:skills create \
    --display-title "$1" \
    --file "${SKILLS_SRC_DIR:?Set SKILLS_SRC_DIR}/$1.zip" \
    --transform id -r
}
export SKILL_CLOSE_ORCHESTRATOR=$(create_skill "3cp-close-orchestrator")
export SKILL_SHARED_REFERENCE=$(create_skill "3cp-shared-reference")
export SKILL_XERO_POSTER=$(create_skill "3cp-xero-journal-poster")
export SKILL_PAYROLL=$(create_skill "3cp-payroll-close")
export SKILL_TREASURY=$(create_skill "3cp-investment-treasury-close")
export SKILL_REVENUE=$(create_skill "3cp-revenue-recognition")
export SKILL_EXPENSE=$(create_skill "expense-monthly-close-builder")
export SKILL_BANK_RECON=$(create_skill "3cp-bank-reconciliation-helper")
for v in SKILL_CLOSE_ORCHESTRATOR SKILL_SHARED_REFERENCE SKILL_XERO_POSTER \
         SKILL_PAYROLL SKILL_TREASURY SKILL_REVENUE SKILL_EXPENSE SKILL_BANK_RECON; do
  save "$v" "${!v}"
done

# ----------------------------------------------------------------------------
# 2. ENVIRONMENT
# ----------------------------------------------------------------------------
echo "== 2. Creating environment =="
ENV_ID=$(ant beta:environments create < environment/3cp-close.environment.yaml --transform id -r)
save ENV_ID "$ENV_ID"

# ----------------------------------------------------------------------------
# 3. VAULT + XERO CREDENTIAL
# ----------------------------------------------------------------------------
# The agent YAMLs declare the xero-3cp MCP server WITHOUT auth; the credential
# lives here and is attached to each session via vault_ids. It is injected at
# Anthropic's egress proxy and never enters the container — code the agents
# run cannot read or exfiltrate it.
echo "== 3. Creating vault + credential =="
VAULT_ID=$(ant beta:vaults create --display-name "3CP Xero (production)" --transform id -r)
save VAULT_ID "$VAULT_ID"

# static_bearer shown; if your xero-3cp MCP server uses OAuth with refresh,
# use the mcp_oauth shape instead (access_token/expires_at/refresh block) so
# Anthropic auto-refreshes the token. NOTE: hosted MCP servers usually want an
# OAuth bearer, NOT a Xero REST API key — these are different auth systems.
ant beta:vaults:credentials create --vault-id "$VAULT_ID" <<EOF
display_name: xero-3cp MCP token
auth:
  type: static_bearer
  mcp_server_url: "$XERO_MCP_URL"
  token: "${XERO_MCP_TOKEN:?Set XERO_MCP_TOKEN}"
EOF

# ----------------------------------------------------------------------------
# 4. SUB-AGENTS (create first — the coordinator roster needs their IDs)
# ----------------------------------------------------------------------------
echo "== 4. Creating sub-agents =="
# Only these variables are substituted; any other \${...} text in the YAML
# comments is left untouched.
SUBST='$XERO_MCP_URL $SKILL_CLOSE_ORCHESTRATOR $SKILL_SHARED_REFERENCE $SKILL_XERO_POSTER $SKILL_PAYROLL $SKILL_TREASURY $SKILL_REVENUE $SKILL_EXPENSE $SKILL_BANK_RECON'
create_agent() {  # $1 = agent yaml path -> prints "id version"
  local id ver
  id=$(envsubst "$SUBST" < "$1" | ant beta:agents create --transform id -r)
  ver=$(ant beta:agents retrieve --agent-id "$id" --transform version -r)
  echo "$id $ver"
}
read -r PAYROLL_AGENT_ID  PAYROLL_AGENT_VER  <<< "$(create_agent agents/3cp-payroll-close.agent.yaml)"
read -r TREASURY_AGENT_ID TREASURY_AGENT_VER <<< "$(create_agent agents/3cp-treasury-close.agent.yaml)"
read -r REVENUE_AGENT_ID  REVENUE_AGENT_VER  <<< "$(create_agent agents/3cp-revenue-close.agent.yaml)"
read -r EXPENSE_AGENT_ID  EXPENSE_AGENT_VER  <<< "$(create_agent agents/3cp-expense-close.agent.yaml)"
read -r RECON_AGENT_ID    RECON_AGENT_VER    <<< "$(create_agent agents/3cp-bank-recon.agent.yaml)"
export PAYROLL_AGENT_ID PAYROLL_AGENT_VER TREASURY_AGENT_ID TREASURY_AGENT_VER \
       REVENUE_AGENT_ID REVENUE_AGENT_VER EXPENSE_AGENT_ID EXPENSE_AGENT_VER \
       RECON_AGENT_ID RECON_AGENT_VER
for v in PAYROLL_AGENT_ID PAYROLL_AGENT_VER TREASURY_AGENT_ID TREASURY_AGENT_VER \
         REVENUE_AGENT_ID REVENUE_AGENT_VER EXPENSE_AGENT_ID EXPENSE_AGENT_VER \
         RECON_AGENT_ID RECON_AGENT_VER; do
  save "$v" "${!v}"
done

# ----------------------------------------------------------------------------
# 5. COORDINATOR (roster pinned to the sub-agent versions captured above)
# ----------------------------------------------------------------------------
echo "== 5. Creating coordinator =="
COORD_SUBST="$SUBST \$PAYROLL_AGENT_ID \$PAYROLL_AGENT_VER \$TREASURY_AGENT_ID \$TREASURY_AGENT_VER \$REVENUE_AGENT_ID \$REVENUE_AGENT_VER \$EXPENSE_AGENT_ID \$EXPENSE_AGENT_VER \$RECON_AGENT_ID \$RECON_AGENT_VER"
COORDINATOR_AGENT_ID=$(envsubst "$COORD_SUBST" < agents/3cp-close-coordinator.agent.yaml \
  | ant beta:agents create --transform id -r)
COORDINATOR_AGENT_VER=$(ant beta:agents retrieve --agent-id "$COORDINATOR_AGENT_ID" --transform version -r)
save COORDINATOR_AGENT_ID "$COORDINATOR_AGENT_ID"
save COORDINATOR_AGENT_VER "$COORDINATOR_AGENT_VER"

# ----------------------------------------------------------------------------
# 6. DEPLOYMENT — created PAUSED; triggered manually (no calendar cron).
# ----------------------------------------------------------------------------
# RATIONALE: sources arrive on an irregular schedule, so there is no cron
# trigger in practice. The API requires a schedule on create, so we set a
# monthly placeholder and PAUSE immediately — a paused deployment never fires
# on schedule but STILL ACCEPTS MANUAL RUNS (POST /v1/deployments/{id}/run).
# Verify your CLI build exposes deployments (ant beta:deployments --help);
# raw-HTTP fallback shown in run-close.sh.
echo "== 6. Creating deployment (paused; manual-run only) =="
DEPLOYMENT_ID=$(ant beta:deployments create --transform id -r <<EOF
name: 3CP monthly close (Mode 2)
agent:
  type: agent
  id: $COORDINATOR_AGENT_ID
  version: $COORDINATOR_AGENT_VER
environment_id: $ENV_ID
vault_ids:
  - $VAULT_ID
initial_events:
  - type: user.message
    content:
      - type: text
        text: "Execute 3CP monthly close Mode 2: prepare payroll, treasury, revenue, expense, and reconciliation journals in parallel. Deliver draft workpaper and completeness report. Flag any ambiguous items for user review before proceeding to Xero posting."
schedule:
  type: cron
  expression: "0 9 28 * *"        # placeholder — never fires (paused below)
  timezone: "Asia/Hong_Kong"
EOF
)
ant beta:deployments pause --deployment-id "$DEPLOYMENT_ID"
save DEPLOYMENT_ID "$DEPLOYMENT_ID"

echo
echo "Done. IDs written to $IDS_FILE — commit the YAMLs, keep the ids file safe."
echo "Day-of-close: source $IDS_FILE && ./run-close.sh"
