# Journal Templates

Standard journal structures for each scenario in the monthly close. Use these as building blocks for the summary journal.

## Naming Conventions for GL Accounts

Throughout this document:

| Short name | Full account name | Type |
|---|---|---|
| AMEX Clearing | AMEX Payment Clearing Account | Balance Sheet (Asset/Liability transit) |
| AMEX Payable | Trade Creditors — AMEX | Balance Sheet (Liability) |
| Employee Reimbursement Payable | Employee Reimbursement Payable | Balance Sheet (Liability) |
| Accrued Expenses | Accrued Expenses | Balance Sheet (Liability) |
| Receivable from PEP | Receivable from PEP Fund — [Fund Name] | Balance Sheet (Asset) |
| Staff Receivable | Staff Receivable / Loan to Employee | Balance Sheet (Asset) |
| Prepayment | Prepayments | Balance Sheet (Asset) |
| AMEX Unsubmitted Suspense | AMEX Unsubmitted — Suspense | Balance Sheet (Asset) |
| Unallocated Suspense | Unallocated AMEX — Suspense | Balance Sheet (Asset) |
| Expense | Various expense accounts by category | P&L |
| Cash | Bank | Balance Sheet (Asset) |

## Template 1: AMEX Statement Payment

When the Company pays AMEX on the 19th of the month (cash outflow):

```
Dr.  AMEX Clearing                      [Statement total]
   Cr.  Cash                                            [Statement total]
```

This is always Balance Sheet to Balance Sheet — no P&L impact.

## Template 2: Month-End Allocation of AMEX Statement

After the AMEX statement payment, allocate each line item. The allocation entries collectively credit AMEX Clearing:

```
Dr.  Expense (P&L)                      [Reimbursable, submitted + approved]
Dr.  Expense (P&L)                      [Reimbursable, submitted, awaiting approval — accrual]
Dr.  Receivable from PEP Fund           [PEP-related, all]
Dr.  Staff Receivable                   [Non-reimbursable amounts]
Dr.  Prepayment                         [Multi-period items — initial booking]
Dr.  AMEX Unsubmitted Suspense          [AMEX charges with no submission]
Dr.  Unallocated Suspense               [Truly unidentified items]
   Cr.  AMEX Clearing                                   [Total statement allocated]
```

The total Dr. must equal AMEX Clearing balance, which must equal the original AMEX statement payment.

### The Combined Summary Entry (Templates 1 + 2)

When Templates 1 and 2 happen in the same close period (typical case — AMEX paid on the 19th, allocation done at month-end), they can be combined. The AMEX Clearing account nets to zero (Dr from payment, Cr from allocation), and the journal simplifies to:

```
Dr.  Expense (P&L)                      [Reimbursable]
Dr.  Receivable from PEP Fund           [PEP-related]
Dr.  Staff Receivable                   [Non-reimbursable]
Dr.  Prepayment                         [Multi-period items]
Dr.  AMEX Unsubmitted Suspense          [Unsubmitted]
Dr.  Unallocated Suspense               [Unidentified]
   Cr.  Cash                                            [Total AMEX statement paid]
```

This is the form the Excel template produces — AMEX Clearing is omitted because it nets to zero. The credit side directly shows the cash outflow.

**Important:** If the AMEX payment and the allocation happen in different periods (e.g., AMEX paid March 19 but allocation done at March 31 month-end), keep AMEX Clearing in the journal to maintain the audit trail. AMEX Clearing should net to zero by month-end.

## Template 3: Prepayment Amortisation

For multi-period prepayments, after initial Prepayment booking:

```
For each period the prepayment covers:
Dr.  Expense (P&L)                      [Period's share]
   Cr.  Prepayment                                       [Period's share]
```

If a prepayment was paid in March but covers Jan–Mar:
- Book all three months of amortisation in March (Jan and Feb portions are prior-period catch-up, acceptable if immaterial)
- Or for material items, post correcting entries to Jan and Feb if those periods are still open

## Template 4: Personal Card / Out-of-Pocket Reimbursable Expense

When an employee fronts an expense on personal card or cash (no AMEX involvement), the cash flow is different from AMEX items. The Company does not pay anyone until reimbursement is approved.

