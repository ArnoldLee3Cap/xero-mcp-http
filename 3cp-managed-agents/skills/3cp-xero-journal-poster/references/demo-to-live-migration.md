# Demo → Live Migration Checklist (run ONCE, fully, before the first live-org posting)

The entire pipeline was validated against Demo Company (Global). Demo's chart of accounts, base
currency (USD vs 3CP's HKD), bank accounts and balances all differ from the live org. One bad code
mapping posts a full month to the wrong account. Complete every step; do not post live until all ✔.

## A. Connection & environment
1. Switch org via switch-org.mjs; confirm list-organisation-details shows the LIVE 3CP org
   (Is Demo Company: false, base currency HKD, correct legal name).
2. Confirm the tool-factory allowlist is active (16 tools) — re-apply after any xero-mcp-server
   upgrade, per standing rule.

## B. Chart-of-accounts validation (scripted, not eyeballed)
3. Pull live COA (list-accounts). Diff EVERY account code referenced in EVERY skill's
   chart-of-accounts.csv and reference files against it: existence, name, type, status (not
   archived). Codes to verify explicitly: 200 220 270 271 415 416 417 418 433 438 440 469 470 471
   475 476 477 477CI 477EI 478 489 498-1 505 506 620 622 640 651 705 711 721 731 741 802 835 870
   871 872 880 899, PEP receivables (657/658), AMEX Clearing, AMEX Unsubmitted Suspense, 6410.
4. Bank accounts: confirm exact Xero names/IDs for DBS HKD x1627, DBS USD x1663, CCB HKD 634,
   CCB USD Savings 642, CCB Time Deposit 1/2, any DBS-side TD account, IBKR — transfers fail or
   mispost on name mismatch.
5. Tax settings: manual journals TaxType NONE / invoices as configured; tracking categories if any.

## C. Opening-state verification (things Demo could never validate)
6. AMEX Unsubmitted Suspense opening balance and composition — releases planned in workpapers must
   exist in it.
7. 870 / 871 / 640 / 872 balances vs the prior IBKR statement.
8. 620 balance vs the prepayment schedule; 802/835 in expected post-settlement state.
9. Confirm prior-month accrual entries exist where June logic assumes them (e.g. May dividend
   accrual incl. its 87.09 WHT; May IT accrual reversal).

## D. First live close = parallel run
10. Produce the skill-generated workpaper AND the manual close independently; diff line by line;
    investigate every difference to root cause before posting anything.
11. Post as DRAFT only; human reviews in Xero; promotion to Posted stays manual.
12. Statement imports (CCB/IBKR CSVs) are manual UI imports — NEVER also create-bank-transaction
    for the same lines (double-book).

## E. After first successful live close
13. Update subledger-schedules.md with verified live opening balances; note the migration date in
    the skill changelog.

## F. AMEX convention transition (added 9-Jul-26 — clearing/suspense model adopted)
14. Pull each per-card AMEX account's ledger; verify balance = paid-but-unapproved charges
    (investigate any unexplained residue first — do not blind-reclass).
15. One-time reclass journal: DR AMEX Unsubmitted Suspense / CR each card account to zero.
    This SEEDS the suspense opening balance (closes the "opening unknown" flag).
16. Reconfigure or disable the Expensify→Xero auto-posting to card accounts BEFORE the first
    skill-produced journal posts — otherwise every card expense double-counts.
17. Archive the per-card accounts; create/verify "AMEX Clearing" and "AMEX Unsubmitted Suspense"
    accounts exist in the live COA.
18. First month after transition: reconcile suspense releases against the seeded composition.
