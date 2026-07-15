#!/usr/bin/env bash
# ============================================================================
# 3CP close — day-of-close trigger (data plane)
# ----------------------------------------------------------------------------
# Usage:
#   source ./3cp-close.ids.env
#   ./run-close.sh mode1     # document-intake audit (ad-hoc session)
#   ./run-close.sh mode2     # full close via manual deployment run
#   ./run-close.sh outputs <session_id>   # download workpaper + report
# ============================================================================
set -euo pipefail
: "${COORDINATOR_AGENT_ID:?source ./3cp-close.ids.env first}"

WORKSPACE_ID="${WORKSPACE_ID:-default}"   # swap for your Console workspace ID

case "${1:-}" in

mode1)
  # Mode 1 is an ad-hoc session (not the deployment): create session, send the
  # document-audit instruction, watch live.
  SID=$(ant beta:sessions create \
    --agent "{type: agent, id: $COORDINATOR_AGENT_ID, version: $COORDINATOR_AGENT_VER}" \
    --environment-id "$ENV_ID" \
    --vault-id "$VAULT_ID" \
    --title "3CP close — Mode 1 document intake $(date +%Y-%m)" \
    --transform id -r)
  echo "Session: $SID"
  echo "Trace:   https://platform.claude.com/workspaces/$WORKSPACE_ID/sessions/$SID"
  echo ">> Upload/mount this month's source documents to the session, then:"
  ant beta:sessions:events send --session-id "$SID" > /dev/null <<'YAML'
events:
  - type: user.message
    content:
      - type: text
        text: "Execute 3CP monthly close Mode 1: audit the provided source documents against recurring-register.md. Report covered vs missing items. Do not begin close execution."
YAML
  echo ">> Streaming (Ctrl-C to detach; session keeps running):"
  ant beta:sessions:events stream --session-id "$SID"
  ;;

mode2)
  # Manual deployment run — works while the deployment is paused.
  echo ">> Triggering manual run of deployment $DEPLOYMENT_ID"
  ant beta:deployments run --deployment-id "$DEPLOYMENT_ID" || {
    echo ">> CLI lacks 'deployments run'; raw-HTTP fallback:"
    curl -s -X POST "https://api.anthropic.com/v1/deployments/$DEPLOYMENT_ID/run" \
      -H "x-api-key: $ANTHROPIC_API_KEY" \
      -H "anthropic-version: 2023-06-01" \
      -H "anthropic-beta: managed-agents-2026-04-01"
  }
  # The run record carries the created session_id.
  sleep 3
  RUN_JSON=$(curl -s "https://api.anthropic.com/v1/deployment_runs?deployment_id=$DEPLOYMENT_ID&limit=1" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01")
  SID=$(echo "$RUN_JSON" | sed -n 's/.*"session_id"[: ]*"\([^"]*\)".*/\1/p')
  echo "Session: ${SID:-<not yet created — check deployment_runs for error.type>}"
  [ -n "${SID:-}" ] && echo "Trace:   https://platform.claude.com/workspaces/$WORKSPACE_ID/sessions/$SID"
  [ -n "${SID:-}" ] && ant beta:sessions:events stream --session-id "$SID"
  ;;

outputs)
  SID="${2:?usage: run-close.sh outputs <session_id>}"
  # Session outputs (workpaper + completeness report) land in
  # /mnt/session/outputs/ and are listed via the Files API with scope_id.
  # Needs BOTH beta headers (files + managed-agents).
  curl -s "https://api.anthropic.com/v1/files?scope_id=$SID" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: files-api-2025-04-14,managed-agents-2026-04-01" \
    | tee files.json
  echo
  echo ">> Download each with:"
  echo '   curl -s "https://api.anthropic.com/v1/files/<FILE_ID>/content" -H "x-api-key: $ANTHROPIC_API_KEY" -H "anthropic-version: 2023-06-01" -H "anthropic-beta: files-api-2025-04-14,managed-agents-2026-04-01" -o <name>.xlsx'
  ;;

*)
  echo "usage: run-close.sh {mode1|mode2|outputs <session_id>}"; exit 1 ;;
esac
