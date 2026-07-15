#!/usr/bin/env python3
"""
Dry-run validator & preview for the 3CP Xero journal poster.

Makes NO Xero calls. Safe to run anytime. It:
  - validates each journal balances within its currency,
  - separates eligible (status DRAFT) from held (HOLD / other),
  - applies an idempotency simulation if --existing-refs is given,
  - prints exactly what WOULD be sent to Xero as DRAFT,
  - optionally previews a promote batch (--promote ref1,ref2).

Usage:
  python dryrun.py --payload 3CP_MJ_April2026_draft_journals.json
  python dryrun.py --payload p.json --existing-refs 3CP-MJ-2026-04-FA-DEP
  python dryrun.py --payload p.json --promote 3CP-MJ-2026-04-LEASE-INT,3CP-MJ-2026-04-FA-DEP
"""
import argparse, json, sys

def money(x): return f"{x:,.2f}"

def validate_journal(j):
    by_ccy_d = {}; by_ccy_c = {}
    ccy = j.get("currency", "?")
    for l in j["lines"]:
        by_ccy_d[ccy] = by_ccy_d.get(ccy, 0) + l.get("debit", 0)
        by_ccy_c[ccy] = by_ccy_c.get(ccy, 0) + l.get("credit", 0)
    d = round(by_ccy_d.get(ccy, 0), 2); c = round(by_ccy_c.get(ccy, 0), 2)
    return d, c, (d == c)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--payload", required=True)
    ap.add_argument("--existing-refs", default="", help="comma-sep refs already in Xero (idempotency sim)")
    ap.add_argument("--promote", default="", help="comma-sep refs to preview promoting Draft->Posted")
    g = ap.parse_args()

    payload = json.load(open(g.payload))
    existing = {r.strip() for r in g.existing_refs.split(",") if r.strip()}
    promote = [r.strip() for r in g.promote.split(",") if r.strip()]

    print(f"Entity : {payload.get('entity')}")
    print(f"Source : {payload.get('source_skill')}   Period: {payload.get('period')}")
    tgt = payload.get("target", {})
    print(f"Target : {tgt.get('system')}  post_as={tgt.get('post_as')}  auto_approve={tgt.get('auto_approve')}")
    print("=" * 78)

    eligible, held, skipped = [], [], []
    for j in payload["journals"]:
        ref = j["reference"]; status = j.get("status", "DRAFT")
        d, c, bal = validate_journal(j)
        if status != "DRAFT":
            held.append((j, d, c, bal)); continue
        if not bal:
            held.append((j, d, c, bal)); continue
        if ref in existing:
            skipped.append((j, d, c)); continue
        eligible.append((j, d, c))

    print("\n--- WOULD CREATE AS XERO DRAFT (eligible) ---")
    if not eligible: print("  (none)")
    for j, d, c in eligible:
        print(f"\n  {j['reference']}   [{j['currency']}]   {j.get('date')}")
        print(f"  \"{j.get('narration','')}\"")
        for l in j["lines"]:
            dr = money(l['debit']) if l['debit'] else ""
            cr = money(l['credit']) if l['credit'] else ""
            print(f"      {l['account']:<48} Dr {dr:>14}  Cr {cr:>14}")
        print(f"      {'— balance —':<48}    {money(d):>17}     {money(c):>14}  {'OK' if d==c else 'OUT'}")

    if skipped:
        print("\n--- SKIPPED (reference already in Xero — idempotent) ---")
        for j, d, c in skipped:
            print(f"  {j['reference']}  [{j['currency']}]  Dr {money(d)} Cr {money(c)}  → exists, not re-created")

    print("\n--- HELD (not eligible to post) ---")
    if not held: print("  (none)")
    for j, d, c, bal in held:
        why = j.get("hold_reason") or ("OUT OF BALANCE" if not bal else f"status={j.get('status')}")
        print(f"  {j['reference']}  [{j['currency']}]  Dr {money(d)} Cr {money(c)}")
        print(f"      reason: {why}")

    if promote:
        print("\n--- PROMOTE PREVIEW (Draft -> Posted) ---")
        refs_in_payload = {j["reference"]: j for j in payload["journals"]}
        for ref in promote:
            j = refs_in_payload.get(ref)
            if not j:
                print(f"  {ref}: not in payload → STOP (unknown reference)"); continue
            d, c, bal = validate_journal(j)
            if j.get("status") != "DRAFT" or not bal:
                print(f"  {ref}: not eligible ({j.get('hold_reason') or 'not a balanced DRAFT'}) → STOP")
            else:
                print(f"  {ref}: re-verify balance Dr {money(d)}=Cr {money(c)} → would set Status=POSTED")
        print("  (live promote also re-reads each draft from Xero before flipping; named-only, never 'post all')")

    print("\n" + "=" * 78)
    print(f"SUMMARY: {len(eligible)} would create as DRAFT | {len(skipped)} skipped (exist) | {len(held)} held")
    print("No Xero calls were made. Posting requires a write-scoped connection (accounting.transactions).")
    return 0 if all(b for *_, b in [(*h[:-1], h[-1]) for h in held] ) or True else 1

if __name__ == "__main__":
    sys.exit(main())
