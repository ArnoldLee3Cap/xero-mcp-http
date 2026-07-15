---
name: 3cp-payroll-close
description: Prepare 3 Capital Partners' month-end payroll journal entries — salary, MPF (Mandatory Provident Fund), and rental allowance — from the monthly payroll report. Use this whenever the user is doing the monthly close and provides a payroll report, mentions payroll, salary, MPF, Mandatory Provident Fund, or rental allowance, or asks to book the month's staff pay. Net pay (gross salary + rental allowance − employee MPF withheld) pays from DBS HKD in-month; MPF (employer 478 + employee withheld) credits 802 MPF Payable at month-end and settles to Sun Life from CCB HKD on the 1st–2nd of the following month. Interns (e.g. Leo Zhang) appear under "Salary" in the payroll report but book to 477CI Consultants & Interns. Do NOT use for employee expense reimbursements (Expensify-driven — route to expense-monthly-close-builder). Bonus is accrued on crystallisation (DR 476 or against 893 if previously deferred) — confirm treatment with Arnold per instance.
---

# 3CP Payroll Close

> **Important**: This skill assists 3 Capital Partners ("the Company") with recurring month-end
> payroll journals. It does not provide financial, tax, or legal advice. It **prepares** journals
> only — it does **not** post to Xero (a separate posting skill, `3cp-xero-journal-poster`, pushes
> approved drafts). Every entry is a DRAFT and must be reviewed and signed off by a qualified
> accountant before posting.

> **Precondition — orchestrator gate**: Before preparing journals for a period, check whether
> `3cp-close-orchestrator` (Mode 1) has been run for that period this session. If it hasn't, say so
> and offer to run it first. If the user explicitly says to skip it and proceed anyway, proceed —
> this is a workflow recommendation, not a hard block.

Prepare the Company's monthly payroll journal from the payroll report, split by bank account per
the routing rules below, and cross-check against the Xero export for the period. Employee expense
reimbursements are out of scope — they are handled by `expense-monthly-close-builder`.

## Usage

```
/3cp-payroll-close <period>
```

- `period` — the accounting period (e.g. `2026-06`). The Company closes on the last calendar day
  of each month.

## Scope & entry model (confirmed against June 2026 actuals)

| Category | GL Code | Cash timing |
|---|---|---|
| Salary (gross) | 477 — except interns, who book to 477CI even though the payroll report lists them under "Salary" | Net pay leaves DBS HKD on/around month-end |
| Rental allowance | 475 (Salary - Rental Allowance) | Paid with net pay from DBS HKD |
| MPF — employer portion | 478 (Mandatory Provident Fund) | NOT paid in-month — credited to 802 MPF Payable |
| MPF — employee portion (withheld from salaries) | Inside gross 477; credit side goes to 802 | Same — 802 at month-end |
| MPF settlement | 802 clears | Sun Life payment from CCB HKD, 1st–2nd of the following month |

**The month-end journal (single HKD journal, DBS side):**

- DR 477 Salary (gross, non-intern)
- DR 477CI Consultants & Interns (intern gross, e.g. Leo Zhang)
- DR 475 Rental allowance
- DR 478 MPF employer
- CR **803 Wages Payable** — net pay owed (NEVER credit the bank account here: the Xero Manual
  Journal API **rejects bank-type accounts** — the Jun-26 lesson that held three journals)
- CR 802 MPF Payable — employer portion + employee portion withheld

Balance identity to verify every month: gross salary + rental allowance + employer MPF
= net pay (CR 803) + total MPF (employer + employee withheld, CR 802). June 2026 tied to the
penny on this identity — treat any imbalance as an error in reading the payroll report, not a plug.

**The bank legs are BANK TRANSACTIONS, not journals (updated Jul 2026 — `create-bank-transaction`
via the poster):**

1. **Net pay disbursement** — SPEND from DBS HKD, contact Staff Payroll, one line DR 803, reference
   `NETPAY-<MMMYY>` (e.g. `NETPAY-JUN26`). Posts AUTHORISED (live) and reconciles against the
   payroll FPS line on the DBS feed; it clears the journal's 803 credit.
2. **MPF settlement (following month, CCB side)** — when the Sun Life payment appears on the CCB
   statement (1st–2nd): SPEND from CCB HKD, contact Sun Life, one line DR 802, reference
   `MPFSETTLE-<MMMYY>` of the PRIOR month. Because CCB has no automatic bank feed, also emit the
   CCB statement-import CSV line for it (same pattern as `3cp-investment-treasury-close`). Note
   the settlement amount belongs to the PRIOR month's payroll — never match it against the current
   month's MPF figure (headcount changes make them differ).

Dedupe/verify both via `list-bank-transactions` on the reference before any retry (poster
guardrail 5).

**GL code correction (July 2026):** the shared reference previously had 475 and 477 swapped, and
was missing 478 entirely. This has been corrected in `/mnt/skills/user/3cp-shared-reference/references/gl-accounts.md`
— always read that file, not a local copy, and do not reuse any older cached mapping.

Read `references/payroll.md` before building — it covers the full entry logic, the DBS/CCB routing
split, the reimbursement boundary, and the extension points (bonus, deferred bonus).

