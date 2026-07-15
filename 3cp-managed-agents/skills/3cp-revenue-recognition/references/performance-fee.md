# Module: Performance Fee — year-end only (`--perf-fee`)

Performance fee is **not accrued** during the year, on prudence grounds. It is recognised **only at the December year-end close**, once it **crystallises** (becomes certain and measurable).

## Rule
- **Jan–Nov:** no performance-fee entry. If asked to accrue it mid-year, **decline and explain** the prudence basis — do not accrue.
- **December close only:** if performance fee has crystallised, recognise it:
  - `DR 623 Performance Fee Receivables  <amount>`
  - `CR 220 Revenue - Performance Fee  <amount>`
  - Reference `3CP-REV-<year>-12-PERF-<CCY>`; book in original currency; one currency per journal.
  - Code 623 confirmed via the authoritative shared GL reference (`/mnt/skills/user/3cp-shared-reference/references/gl-accounts.md`) — not TBD.

## Notes
- "Crystallised" means the performance fee is no longer contingent (the measurement period has ended and the hurdle/high-water-mark outcome is determined). Confirm crystallisation with the user before booking.
- Source of the amount is the Company's performance-fee computation (not this skill; not Addepar's management-fee export).
- Keep this module dormant outside December; the concept is retained so the year-end close picks it up.
