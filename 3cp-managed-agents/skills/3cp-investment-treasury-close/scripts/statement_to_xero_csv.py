#!/usr/bin/env python3
"""statement_to_xero_csv.py — convert parsed bank/broker statement transactions
into a Xero **bank statement import** CSV (StatementImportTemplate).

Use ONLY for accounts WITHOUT an automatic feed — currently **CCB and IBKR**.
DBS feeds automatically into Xero, so DBS statements are NOT imported this way
(we still create the manual journals for DBS-paid transactions; Xero reconciles
the feed against those journals).

Usage:
  python3 statement_to_xero_csv.py --txns parsed_txns.json --out <Acct>_StatementImport_Xero.csv

Input JSON: a list of transactions, each:
  {"date":"YYYY-MM-DD", "amount": <signed float>, "payee":"...", "description":"...",
   "reference":"...", "check_number":"" }
  amount sign: money INTO the account = positive; money OUT = negative.

Why the detail matters: Xero matches imported statement lines to existing
ledger transactions (journals/invoices/bills) and *learns* from Payee + Reference.
The richer and more consistent Payee/Description/Reference are, the more lines
Xero auto-suggests a match for at reconciliation — so the parser should populate
all three as specifically as the statement allows:
  - Payee     = the counterparty (e.g. "CCB (Asia) Time Deposit", "IBKR - dividend USD")
  - Description = a clear, human narrative of the line
  - Reference = a stable identifier that also appears on the matching journal
               (account no., TD confirmation no., IBKR activity id, invoice no.)
Consistent Reference between the statement line and the journal is the single
biggest driver of clean auto-reconciliation.
"""
import argparse, csv, json, datetime, sys

HDR = ['*Date','*Amount','Payee','Description','Reference','Check Number']

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--txns', required=True, help='JSON list of parsed transactions')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    txns = json.load(open(a.txns))
    rows, total = [], 0.0
    for t in txns:
        d = datetime.date.fromisoformat(t['date'])
        amt = round(float(t['amount']), 2); total += amt
        rows.append({'*Date': d.strftime('%d/%m/%Y'),
                     '*Amount': f'{amt:.2f}',
                     'Payee': t.get('payee',''),
                     'Description': t.get('description',''),
                     'Reference': t.get('reference',''),
                     'Check Number': t.get('check_number','')})
    with open(a.out, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=HDR); w.writeheader()
        for r in rows: w.writerow(r)
    print(f"WROTE {a.out}: {len(rows)} statement line(s), net movement {total:,.2f}")
    miss = [i for i,t in enumerate(txns) if not (t.get('payee') and t.get('reference'))]
    if miss:
        print(f"  ! {len(miss)} line(s) missing Payee or Reference — fill for clean reconciliation (lines {miss})")

if __name__ == '__main__':
    main()