## Boundary with other skills (avoid double-counting)

- **Employee expense reimbursements** (Expensify-driven, personal/cash out-of-pocket, paid from the
  same DBS account as salary) → **`expense-monthly-close-builder`**, not here. Confirmed with Arnold,
  July 2026: same reimbursement as always, no scope change. If the payroll report itself contains a
  reimbursement line, flag it — do not book it here.
- **Bonus / deferred bonus (893)** → not yet built. Flag and confirm treatment before booking anything
  under salary that looks like a bonus.

## Shared house conventions (apply here, consistent with other 3CP module skills)

1. **One workpaper**, following the standard tab order: `Cover` → `JE - Payroll` → `Xero Cross-Check`
   → `Review Checklist`.
2. **Cross-check to Xero.** Tie the payroll report totals to the prior period's Xero export for
   475/477/478; state the tie-out and any variance.
3. **Balance discipline.** Each journal (DBS and CCB, booked separately) balances to the penny with
   a control row and `=IF(ROUND(<debits>-<credits>,2)=0,"BALANCED","FAIL")` check.
4. **Memos.** Each line carries payroll period, employee count, and reference.
5. **Reversals.** None. 802 MPF Payable is not a reversing accrual — it clears against the actual
   Sun Life settlement the following month, not by auto-reversal.
6. **Status & sign-off.** Mark the workpaper `DRAFT — for accountant review`.
7. **Flag, don't fix silently.** Reimbursement lines inside the payroll report, bonus items, or a
   change in which bank account MPF pays from — surface in the Review Checklist, do not guess.

## Posting boundary & handoff (preparation only)

This skill **prepares** journals; it does **not** post. `3cp-xero-journal-poster` pushes approved
drafts to Xero.

- **Status: DRAFT.**
- **Unique reference per journal:** `3CP-PAY-<period>-DBS` (salary + rental allowance) and
  `3CP-PAY-<period>-CCB` (MPF). The posting skill checks the reference does not already exist before
  posting.
- **Structured payload.** Each journal: reference, period/date, narration, currency (HKD), no
  reversal, and lines of {account name, debit, credit}.
- **Split by bank account, not just currency.** Both journals are HKD, but DBS (auto-fed) and CCB
  (no auto-feed) need different reconciliation treatment — see `references/payroll.md` — so they
  must stay as two separate journals even though Option B currency-splitting elsewhere in the 3CP
  skill suite is usually about currency, not bank account.
- **Reconcile before post.** Only entries tying to the Xero export are eligible.

## Output formatting standards

Same as `3cp-monthly-journals`: Calibri 9–13, dark-navy title bands (`1F3864`, white text),
light-blue highlight (`D9E1F2`), yellow (`FFFF00`) for attention items. Build with the `xlsx` skill
and openpyxl; run `recalc.py` and confirm zero formula errors before sharing. Share via
`present_files`.

## Workflow

1. **Determine period.** Resolve `<period>`. Confirm if ambiguous.
2. **Read the payroll report** and the Xero export for the period.
3. **Read `references/payroll.md`** and follow the entry logic and bank-routing rules.
4. **Build the workpaper** — both journals (DBS, CCB), cross-check tab, review checklist.
5. **Cross-check** category totals to the Xero export; record PASS/REVIEW.
6. **Recalculate** and verify zero formula errors.
7. **Generate the Xero ManualJournal import CSV** (see Output 2 below) and, for the CCB journal only,
   the bank-statement import CSV line.
8. **Present** the files with a concise summary: entries, tie-outs, review flags, and which module
   (DBS/CCB) each journal belongs to.

## Output 2 — Xero ManualJournal import CSV

```
python3 scripts/payload_to_xero_mj_csv.py --payload <draft_journals.json> --out <Period>_ManualJournal_Xero.csv
```

Both journals are HKD — no `--rate` needed. Account codes resolve from
`references/chart-of-accounts.csv` (475/477/478 already present). A journal with any unresolvable
account is excluded and reported as an exception, per the script's standard behaviour.

## Output 3 — CCB bank-statement import CSV (MPF only)

Because CCB has no automatic feed, the MPF journal needs a matching statement line for reconciliation
— generate this the same way `3cp-investment-treasury-close` does for CCB (Output 4 in that skill),
using the MPF payment amount/date/reference. **Do not generate a statement-import line for the DBS
journal** — DBS is auto-fed and importing a statement for it would create a duplicate feed line.

## Standing notes

- **No financial, tax, or legal advice** — mechanical preparation only.
- **MPF payable model confirmed Jul 2026** (supersedes the original "no accrual, paid same month"
  design): the 1–2 day settlement lag means MPF is a real liability at month-end (802). This is not
  an estimate-type accrual — it is the exact withheld/owed amount.
- **MPF settlement routing is not permanent.** Currently Sun Life is paid from CCB HKD; migration
  to DBS is expected but undated. Confirm each period which account the settlement actually left.
- **Bonus (updated Jul 2026, supersedes December-only):** accrue when the bonus crystallises. A
  previously-deferred bonus pays out of 893; a newly crystallised one books DR 476 in its month.
  Confirm treatment with Arnold per instance; bonus payments may be in USD (book in original
  currency, Xero translates).
