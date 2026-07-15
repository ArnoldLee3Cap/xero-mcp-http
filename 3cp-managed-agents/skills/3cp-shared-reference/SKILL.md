---
name: 3cp-shared-reference
description: >-
  Holds 3 Capital Partners' cross-cutting reference files that multiple skills read — currently
  gl-accounts.md (authoritative GL account codes) and recurring-register.md (locked
  recurring-transactions register used by 3cp-close-orchestrator, and by the soft gate in
  3cp-monthly-journals, 3cp-investment-treasury-close, expense-monthly-close-builder, and
  3cp-revenue-recognition). This skill has no workflow of its own — it exists purely so these
  shared files persist across sessions (a bare file outside any skill folder does not survive a
  new session; only files packaged inside an installed skill do). Use whenever a skill needs to
  read or update gl-accounts.md or recurring-register.md, when reconciling GL codes, or when the
  close orchestrator needs its checklist. Trigger phrases — GL accounts, chart of accounts,
  recurring register, shared reference. Any update to either file happens here first, then
  affected skills are repackaged.
---

# 3CP Shared Reference

Read-only data skill. No workflow logic — just two authoritative files consumed by other 3CP skills.

## Files

- `references/gl-accounts.md` — authoritative GL account codes. Any skill citing a GL code should
  point here rather than maintaining its own copy.
- `references/recurring-register.md` — locked recurring-transactions register (STATUS: LOCKED, 3
  July 2026). Source of truth for `3cp-close-orchestrator` (both modes) and the soft pre-close gate
  in the four module skills.

## Why this skill exists

Both files used to live as bare files in `/mnt/skills/user/shared/`, outside any skill's own folder.
That path is not packaged or persisted — only content bundled inside an installed skill survives
into a new session. Both files disappeared as a result. Moving them here (as `references/` inside
an actual skill) fixes that: whenever this skill is repackaged and reinstalled, its reference files
come with it.

## Update rules

1. Update the file here first — never maintain a second copy inside a consuming skill.
2. After any edit, repackage this skill (`3cp-shared-reference`) and reinstall it, or the change
   won't persist into the next session.
3. Consuming skills reference these files by path:
   `/mnt/skills/user/3cp-shared-reference/references/gl-accounts.md`
   `/mnt/skills/user/3cp-shared-reference/references/recurring-register.md`
   If any skill still points to the old `/mnt/skills/user/shared/` path, update that skill's
   reference and repackage it too.