### Template 4a: Submitted and Approved in Same Month

Employee incurs expense in March, submits in March, approved in March. Xero auto-posts:

```
Dr.  Expense (P&L)                      [Approved amount]
   Cr.  Employee Reimbursement Payable                  [Approved amount]
```

When the Company pays the employee (typically via bank transfer, weekly or monthly batch):

```
Dr.  Employee Reimbursement Payable     [Paid amount]
   Cr.  Cash                                            [Paid amount]
```

**No P&L impact at the payment stage** — the P&L was hit at approval.

### Template 4b: Expense Incurred but Not Yet Submitted (Personal Card)

This is the blind spot of personal card spending — Sally has no AMEX statement to fall back on. Two approaches:

**Approach 1 — Trailing average accrual (for material amounts):**

If personal card spend is material (>HK$20–30k/month), accrue based on trailing 3-month average:

```
Dr.  Expense (P&L)                      [Estimated amount]
   Cr.  Accrued Expenses                                [Estimated amount]
```

Reversed and trued up when actual submissions clear.

**Approach 2 — Accept the timing difference (for immaterial amounts):**

At low volume / value, don't accrue. Accept that personal-card expenses land in the month of submission rather than the month of incurrence. Auditors are comfortable with this for immaterial amounts.

### Template 4c: Submitted, Not Yet Approved (Personal Card)

Employee has submitted to Expensify, so the assertion exists. Sally can see it on the submitted-but-unapproved report at month-end.

**At month-end (accrual):**
```
Dr.  Expense (P&L)                      [Submitted amount]
   Cr.  Accrued Expenses                                [Submitted amount]
```

**When approved next month (Xero auto-post):**
```
Dr.  Expense (P&L)                      [Approved amount]
   Cr.  Employee Reimbursement Payable                  [Approved amount]
```

**Sally's reversal of prior accrual:**
```
Dr.  Accrued Expenses                   [Prior accrual amount]
   Cr.  Expense (P&L)                                   [Prior accrual amount]
```

Net P&L impact in approval month: zero (auto-post +X, reversal -X). The expense correctly sits in the prior month.

### Template 4d: Personal Card Expense Tagged as PEP

Same as AMEX-based PEP treatment — must be routed to Receivable from PEP Fund, not Expense.

**Approved and Xero auto-posts (initially as Expense):**
```
Dr.  Expense (P&L)                      [Approved amount]
   Cr.  Employee Reimbursement Payable                  [Approved amount]
```

**Sally reclassifies:**
```
Dr.  Receivable from PEP Fund           [Approved amount]
   Cr.  Expense (P&L)                                   [Approved amount]
```

The Employee Reimbursement Payable is still there — the Company still owes the employee. When the PEP fund eventually pays the recharge, that clears the Receivable; the Company still pays the employee from its own cash separately.

### Template 4e: Personal Card Expense Rejected

If a personal-card expense is rejected as non-reimbursable, **no entry is needed.** Unlike AMEX (where cash has already left), the Company never paid anything. Expensify simply rejects the claim. The employee absorbs the cost on their personal card.

This is a key operational advantage of personal card over AMEX — no Staff Receivable to chase.

### Cash Flow Timing Comparison

| Expense path | Cash leaves Company | Bridging account used |
|---|---|---|
| AMEX | Statement payment on 19th of next month | AMEX Clearing |
| Personal card / out-of-pocket | When employee is reimbursed (after approval) | Employee Reimbursement Payable |

This timing difference is why the two paths need separate accounting treatment.

## Template 5: Xero Auto-Post Reversal (Critical Pattern)

When Expensify approval triggers Xero auto-post and the item was previously accrued, the auto-post double-counts. Release the prior accrual:

**Xero auto-post (happens automatically):**
```
Dr.  Expense (P&L)                      [Approved amount]
   Cr.  AMEX Payable                                     [Approved amount]
```

**Sally's reversal entry (same month as auto-post):**
```
Dr.  Accrued Expenses                   [Prior accrual amount]
   Cr.  Expense (P&L)                                    [Prior accrual amount]
```

If accrual amount = auto-post amount, net P&L impact for the current month is zero (the expense correctly stays in the prior month).

