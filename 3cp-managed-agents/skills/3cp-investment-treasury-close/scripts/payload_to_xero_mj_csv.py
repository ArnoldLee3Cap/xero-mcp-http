#!/usr/bin/env python3
"""payload_to_xero_mj_csv.py — convert a 3CP contract payload (draft journals JSON)
into a Xero ManualJournal import CSV.

Usage:
  python3 payload_to_xero_mj_csv.py --payload X.json --out out.csv \
      [--coa chart-of-accounts.csv] [--rate 7.834] [--tax "Tax Exempt"]

Rules
-----
- One CSV row per journal LINE. Xero groups rows into one journal by identical
  *Narration + *Date. Narration = "<reference> | <narration>" so the idempotency
  reference stays visible in Xero.
- *Amount is signed: debit positive, credit negative.
- The ManualJournal template has NO currency column -> imports post in the org
  base currency (HKD). HKD journals pass through unchanged. Non-HKD journals
  require --rate (HKD per 1 unit of journal currency, the month-end Xero rate);
  amounts are converted and the original-currency amount is noted in Description.
  Any sub-cent imbalance from conversion rounding is absorbed into the last line.
- Account codes are resolved from the chart of accounts (exact name match,
  then alias table, then 'Less '-prefix tolerance). A journal with ANY
  unresolvable line is EXCLUDED from the CSV and reported as an exception
  (fix: add the code to Xero / the alias table, or settle that journal outside
  the MJ import).
- DRAFT journals only; HOLD journals are skipped and reported.
"""
import argparse, csv, json, sys, datetime, os

ALIASES = {
    # payload name (lower)                                : chart name (exact)
    "amount due from a broker - interactive brokers"      : "Amount due from Interactive Brokers",
    "lease liability"                                     : "Lease Liabiltity",  # chart typo, code 899
    "accumulated depreciation right-of-use of asset"      : "Less Accumulated Depreciation Right-of-use of Asset",
    "accumulated depreciation on computer equipment"      : "Less Accumulated Depreciation on Computer Equipment",
    "accumulated depreciation on furniture & fixtures"    : "Less Accumulated Depreciation on Furniture & Fixtures",
    "accumulated depreciation on leasehold improvements"  : "Less Accumulated Depreciation on Leasehold Improvements",
    "accumulated depreciation on office equipment"        : "Less Accumulated Depreciation on Office Equipment",
    "accrued management fee receivable"                   : "Management fee receivables",
    "management fee income"                               : "Revenue - Management Fees",
}

HDR = ['*Narration','*Date','Description','*AccountCode','*TaxRate','*Amount',
       'TrackingName1','TrackingOption1','TrackingName2','TrackingOption2']

def load_coa(path):
    by_name = {}
    with open(path, newline='', encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            code = (r.get('*Code') or r.get('Code') or '').strip()
            name = (r.get('*Name') or r.get('Name') or '').strip()
            if name:
                by_name[name.lower()] = code  # may be '' (uncoded bank accounts)
    return by_name

def resolve(name, coa):
    """-> (code or None, resolved_chart_name or None)"""
    n = name.strip().lower()
    if n in coa and coa[n]:
        return coa[n], name
    if n in ALIASES:
        a = ALIASES[n].lower()
        if a in coa and coa[a]:
            return coa[a], ALIASES[n]
    less = 'less ' + n
    if less in coa and coa[less]:
        return coa[less], 'Less ' + name
    return None, None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--payload', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--coa', default=os.path.join(os.path.dirname(__file__), '..', 'references', 'chart-of-accounts.csv'))
    ap.add_argument('--rate', type=float, default=None, help='HKD per 1 unit of journal currency (month-end Xero rate) for non-HKD journals')
    ap.add_argument('--tax', default='Tax Exempt', help='TaxRate CSV display name (must exist in the Xero org; default Tax Exempt = API code NONE)')
    a = ap.parse_args()

    coa = load_coa(a.coa)
    pay = json.load(open(a.payload))
    rows, included, skipped, exceptions = [], [], [], []

    for j in pay['journals']:
        ref, ccy, status = j['reference'], j.get('currency','HKD'), j.get('status','DRAFT')
        if status != 'DRAFT':
            skipped.append((ref, f'status {status}: ' + j.get('hold_reason','')))
            continue
        if ccy != 'HKD' and not a.rate:
            exceptions.append((ref, f'{ccy} journal but no --rate supplied (MJ import is HKD-only)'))
            continue
        # resolve all lines first — all-or-nothing per journal
        lines, bad = [], []
        for l in j['lines']:
            nm = l.get('account','')
            code = (l.get('account_code') or '').strip() or None
            chart_nm = nm
            if not code:
                code, chart_nm = resolve(nm, coa)
            if not code:
                bad.append(nm)
                continue
            amt = (l.get('debit',0) or 0) - (l.get('credit',0) or 0)
            lines.append((nm, chart_nm, code, amt))
        if bad:
            exceptions.append((ref, 'unresolvable account(s): ' + '; '.join(sorted(set(bad)))))
            continue
        # convert
        rate = 1.0 if ccy == 'HKD' else a.rate
        conv = [round(amt*rate, 2) for _,_,_,amt in lines]
        resid = round(-sum(conv), 2)
        if abs(resid) >= 0.005:
            conv[-1] = round(conv[-1] + resid, 2)   # absorb rounding into last line
        d = datetime.date.fromisoformat(j['date'])
        narr = f"{ref} | {j.get('narration','')[:160]}"
        for (nm, chart_nm, code, amt), hkd in zip(lines, conv):
            desc = chart_nm
            if ccy != 'HKD':
                desc += f" [{ccy} {abs(amt):,.2f} @ {rate}]"
            rows.append({'*Narration':narr, '*Date':d.strftime('%d/%m/%Y'), 'Description':desc,
                         '*AccountCode':code, '*TaxRate':a.tax, '*Amount':f'{hkd:.2f}',
                         'TrackingName1':'','TrackingOption1':'','TrackingName2':'','TrackingOption2':''})
        included.append((ref, ccy, sum(c for c in conv if c > 0)))

    with open(a.out, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=HDR); w.writeheader()
        for r in rows: w.writerow(r)

    print(f"WROTE {a.out}: {len(included)} journal(s), {len(rows)} line(s)")
    for ref, ccy, dr in included: print(f"  + {ref} [{ccy}] DR total HKD {dr:,.2f}")
    for ref, why in skipped:      print(f"  ~ SKIPPED {ref}: {why}")
    for ref, why in exceptions:   print(f"  ! EXCEPTION {ref}: {why}")
    if exceptions: sys.exit(2)

if __name__ == '__main__':
    main()
