#!/usr/bin/env python3
"""match_statement.py — propose reconciliation matches between bank STATEMENT
lines and posted ACCOUNT TRANSACTIONS (Spend/Receive Money) for 3CP.

This is a READ-ONLY analysis tool. It makes NO Xero calls and changes nothing.
It takes the two sides of a Xero bank reconciliation and proposes which
statement line pairs with which account transaction, so the user can confirm
each pair in Xero's Reconcile tab. The actual "match -> OK" click stays a human
step in Xero (the xero-3cp MCP surface has no reconcile/match write tool).

Matching principle (deliberate):
  - Match on AMOUNT (signed, same currency) + REFERENCE — NOT on date.
    Value-date-vs-post-date timing differences and weekend roll-forwards mean a
    line dated 30-Jun can post a day or two later; date is used only as a
    tiebreaker and to surface timing gaps, never as a match key.
  - A consistent Reference on both sides is the strongest signal. For CCB/IBKR
    the treasury skill populates Reference on the import CSV to mirror the
    posted transaction; for DBS the feed reference is whatever the bank sends.

Inputs (both JSON):
  --statement   list of statement lines, each:
      {"date":"YYYY-MM-DD", "amount": <signed float, IN=+ / OUT=->,
       "payee":"...", "description":"...", "reference":"...",
       "currency":"HKD"|"USD"}
  --transactions  list of posted account transactions (from
      xero-3cp:list-bank-transactions), each EITHER with a signed "amount"
      (RECEIVE=+ / SPEND=-) OR with "type" ("SPEND"|"RECEIVE") + "total":
      {"id":"...", "reference":"...", "date":"YYYY-MM-DD",
       "total": <positive float>, "type":"SPEND"|"RECEIVE",
       "contact":"...", "currency":"HKD"|"USD", "reconciled": false}

Output: a match proposal (JSON to --out, plus a readable summary to stdout):
  high / medium confidence pairs, ambiguous sets (user must pick),
  unmatched statement lines, and unmatched transactions.

Usage:
  python3 match_statement.py --statement stmt.json --transactions txns.json \
      --out match_proposal.json [--cent-eps 0.01] [--fee-max 60] [--fee-pct 0.005]
"""

import argparse
import json
import re
import sys
from itertools import combinations


def norm_ref(r):
    """Normalise a reference to comparable tokens: uppercase alphanumerics."""
    if not r:
        return set()
    toks = re.findall(r"[A-Za-z0-9]+", str(r).upper())
    # keep tokens of length >= 3 (drop noise like single letters / short codes
    # that collide too easily), but always keep any all-digit token >= 4 chars
    return {t for t in toks if len(t) >= 3}


def signed_txn_amount(t):
    """Return the signed amount for a transaction (RECEIVE=+, SPEND=-).
    
    Xero convention: SPEND total is positive (outflow), RECEIVE total is positive
    (inflow). Sign is determined by type. HOWEVER, IBKR valuation journals can be
    posted as Receive Money with a negative total (net NAV decreased) — in that
    case the negative total is correct and must not be flipped. So we apply the
    sign convention (SPEND → negate, RECEIVE → keep) to the raw total, NOT abs().
    """
    if "amount" in t and t["amount"] is not None:
        return float(t["amount"])
    typ = str(t.get("type", "")).upper()
    total = float(t.get("total", 0.0))
    if typ == "SPEND":
        return -abs(total)  # SPEND total is always positive in Xero; negate it
    if typ == "RECEIVE":
        return total  # keep as-is; positive for inflows, negative for net-negative valuations
    raise ValueError(
        f"Transaction {t.get('id','?')} has neither a signed 'amount' nor a "
        f"valid 'type' (SPEND/RECEIVE) + 'total'."
    )


def amounts_equal(a, b, eps):
    return abs(a - b) <= eps


def ref_overlap(a_ref, b_ref):
    ta, tb = norm_ref(a_ref), norm_ref(b_ref)
    if not ta or not tb:
        return 0.0
    inter = ta & tb
    if not inter:
        return 0.0
    return len(inter) / max(1, min(len(ta), len(tb)))