## Template 6: PEP Reclassification

When an item was accrued as Company expense but is later identified as PEP:

```
Dr.  Receivable from PEP Fund           [Reclassified amount]
   Cr.  Expense (P&L)                                    [Reclassified amount]
```

This removes the item from P&L (correcting the over-accrual) and creates the receivable.

If the item was both auto-posted AND accrued AND needs PEP reclassification, all three entries occur in sequence:
1. Xero auto-post: Dr. Expense / Cr. AMEX Payable (happens automatically)
2. Reverse accrual: Dr. Accrued Expenses / Cr. Expense
3. Reclassify to PEP: Dr. Receivable from PEP / Cr. Expense

## Template 7: Non-Reimbursable Reclassification

When an item was initially accrued as reimbursable but Sally rejects on review:

```
Dr.  Staff Receivable                   [Rejected amount]
   Cr.  Expense (P&L)                                    [Rejected amount]
```

If the item was paid on AMEX, this corrects the accrual. The employee must repay separately.

## Template 8: Suspense Resolution

When a previously parked suspense item is resolved:

**From AMEX Unsubmitted Suspense (employee finally submits):**
```
[Whatever the correct classification is]      [Amount]
   Cr.  AMEX Unsubmitted Suspense                       [Amount]
```

**From Unallocated Suspense (Sally identifies the item):**
```
[Whatever the correct classification is]      [Amount]
   Cr.  Unallocated Suspense                            [Amount]
```

## Template 9: PEP Fund Quarterly Recharge Receipt

When the PEP fund pays the accumulated recharge:

```
Dr.  Cash                                [Recharge amount]
   Cr.  Receivable from PEP Fund                         [Recharge amount]
```

No P&L impact at any stage of the PEP cycle.

## Template 10: Staff Receivable Settlement

When the employee repays the non-reimbursable amount:

```
Dr.  Cash                                [Repayment amount]
   Cr.  Staff Receivable                                 [Repayment amount]
```

## Building the Summary Journal

The month-end summary journal combines Templates 2 + 3 (initial) + 5/6/7 (reclassifications from prior months) + 8 (suspense resolutions) into one entry per month.

Structure of the final summary journal:

```
SUMMARY JOURNAL — [Month] [Year]

DEBITS:
  [Each account that increases in the period]

CREDITS:
  [Each account that decreases in the period]

CHECK:
  Total Debits = Total Credits ✓
  AMEX Clearing closing balance = 0 ✓
  P&L impact = Truly Company-incurred expense for period ✓
```

## Worked Mini-Example

Scenario: HK$100k AMEX statement, of which 50k is PEP, 30k is reimbursable, 10k is subscriptions (Q1), 8k is non-reimbursable, 2k is unidentified.

**Combined month-end summary entry (AMEX Clearing nets to zero):**

```
SUMMARY JOURNAL — March 31

DEBITS:
  Receivable from PEP Fund           50,000
  Expense (P&L) — Reimbursable        30,000
  Prepayment                          10,000
  Expense (P&L) — Subscriptions       10,000  [amortise all Q1 in Mar]
  Staff Receivable                     8,000
  Unallocated Suspense                 2,000
                                    --------
  Total Debits                      110,000

CREDITS:
  Cash                              100,000   [paid AMEX statement on 19th]
  Prepayment                         10,000   [release as amortised within Mar]
                                    --------
  Total Credits                     110,000

P&L Impact: +40,000 expense
```

Note the offsetting Prepayment entries — the 10k books in, then 10k books out as it's amortised within the same month. The net Prepayment balance is zero. AMEX Clearing also nets to zero (not shown) — Dr 100k from cash payment, Cr 100k from allocation.

## Key Verification Checks

After building any summary journal:

1. **Debits = Credits** (basic double-entry)
2. **AMEX Clearing nets to zero** at month-end
3. **No PEP item lands in Expense** — all PEP routes to Receivable
4. **No Non-reimbursable item lands in Expense** — all routes to Staff Receivable
5. **Suspense balances are documented** with aging
6. **P&L delta reconciles** to the sum of truly reimbursable + amortised prepayment portions
