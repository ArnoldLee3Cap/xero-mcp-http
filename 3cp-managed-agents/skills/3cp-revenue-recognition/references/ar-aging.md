# Module: Aged Receivables maintenance (`--ar-aging`)

Maintain the aged receivables summary for fee receivables, combining **accrued (unbilled)** and **billed (trade)** receivables. This feeds the FRR (aged receivables attract haircuts and concentration tests), so it must reconcile.

## Inputs
- Revenue receivable list (by client: amounts, invoice/accrual dates, billed vs accrued, collections).
- The receivable GL balances (accrued + trade) for reconciliation.

## Procedure
1. For each open receivable, classify **accrued/unbilled** vs **billed** and date it (accrual month-end date for unbilled; invoice date for billed).
2. Age into buckets relative to period-end: **Current, 1–30, 31–60, 61–90, 90+ days**. (Given quarterly billing + ~1 month collection, expect material balances in the early buckets around the billing/collection cycle; genuine ageing past 90+ is a flag.)
3. Summarise by client and bucket; show accrued vs billed split.
4. **Reconcile:** total aged receivables = Accrued Management Fee Receivable + Trade Receivable per GL; and ties to the revenue receivable list. Surface any difference.
5. **Maintain both views** (this is the right approach, and not extra work — they're complementary):
   - **Billed/invoiced AR → Xero's native Aged Receivables.** Once the quarterly invoice is raised in Xero, Xero ages it automatically. No manual effort.
   - **Unbilled accrued AR → a maintained schedule.** Xero's native report can't see accrued income that has no invoice yet, so the skill keeps the accrued/unbilled aging from the revenue receivable list + the monthly accruals.
   - **Combined reconciled summary.** Produce one view = native billed AR + accrued schedule, reconciled to the receivable GL (Trade Receivable + Accrued Management Fee Receivable). This combined figure is what feeds the FRR. So "both" = Xero does the billed half for free; the skill maintains the accrued half and the combined reconciliation.

## Flags
- Receivable in 90+ with no collection — recoverability / FRR haircut implication; flag.
- Concentration: a single client dominating receivables — FRR concentration test; flag.
- Unbilled accrued that should have been billed (past the quarterly invoice date) — billing lag; flag.
- Difference between aged total and GL / receivable list — reconcile before relying on it.
