# Version & Update Procedure

Agents are immutable per version: every `agents update` creates a new version;
sessions pin to a version at creation. The coordinator's roster pins each
sub-agent's version, so updates flow **bottom-up: skill → sub-agent →
coordinator roster → deployment** (the deployment pins the coordinator
version). Nothing running mid-close ever changes under you.

## Worked example: shipping `expense-monthly-close-builder` v2

```bash
source ./3cp-close.ids.env

# 1. New SKILL version (skills are versioned independently of agents)
ant beta:skills:versions create --skill-id "$SKILL_EXPENSE" \
  --file ./skills/expense-monthly-close-builder-v2.zip
# If your agents reference version "latest" you could stop here — but for a
# regulated close, pin explicitly (next step) so each close is reproducible.

# 2. Bump the SUB-AGENT to reference the new skill version.
# update requires the current version as an optimistic lock.
CUR_VER=$(ant beta:agents retrieve --agent-id "$EXPENSE_AGENT_ID" --transform version -r)
envsubst "$SUBST" < agents/3cp-expense-close.agent.yaml \
  | ant beta:agents update --agent-id "$EXPENSE_AGENT_ID" --version "$CUR_VER"
EXPENSE_AGENT_VER=$(ant beta:agents retrieve --agent-id "$EXPENSE_AGENT_ID" --transform version -r)

# 3. Bump the COORDINATOR roster pin -> new coordinator version.
CUR_COORD_VER=$(ant beta:agents retrieve --agent-id "$COORDINATOR_AGENT_ID" --transform version -r)
export EXPENSE_AGENT_VER   # picked up by envsubst in the coordinator template
envsubst "$COORD_SUBST" < agents/3cp-close-coordinator.agent.yaml \
  | ant beta:agents update --agent-id "$COORDINATOR_AGENT_ID" --version "$CUR_COORD_VER"
COORDINATOR_AGENT_VER=$(ant beta:agents retrieve --agent-id "$COORDINATOR_AGENT_ID" --transform version -r)

# 4. Re-point the DEPLOYMENT at the new coordinator version.
# Deployments pin the agent version set at create; update the deployment (or
# archive + recreate it) so the next manual run uses the new pin:
curl -s -X POST "https://api.anthropic.com/v1/deployments/$DEPLOYMENT_ID" \
  -H "x-api-key: $ANTHROPIC_API_KEY" -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: managed-agents-2026-04-01" -H "content-type: application/json" \
  -d "{\"agent\": {\"type\": \"agent\", \"id\": \"$COORDINATOR_AGENT_ID\", \"version\": $COORDINATOR_AGENT_VER}}"

# 5. Record the new pins.
sed -i "s/^export EXPENSE_AGENT_VER=.*/export EXPENSE_AGENT_VER=\"$EXPENSE_AGENT_VER\"/" 3cp-close.ids.env
sed -i "s/^export COORDINATOR_AGENT_VER=.*/export COORDINATOR_AGENT_VER=\"$COORDINATOR_AGENT_VER\"/" 3cp-close.ids.env
```

## Inspecting version history

```bash
# All versions of an agent (audit trail of config changes)
ant beta:agents:versions list --agent-id "$COORDINATOR_AGENT_ID" \
  --transform '{version,updated_at}' --format jsonl

# What a given close ran on: retrieve the session — its agent snapshot carries
# id + version; sub-agent snapshots are on each thread:
ant beta:sessions retrieve --session-id "$SID" --transform '{agent:agent}'
```

## Rules of thumb

- **Update, don't re-create.** Same persona, tweaked behavior → `agents
  update` (new version). A genuinely different agent → new `agents create`.
  Never call `agents create` in the day-of-close path.
- **Rollback** = re-pin the coordinator roster (or the deployment) to the
  prior version number. Old versions are immutable and always available.
- **In-flight sessions are safe.** A session keeps the version it was created
  with; updates only affect sessions created afterwards.
- **Archive is permanent** (no unarchive; new sessions can't reference an
  archived agent). Never archive as cleanup — old versions cost nothing.
- **YAML is the source of truth.** Commit `agents/*.yaml` to git; every update
  should be a rendered template applied with `ant beta:agents update`, so git
  history and Anthropic version history stay in lockstep.