def main():
    ap = argparse.ArgumentParser(description="Propose bank reconciliation matches (read-only).")
    ap.add_argument("--statement", required=True, help="statement lines JSON")
    ap.add_argument("--transactions", required=True, help="posted transactions JSON")
    ap.add_argument("--out", default="match_proposal.json", help="output JSON path")
    ap.add_argument("--cent-eps", type=float, default=0.01,
                    help="exact-amount tolerance for rounding (default 0.01)")
    ap.add_argument("--fee-max", type=float, default=60.0,
                    help="max absolute amount diff to flag as a possible bank fee (default 60)")
    ap.add_argument("--fee-pct", type=float, default=0.005,
                    help="max proportional amount diff to flag as a possible fee (default 0.5%%)")
    args = ap.parse_args()

    with open(args.statement) as f:
        stmt = json.load(f)
    with open(args.transactions) as f:
        txns = json.load(f)

    # index transactions, drop already-reconciled ones (nothing to match)
    open_txns = []
    for i, t in enumerate(txns):
        if t.get("reconciled") is True:
            continue
        t = dict(t)
        t["_i"] = i
        t["_amt"] = signed_txn_amount(t)
        t["_cur"] = str(t.get("currency", "")).upper()
        open_txns.append(t)

    stmt_lines = []
    for j, s in enumerate(stmt):
        s = dict(s)
        s["_j"] = j
        s["_amt"] = float(s["amount"])
        s["_cur"] = str(s.get("currency", "")).upper()
        stmt_lines.append(s)

    matched = []        # high/medium 1:1
    ambiguous = []      # one side, several equal-amount candidates
    grouped = []        # 1-to-many (a line == sum of several txns, or vice versa)
    fee_flags = []      # amounts differ by a plausible fee
    used_txn = set()
    used_stmt = set()

    def cur_ok(a, b):
        # if either side omits currency, don't block on it; if both present, must match
        return (not a) or (not b) or (a == b)

    # ---- Pass 1: exact 1:1 amount matches, ranked by reference overlap ----
    for s in stmt_lines:
        if s["_j"] in used_stmt:
            continue
        cands = [t for t in open_txns
                 if t["_i"] not in used_txn
                 and cur_ok(s["_cur"], t["_cur"])
                 and amounts_equal(s["_amt"], t["_amt"], args.cent_eps)]
        if not cands:
            continue
        # score by reference overlap; prefer the strongest, break ties by nearest date
        scored = sorted(
            cands,
            key=lambda t: (ref_overlap(s.get("reference"), t.get("reference")),),
            reverse=True,
        )
        top = scored[0]
        top_ref = ref_overlap(s.get("reference"), top.get("reference"))
        strong = [t for t in scored if ref_overlap(s.get("reference"), t.get("reference")) == top_ref]

        if len(cands) == 1:
            conf = "high" if top_ref > 0 else "medium"
            matched.append(_pair(s, top, conf,
                                 "unique amount match" + (" + reference overlap" if top_ref > 0 else
                                                          " (no reference to confirm — verify payee/date)")))
            used_stmt.add(s["_j"]); used_txn.add(top["_i"])
        elif top_ref > 0 and len(strong) == 1:
            matched.append(_pair(s, top, "high", "amount match + unique reference overlap among several equal-amount candidates"))
            used_stmt.add(s["_j"]); used_txn.add(top["_i"])
        else:
            ambiguous.append({
                "statement_line": _s(s),
                "candidates": [_t(t) for t in cands],
                "reason": "several transactions share this amount and reference doesn't disambiguate — pick the correct one in Xero",
            })
            used_stmt.add(s["_j"])
            # do not consume any txn — user resolves

    # ---- Pass 2: 1-to-many (statement line == sum of up to 4 open txns) ----
    remaining_txns = [t for t in open_txns if t["_i"] not in used_txn]
    for s in stmt_lines:
        if s["_j"] in used_stmt:
            continue
        pool = [t for t in remaining_txns if t["_i"] not in used_txn and cur_ok(s["_cur"], t["_cur"])]
        found = None
        for k in (2, 3, 4):
            for combo in combinations(pool, k):
                if amounts_equal(sum(c["_amt"] for c in combo), s["_amt"], args.cent_eps):
                    found = combo
                    break
            if found:
                break
        if found:
            grouped.append({
                "statement_line": _s(s),
                "transactions": [_t(t) for t in found],
                "reason": f"one statement line equals the sum of {len(found)} posted transactions (batched movement)",
            })
            used_stmt.add(s["_j"])
            for c in found:
                used_txn.add(c["_i"])

    # ---- Pass 3: many-to-1 (several statement lines sum to one txn) ----
    remaining_stmt = [s for s in stmt_lines if s["_j"] not in used_stmt]
    for t in open_txns:
        if t["_i"] in used_txn:
            continue
        pool = [s for s in remaining_stmt if s["_j"] not in used_stmt and cur_ok(s["_cur"], t["_cur"])]
        found = None
        for k in (2, 3, 4):
            for combo in combinations(pool, k):
                if amounts_equal(sum(c["_amt"] for c in combo), t["_amt"], args.cent_eps):
                    found = combo
                    break
            if found:
                break
        if found:
            grouped.append({
                "transaction": _t(t),
                "statement_lines": [_s(s) for s in found],
                "reason": f"one posted transaction equals the sum of {len(found)} statement lines (e.g. principal + fee booked as one entry)",
            })
            used_txn.add(t["_i"])
            for c in found:
                used_stmt.add(c["_j"])

    # ---- Pass 4: possible-fee near matches (unused sides only) ----
    for s in stmt_lines:
        if s["_j"] in used_stmt:
            continue
        for t in open_txns:
            if t["_i"] in used_txn:
                continue
            if not cur_ok(s["_cur"], t["_cur"]):
                continue
            diff = abs(s["_amt"] - t["_amt"])
            if 0 < diff <= max(args.fee_max, abs(s["_amt"]) * args.fee_pct):
                fee_flags.append({
                    "statement_line": _s(s),
                    "transaction": _t(t),
                    "amount_difference": round(s["_amt"] - t["_amt"], 2),
                    "reason": "amounts differ by a small amount consistent with a wire/bank fee — confirm whether the fee is inside one side",
                })

    unmatched_stmt = [_s(s) for s in stmt_lines if s["_j"] not in used_stmt]
    unmatched_txn = [_t(t) for t in open_txns if t["_i"] not in used_txn]

    result = {
        "summary": {
            "statement_lines": len(stmt_lines),
            "open_transactions": len(open_txns),
            "matched_1to1": len(matched),
            "grouped": len(grouped),
            "ambiguous": len(ambiguous),
            "possible_fee_flags": len(fee_flags),
            "unmatched_statement_lines": len(unmatched_stmt),
            "unmatched_transactions": len(unmatched_txn),
        },
        "matched": matched,
        "grouped": grouped,
        "ambiguous": ambiguous,
        "possible_fee_flags": fee_flags,
        "unmatched_statement_lines": unmatched_stmt,
        "unmatched_transactions": unmatched_txn,
    }

    with open(args.out, "w") as f:
        json.dump(result, f, indent=2)

    _print_summary(result, args.out)


