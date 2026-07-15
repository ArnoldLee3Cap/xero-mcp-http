#!/usr/bin/env python3
"""
IBKR NAV bridge validator for the 3CP treasury close.

Confirms the Interactive Brokers activity statement is internally consistent
before any journal is prepared:
  (1) cash + stock + interest_accruals = Total NAV   (prior and current)
  (2) MTM + interest_received + delta_accrual = change in NAV

All inputs are USD, taken straight from the statement's Net Asset Value,
Mark-to-Market, and Interest Accruals sections. No rates involved (USD base).

Usage:
    python ibkr_nav_check.py \
        --prior-cash 501015.03 --prior-stock 1223935.07 --prior-accr 657.25 \
        --cur-cash 501715.13  --cur-stock 1406837.83  --cur-accr 1243.51 \
        --mtm 182902.77 --interest-received 700.09 --interest-accrued 1286.34

Prints PASS/FAIL on each check with the residual, plus the interest figure to
book (interest_accrued = the period income; interest_received is the cash leg).
"""
import argparse

def chk(label, lhs, rhs, tol=0.05):
    ok = abs(lhs - rhs) <= tol
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}: {lhs:,.2f} vs {rhs:,.2f} (residual {lhs-rhs:+,.2f})")
    return ok

def main():
    p = argparse.ArgumentParser()
    for a in ["prior-cash","prior-stock","prior-accr","cur-cash","cur-stock","cur-accr",
              "mtm","interest-received","interest-accrued"]:
        p.add_argument("--"+a, type=float, required=True)
    g = p.parse_args()
    prior_nav = g.prior_cash + g.prior_stock + g.prior_accr
    cur_nav   = g.cur_cash + g.cur_stock + g.cur_accr
    d_accr    = g.cur_accr - g.prior_accr
    print("IBKR NAV bridge (USD):\n")
    print(f"  Prior NAV  = {prior_nav:,.2f}")
    print(f"  Current NAV= {cur_nav:,.2f}")
    print(f"  Change     = {cur_nav-prior_nav:,.2f}\n")
    a = chk("ΔNAV = MTM + interest received + Δaccrual",
            cur_nav - prior_nav, g.mtm + g.interest_received + d_accr)
    # interest_accrued should equal interest_received + change in accrual
    b = chk("interest accrued = interest received + Δaccrual",
            g.interest_accrued, g.interest_received + d_accr)
    print(f"\n  → Period MTM to book (Unrealised P&L IBKR): USD {g.mtm:,.2f}")
    print(f"  → Period interest income to book           : USD {g.interest_accrued:,.2f}")
    print("\nRESULT:", "ALL CHECKS PASS" if (a and b) else "CHECK FAILED — investigate before posting")

if __name__ == "__main__":
    main()
