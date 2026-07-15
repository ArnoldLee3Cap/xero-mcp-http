# Module: IBKR Valuation & Income (`--broker`)

Prepare the month-end broker journal in **USD** from the Interactive Brokers activity statement, and reconcile the IBKR NAV to the statement. FX is Xero's (post in USD).

## Inputs

- **IBKR Activity Statement** for the period (base currency USD). Key sections: Net Asset Value (cash / stock / interest accruals, prior vs current); Mark-to-Market Performance Summary (period MTM by symbol); Realized & Unrealized Performance Summary; Interest Accruals; any Dividends / Withholding / Commissions.
- **Xero export** — to reconcile the broker balances (`Financial assets at FV through P/L` = stock; `Amount due from a broker` = cash + accruals).

## NAV bridge (validate first)

Confirm: `cash + stock (MV) + interest accruals = Total NAV`, and the period change reconciles as `MTM + interest received (cash) + Δ interest accrual = ΔNAV`. Use `scripts/ibkr_nav_check.py`.

*April 2026 worked example:* cash 501,715.13 + stock 1,406,837.83 + accruals 1,243.51 = NAV 1,909,796.47; change 184,189.11 = MTM 182,902.77 + interest received 700.09 + Δaccrual 586.25. Ties.

## Entries (USD draft, unique references)

Prepare one entry per item that is non-nil; state nil items as nil (do not post zero lines):

- **Securities mark-to-market** (`3CP-TRES-<period>-MTM`): period MTM movement (Mark-to-Market Performance Summary total).
  `DR Financial assets at FV through P/L  /  CR Unrealised P&L (IBKR)` (or the reverse for a loss). April: USD 182,902.77.
- **Broker interest income** (`-INT`): period interest accrued (Interest Accruals → Interest Accrued).
  `DR Amount due from a broker - Interactive Brokers (interest receivable)  /  CR Interest Income (Bank)`. April: USD 1,286.34.
- **Dividends** (`-DIV`) when present: `DR receivable/cash  /  CR Dividend income (IBKR)`; book the related **Withholding Tax (IBKR)** (`-WHT`) gross/withheld per the statement.
- **Commissions** (`-COMM`) when present: `DR Commission (IBKR)  /  CR Amount due from a broker`.
- **Realised securities P&L** (`-RPL`) when there are disposals: from the Realized Performance Summary.

All amounts in USD; Xero applies the rate on posting. Add an indicative HKD @ 7.80 column on the workpaper only (labelled "indicative — not posted").

## Reconciliation to Xero (original currency)

- Stock MV (USD) → `Financial assets at FV through P/L`.
- Cash + interest accruals (USD) → `Amount due from a broker - Interactive Brokers` (net of the FVTPL contra).
- Total → IBKR NAV. Tie in USD; the HKD differences are pure rate (Xero spot) and are expected — do not chase.

## Flags

- **FVTPL FX**: securities are non-monetary — the FX component of their value change is part of the fair-value P&L (IAS 21), via Xero's translation; do **not** revalue them separately as a monetary item. Flag for reviewer.
- Dividends with withholding — confirm gross vs net and the WHT rate.
- Any realised disposals — confirm cost basis and that realised ≠ double-counted against prior unrealised.
- Numeric GL codes TBD.

## MTM and dividend decomposition (locked Jul 2026 — corrections from June 2026 close)

**MTM = pure price movement ONLY.** Use the MTM Performance Summary's **Position column totals**
(stocks + forex; June: -95,260.04 + -0.01 = -95,260.05). NEVER use "Total (Combined Assets)"
including the "Other" column — "Other" holds dividend-accrual postings (code Po); mixing them into
MTM double-counts dividends. Cross-check: MTM entry must equal the NAV walk's "Mark-to-Market" line.

**Dividends: decompose by ex-date, not cash receipt.**
- Dividend with ex-date in a PRIOR month (sitting in opening Dividend Accruals): cash receipt only
  CLEARS the accrual — DR 640 / CR 871. NOT current-month income.
- Dividend with ex-date in the CURRENT month: current income — DR 640 (net) + DR 506 (WHT) / CR 271 (gross).
- Tie-out: 871 must land at the statement's ending Dividend Accruals; 640's movement must equal
  cash change + interest-accrual change (June: 1,619.93 + 45.66 = 1,665.59 ✓).

**Broker interest:** income = "Interest Accrued" for the period (June: 1,373.08); the cash received
is the prior month's accrual clearing within 640. DR 640 / CR 270 at the accrued figure.

## Account split — 640 vs 870/871 (corrected Jul 2026 from live ledger)

- **640** = broker CASH only. **870** = Interest accrual (separate account). **871** = Dividend accrual.
- Broker interest entry each month: DR 640 [cash interest received] + DR 870 [change in interest
  accruals, may be negative] / CR 270 [Interest Accrued for the period]. June 2026: DR 640 1,327.42
  + DR 870 45.66 / CR 270 1,373.08. The live 870 ledger posts exactly this "Change in Interest
  Accruals" line monthly.
- **WHT follows the ex-date, like the dividend:** WHT on a dividend accrued in a prior month was
  expensed in that month (IBKR accrues dividends NET of tax — opening accrual 203.20 = 290.29 gross
  − 87.09 WHT). Only WHT on current-month ex-dates is a current expense. The statement's cash-basis
  "Withholding Tax" total spans both — decompose it; never book it whole.
- **CCB time-deposit interest is NOT 640**: it arrives in the CCB USD bank account — book as
  Receive Money on that bank account coded to 270 (reconciles against the statement import).

## WHT recognition — standing policy (confirmed Jul 2026)

**Recognise WHT on ex-date, gross-at-ex-date, going forward — every month, not just when a
correction is being made.** Per-dividend entry at ex-date: `DR 640 (net cash) + DR 506 (WHT)
/ CR 271 (gross dividend income)`. This is the default treatment for every future close, not
a one-off fix — module should apply it without re-deriving it each month.

**No retroactive catch-up for prior-period WHT misses below materiality.** If a WHT amount was
missed or booked net-only in a prior closed month, do NOT reopen/adjust that month if (a) the
prior month's net booking already left net profit correct, and (b) the amount is immaterial
(precedent: MSFT WHT 87.09 left unadjusted in May 2026). Flag the amount to Arnold for a
go/no-go materiality call rather than auto-adjusting; only correct prospectively.