def _s(s):
    return {"date": s.get("date"), "amount": round(s["_amt"], 2),
            "payee": s.get("payee"), "description": s.get("description"),
            "reference": s.get("reference"), "currency": s.get("currency")}


def _t(t):
    return {"id": t.get("id"), "date": t.get("date"), "amount": round(t["_amt"], 2),
            "reference": t.get("reference"), "contact": t.get("contact"),
            "currency": t.get("currency")}


def _pair(s, t, confidence, reason):
    return {"confidence": confidence, "reason": reason,
            "statement_line": _s(s), "transaction": _t(t),
            "date_gap_days": _date_gap(s.get("date"), t.get("date"))}


def _date_gap(d1, d2):
    try:
        from datetime import date
        y1, m1, dd1 = map(int, str(d1)[:10].split("-"))
        y2, m2, dd2 = map(int, str(d2)[:10].split("-"))
        return abs((date(y1, m1, dd1) - date(y2, m2, dd2)).days)
    except Exception:
        return None


def _print_summary(r, out_path):
    s = r["summary"]
    print("\n=== Reconciliation match proposal (READ-ONLY — confirm each in Xero) ===")
    print(f"Statement lines: {s['statement_lines']}   Open transactions: {s['open_transactions']}")
    print(f"  1:1 matched:        {s['matched_1to1']}")
    print(f"  grouped (1<->many): {s['grouped']}")
    print(f"  ambiguous:          {s['ambiguous']}   (user must pick)")
    print(f"  possible-fee flags: {s['possible_fee_flags']}")
    print(f"  UNMATCHED lines:    {s['unmatched_statement_lines']}")
    print(f"  UNMATCHED txns:     {s['unmatched_transactions']}")
    if r["matched"]:
        print("\n-- Proposed 1:1 matches --")
        for m in r["matched"]:
            sl, tx = m["statement_line"], m["transaction"]
            gap = m.get("date_gap_days")
            gaptxt = f"  [date gap {gap}d]" if gap else ""
            print(f"  [{m['confidence'].upper():6}] {sl['amount']:>12} {sl.get('currency') or '':3} "
                  f"stmt<{sl.get('reference') or sl.get('payee') or '?'}> "
                  f"<-> txn<{tx.get('reference') or tx.get('contact') or '?'}> ({tx.get('id')}){gaptxt}")
            print(f"           reason: {m['reason']}")
    if r["ambiguous"]:
        print("\n-- Ambiguous (pick in Xero) --")
        for a in r["ambiguous"]:
            sl = a["statement_line"]
            print(f"  {sl['amount']:>12} {sl.get('currency') or '':3} — {len(a['candidates'])} equal-amount candidates")
    if r["possible_fee_flags"]:
        print("\n-- Possible bank-fee near-matches --")
        for fl in r["possible_fee_flags"]:
            print(f"  stmt {fl['statement_line']['amount']} vs txn {fl['transaction']['amount']} "
                  f"(diff {fl['amount_difference']})")
    if r["unmatched_statement_lines"]:
        print("\n-- UNMATCHED statement lines (no posted transaction found) --")
        for sl in r["unmatched_statement_lines"]:
            print(f"  {sl['amount']:>12} {sl.get('currency') or '':3} {sl.get('payee') or ''} "
                  f"<{sl.get('reference') or ''}>")
    if r["unmatched_transactions"]:
        print("\n-- UNMATCHED transactions (no statement line found — may be timing, or a wrong post) --")
        for tx in r["unmatched_transactions"]:
            print(f"  {tx['amount']:>12} {tx.get('currency') or '':3} {tx.get('contact') or ''} "
                  f"<{tx.get('reference') or ''}> ({tx.get('id')})")
    print(f"\nFull proposal written to: {out_path}\n")


if __name__ == "__main__":
    main()
