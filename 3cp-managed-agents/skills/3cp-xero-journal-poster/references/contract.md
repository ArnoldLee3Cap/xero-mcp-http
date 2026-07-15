# Journal payload contract (consumed by this skill)

All 3CP prep skills emit this shape so one poster can consume them. JSON.

```json
{
  "contract_version": "1.0",
  "entity": "3 Capital Partners Limited",
  "source_skill": "3cp-monthly-journals",
  "period": "2026-04",
  "period_end": "2026-04-30",
  "target": {"system": "Xero", "post_as": "DRAFT", "auto_approve": false},
  "journals": [
    {
      "reference": "3CP-MJ-2026-04-LEASE-INT",
      "status": "DRAFT",
      "date": "2026-04-30",
      "currency": "HKD",
      "narration": "…",
      "reversal": {"flag": false, "date": null},
      "lines": [
        {"account": "Interest on Lease Liabilities", "debit": 7821.00, "credit": 0.00},
        {"account": "Lease Liability",                "debit": 0.00,   "credit": 7821.00}
      ]
    }
  ]
}
```

## Field rules

- **reference** — unique, idempotent key. Format `3CP-<MODULE>-<period>-<segment>[-<CCY>]`. The poster dedupes on this.
- **status** — `DRAFT` (eligible to post) or `HOLD` (excluded; carries `hold_reason`). The poster never posts a `HOLD` journal.
- **currency** — one currency per journal (Option B). HKD or USD. Non-base currencies post in their currency; Xero applies its FX rate on posting. The payload never carries a rate or an HKD-equivalent for a USD journal.
- **reversal** — `{flag, date}`. If `flag` is true, the posting integration sets the journal to auto-reverse on `date` (Xero supports a reversing date on manual journals).
- **lines** — each `{account, debit, credit}`; exactly one of debit/credit is non-zero. Must balance within the journal's currency.

## Validation the poster enforces

- Debits = credits **within each currency** (never summed across currencies).
- Every `account` resolves to a Xero account code/ID before the write call.
- `reference` not already present in Xero (idempotency).
- `status == DRAFT` (HOLD items are reported, not posted).
