# Module: Monthly Payroll

Prepare monthly journals for salary, MPF (Mandatory Provident Fund), and rental allowance from the
single monthly payroll report, and cross-check against the period Xero export.

## Inputs

1. **Payroll report** (Excel or PDF) — one file per month, containing per-employee salary, MPF
   employer contribution, and rental allowance in a single report. This report defines scope.
2. **Xero export** — to verify how the prior period's payroll was actually booked (amount and account).

## Scope boundary (critical — see SKILL.md)

Only **salary, MPF employer contribution, and rental allowance** from the payroll report belong here.

**Employee expense reimbursements are out of scope, even though they may pay out of the same DBS
account.** Reimbursements for employee-borne expenses are Expensify-driven and already handled by
`expense-monthly-close-builder` (the REIMB journal). Do not book them here — confirmed with Arnold,
July 2026: same reimbursement, same skill boundary as always. Booking it here too would double-count.

Bonus and deferred bonus (893) are **not yet in scope** — see Extension points below.

## Entries — net pay in-month; MPF via 802 payable (confirmed Jun 2026)

Net pay (gross salary + rental allowance − employee MPF withheld) leaves DBS HKD on/around
month-end. MPF — the employer portion (478) **plus** the employee portion withheld from salaries —
is owed but unpaid at month-end: credit **802 MPF Payable**, which clears when the Sun Life
payment leaves CCB HKD on the 1st–2nd of the following month.

Month-end journal (one HKD journal):

- `DR 477 Salary <gross, non-intern>`
- `DR 477CI Consultants & Interns <intern gross — interns appear under "Salary" in the payroll report but book to 477CI>`
- `DR 475 Salary - Rental Allowance <amount>`
- `DR 478 Mandatory Provident Fund <employer portion per payroll report>`
- `CR <DBS - HKD Current x1627> <net pay actually transferred>`
- `CR 802 MPF Payable <employer portion + employee portion withheld>`

**Balance identity (check every month, must tie to the penny):**
gross salary + rental allowance + employer MPF = net pay + total MPF (employer + employee withheld).
An imbalance means the payroll report was misread — never plug the difference.

Following month, when the Sun Life settlement appears on the CCB statement:

- `DR 802 MPF Payable / CR <CCB HKD>` — amount belongs to the PRIOR month's payroll; do not
  compare it to the current month's MPF (headcount changes make them differ).

Reversal: No (802 clears against the actual settlement, not by auto-reversal).
Memo: payroll report period, employee count, reference.

## Bank routing (critical — determines which module output applies)

Payroll is paid from two different accounts today, with different Xero feed behaviour. Get this
wrong and either the journal never reconciles (CCB) or a duplicate statement gets imported (DBS).

| Item | Bank account (today) | Auto-feed? | What else is needed |
|---|---|---|---|
| Net pay (salary + rental allowance − employee MPF) | DBS - HKD Current x1627 | **Yes** | Journal only. Xero auto-matches the feed line by amount/date/reference — do **not** import a DBS statement. |
| MPF settlement (clears 802, following month) | CCB HKD account | **No** | Settlement journal **plus** a CCB bank-statement import CSV line (same pattern as `3cp-investment-treasury-close` Output 4) — otherwise there is no feed line in Xero to reconcile against. |

**Planned migration:** MPF is expected to move from CCB to DBS in future. When that happens: change
the credit account for the MPF line to DBS, and drop the CCB statement-import step — MPF then behaves
exactly like salary. Check with Arnold each period which account MPF actually paid from before
assuming the old routing; do not hardcode "MPF = CCB" as a permanent rule.

**Journal references:**
- `3CP-PAY-<period>-DBS` — the month-end payroll journal (477/477CI/475/478 → DBS bank + 802).
- `3CP-PAY-<period>-MPFSETTLE` — the following-month settlement (DR 802 / CR CCB HKD), prepared
  when the CCB statement shows the Sun Life payment; emit the CCB statement-import CSV line with it.

## Xero classification cross-check

Compare the payroll report total (by category: salary, MPF, rental allowance) against the prior
period's Xero export for accounts 475/477/478. Mark PASS where amounts and classification tie;
mark REVIEW where a prior period shows something posted to the old (pre-correction) 475/477 mapping
— see the shared GL reference for the July 2026 code-swap correction. Flag rather than silently
reclassify any prior-period entries found on the wrong code.

## Flags to watch

- Any employee reimbursement line appearing inside the payroll report itself (not just the DBS bank
  statement) — flag and route to `expense-monthly-close-builder`, do not book here.
- Bonus (updated Jul 2026 — accrue on crystallisation, supersedes December-only): a
  previously-deferred bonus pays out of 893; a newly crystallised one books DR 476 in its month.
  May be USD-denominated (book in original currency, Xero translates). Confirm treatment with
  Arnold per instance — do not silently absorb into salary.
- Any month where MPF pays from an account other than the one assumed above (e.g. mid-migration) —
  confirm with Arnold before building the journal; do not guess which account is live that period.

## Workpaper tabs

`Cover` → `JE - Payroll` (both journals, each balancing to its own bank account) → `Xero Cross-Check`
(PASS/REVIEW per category) → `Review Checklist`.

## Posting reference (handoff)

Two journals per period → `3CP-PAY-<period>-DBS` (salary + rental allowance) and
`3CP-PAY-<period>-CCB` (MPF). Each single-currency (HKD), DRAFT, per SKILL.md → Posting boundary &
handoff. The CCB journal additionally needs its statement-import CSV line generated before posting
is reconciliation-complete.

## Extension points (not yet built)

- **Bonus / deferred bonus (893).** Year-end or discretionary bonus accrual — different timing
  profile (accrues before payment) from the three in-scope items. Add as a new section here, reusing
  the shared conventions, when Arnold provides a bonus schedule.
- **Employee insurance (477EI), consultants & interns (477CI).** Currently handled elsewhere (or
  not at all) — confirm scope with Arnold before folding into this skill.
