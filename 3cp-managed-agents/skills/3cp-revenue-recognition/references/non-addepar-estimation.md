# Module: Non-Addepar clients — estimation accrual + quarter-end true-up (Amy Sadick)

Some management-fee clients are **not** calculated in Addepar. Their fee is computed in a **standalone Excel** at the **end of the quarter** (e.g. Q1 → calculated early April). Because the actual isn't known during the quarter, accrue on an **estimation basis** monthly and **true-up in the quarter-end month**, mirroring the Addepar quarterly true-up.

Currently: **Amy Sadick** (the only such client). Treat as USD.

## Monthly estimate (all three months of the quarter)
- **Each month accrue 1/3 of the *previous quarter's actual* management fee.**
- Q1 2026 basis = **Q4 2025 actual = USD 50,616.40** → monthly accrual **16,872.13** (50,616.40 ÷ 3).
- Going forward the basis rolls: **Q2 2026 estimate = Q1 2026 actual 49,568.32 ÷ 3 = 16,522.77/month**; true-up in June to the Q2 standalone-Excel actual. (Same logic as the Addepar clients — prior quarter ÷ 3, quarter-end true-up.)
- Entry (per month): `DR Accrued Management Fee Receivable / CR Management Fee Income`. Reference `3CP-REV-<period>-MGMT-AMYS-USD`. Reversal: No. Separate journal from the Addepar accrual (own method/stream — keep auditable).

## Quarter-end true-up (last month of the quarter)
- Read the **actual** quarter fee from the standalone Amy Sadick Excel (`Draft_Amy_S_<YYYY>_<MM>.xlsx`).
  - **Actual = "Invoice1" Subtotal** = sum of the monthly "Management Fee (USD)" rows = the "Amy Sadick" row on "Monthly Data for Calculation". Q1 2026 = **49,568.32** (Jan 16,929.10 + Feb 16,664.52 + Mar 15,974.70).
  - Fee mechanics in the sheet (for context, not re-computed here): tiered on Chargeable Balance (Apargle + Ultimate Sources bank balances) — $20MM @ 0.85% p.a., next @ 0.75%, etc. **Ignore the Performance Fee sheets** (year-end only; 0 for 2026).
- **True-up = actual − cumulative estimate booked.** Q1 2026 = 49,568.32 − (3 × 16,872.13 = 50,616.39) = **−1,048.07** (over-accrued → reduce).
- Entry: if negative, `DR Management Fee Income / CR Accrued Management Fee Receivable`; if positive, the reverse. Reference `3CP-REV-<period>-TRUEUP-AMYS-USD`. Separate from the Addepar true-up.
- **Timing:** the actual is calculated in the month *after* quarter-end, so the quarter-end revenue workpaper is finalised then (same as the Addepar quarterly true-up).

## Worked example — Q1 2026 (USD)
Jan 16,872.13 + Feb 16,872.13 + Mar 16,872.13 (est.) = 50,616.39 accrued; true-up −1,048.07 → **49,568.32 actual** (= invoice SADICK20260331). Combined with the Addepar stream (658,553.69), total Q1 management fee = **708,122.01** = tracker total.
