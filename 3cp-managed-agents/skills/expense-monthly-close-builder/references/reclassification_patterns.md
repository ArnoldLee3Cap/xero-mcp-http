# Reclassification Patterns

This file documents the correction entries needed when an item's classification changes between months, or when timing mismatches require offsetting entries.

## The Core Principle

The Expensify-Xero integration auto-posts approved expenses to **Expense (P&L)** in the month of approval. When the underlying expense was incurred in a prior month, this creates two problems:

1. **Wrong period:** Expense lands in approval month, not incurrence month
2. **Double-count:** If the prior month accrued the same item, it's now in two places

The fix is always a two-part correction: **release the prior accrual** (offsetting the double-count) and, where needed, **reclassify** to the correct account.

## Pattern A: Simple Auto-Post Reversal (Same Classification)

**Scenario:** March expense, accrued at March 31 as reimbursable. Approved in April. Xero auto-posts in April. No reclassification needed — it really is reimbursable.

**March 31 (accrual):**
```
Dr.  Expense                     [Amount]
   Cr.  Accrued Expenses                          [Amount]
```

**April (Xero auto-post — automatic):**
```
Dr.  Expense                     [Amount]
   Cr.  AMEX Payable                              [Amount]
```

**April (manual reversal):**
```
Dr.  Accrued Expenses            [Amount]
   Cr.  Expense                                   [Amount]
```

**Net April P&L impact: zero.** March correctly carries the expense.

## Pattern B: Auto-Post + Reclassification to PEP

**Scenario:** March expense, accrued as reimbursable. Approved in April. Sally identifies as PEP during review.

**March 31 (accrual):**
```
Dr.  Expense                     [Amount]
   Cr.  Accrued Expenses                          [Amount]
```

**April (Xero auto-post — automatic):**
```
Dr.  Expense                     [Amount]
   Cr.  AMEX Payable                              [Amount]
```

**April (manual corrections — two entries):**
```
Entry 1: Reverse accrual
Dr.  Accrued Expenses            [Amount]
   Cr.  Expense                                   [Amount]

Entry 2: Reclassify to PEP
Dr.  Receivable from PEP Fund    [Amount]
   Cr.  Expense                                   [Amount]
```

**Net April P&L impact: -[Amount].** This correction removes the prior over-accrual from March (which assumed the item was reimbursable).

**Net cumulative P&L impact:** Zero. The item was never a Company expense.

**Watch for:** Three separate Expense P&L hits in April (auto-post +, reversal -, reclassification -). They sum to -[Amount], not zero.

## Pattern C: Auto-Post + Reclassification to Non-Reimbursable

**Scenario:** March expense, accrued as reimbursable. Approved (or rather, processed) in April. Sally rejects as non-reimbursable.

**March 31 (accrual):**
```
Dr.  Expense                     [Amount]
   Cr.  Accrued Expenses                          [Amount]
```

**April (Xero auto-post would NOT happen for rejected items — but accrual still needs reversing):**
```
Entry 1: Reverse accrual
Dr.  Accrued Expenses            [Amount]
   Cr.  Expense                                   [Amount]

Entry 2: Recognise employee receivable
Dr.  Staff Receivable            [Amount]
   Cr.  AMEX Clearing or AMEX Payable             [Amount]
```

**Note:** If the item was on AMEX, the cash already left the bank (paid in March). The Staff Receivable now represents what the employee owes back. The credit side depends on whether the AMEX Clearing was already cleared or not — usually it was cleared by the March accrual, so the credit is to AMEX Clearing.

If the AMEX Clearing was credited in March via the accrual, the employee receivable in April effectively replaces what was treated as expense.

## Pattern D: AMEX Unsubmitted Suspense Resolution

When an AMEX charge was parked in suspense at a prior month-end and is finally submitted, the resolution depends on the classification determined by Sally/Alex during review. There are three possible terminal states.

**Setup for all three sub-patterns:**

March 31 (initial parking — same for all three):
```
Dr.  AMEX Unsubmitted Suspense   10,000
   Cr.  AMEX Clearing                            10,000
```

### Pattern D1: Resolves as Reimbursable Company Expense

Employee submits in May. Sally classifies as a valid Company business expense. Alex approves.

**May (Xero auto-post — automatic):**
```
Dr.  Expense                      10,000
   Cr.  AMEX Payable                            10,000
```

**May (manual correction — neutralise the spurious AMEX Payable and release suspense):**
```
Dr.  AMEX Payable                 10,000
   Cr.  AMEX Unsubmitted Suspense              10,000
```

**Net May P&L impact: +10,000.** This is the trade-off of conservative suspense treatment — expense lands in May (period of submission) rather than March (period of incurrence). Acceptable for immaterial amounts.

**Combined net entry view:**

| Account | Movement |
|---|---|
| Expense (P&L) | +10,000 |
| AMEX Unsubmitted Suspense | -10,000 |
| AMEX Payable | 0 (raised then cleared) |

### Pattern D2: Resolves as PEP-Related

Employee submits in May, tags it as PEP Fund III. Sally confirms during review and approves.

**May (Xero auto-post — automatic, naively books to Expense):**
```
Dr.  Expense                      10,000
   Cr.  AMEX Payable                            10,000
```

**May (manual corrections — two entries):**

Entry 1: Release suspense, neutralise AMEX Payable:
```
Dr.  AMEX Payable                 10,000
   Cr.  AMEX Unsubmitted Suspense              10,000
```

Entry 2: Reclassify Expense to PEP Receivable:
```
Dr.  Receivable from PEP Fund III 10,000
   Cr.  Expense                                10,000
```

**Net May P&L impact: zero.** ✓ (Auto-post +10,000 nets with reclassification -10,000.)

**Combined net entry view:**

| Account | Movement |
|---|---|
| Expense (P&L) | 0 (raised then reclassified) |
| AMEX Unsubmitted Suspense | -10,000 |
| AMEX Payable | 0 (raised then cleared) |
| Receivable from PEP Fund III | +10,000 |

PEP recharge cycle continues — when PEP Fund III pays quarterly, the receivable clears against Cash.

### Pattern D3: Resolves as Non-Reimbursable

Employee submits in May. Sally rejects as personal/non-reimbursable.

**Important:** Xero does NOT auto-post for rejected items. Only manual entries needed.

**May (manual entry — single entry):**
```
Dr.  Staff Receivable             10,000
   Cr.  AMEX Unsubmitted Suspense              10,000
```

**Net May P&L impact: zero.** ✓ (No P&L touch anywhere in the lifecycle.)

**Combined net entry view:**

| Account | Movement |
|---|---|
| AMEX Unsubmitted Suspense | -10,000 |
| Staff Receivable | +10,000 |
| P&L | 0 |

Employee subsequently repays the firm:
```
Dr.  Cash                         10,000
   Cr.  Staff Receivable                       10,000
```

### Pattern D4: Mixed Resolution (Partial Classifications)

Employee submits the HK$10k. Sally identifies HK$6k as PEP, HK$3k as legitimate Company expense, HK$1k as personal.

**May (Xero auto-post for approved portion — 6k + 3k = 9k):**
```
Dr.  Expense                       9,000
   Cr.  AMEX Payable                             9,000
```

**May (manual corrections):**

Entry 1: Release full suspense balance to appropriate destinations
```
Dr.  Receivable from PEP Fund      6,000
Dr.  AMEX Payable                  9,000   [Clear the spurious AMEX Payable from auto-post]
Dr.  Staff Receivable              1,000
   Cr.  AMEX Unsubmitted Suspense              10,000
   Cr.  Expense                                  6,000   [Reclassify PEP portion out of P&L]
```

**Net May P&L impact:**
- Auto-post Dr. Expense: +9,000
- Reclassify PEP Cr. Expense: -6,000
- Net: **+3,000** (the Company-reimbursable portion only) ✓

### Summary: Choosing the Right D Sub-Pattern

| Resolution outcome | Entries needed | P&L impact in resolution month |
|---|---|---|
| D1 — Reimbursable | Release suspense + neutralise auto-post | +Amount |
| D2 — PEP-related | D1 + reclassify to PEP receivable | 0 |
| D3 — Non-reimbursable | Release suspense → Staff Receivable (no auto-post) | 0 |
| D4 — Mixed | Combined entry covering all three terminal states | +Reimbursable portion only |

The terminal destination from AMEX Unsubmitted Suspense is always one (or a mix) of: Expense (Reimbursable) / Receivable from PEP / Staff Receivable.

## Pattern E: Unallocated Suspense Resolution

Different action path from AMEX Unsubmitted. Unallocated items require investigation before classification is possible.

### Pattern E1: Item Identified — Move to Appropriate Account

After investigation, Sally identifies a HK$500 unallocated charge as belonging to Carol Chan (who recently changed her cardholder profile).

**Move from Unallocated Suspense to AMEX Unsubmitted Suspense (employee now identified, still awaiting submission):**
```
Dr.  AMEX Unsubmitted Suspense      500
   Cr.  Unallocated Suspense                       500
```

Now it follows Pattern D when Carol submits.

### Pattern E2: Item Confirmed as Fraudulent / Billing Error

Investigation reveals the charge is a billing error or unauthorised transaction.

**File AMEX dispute. While dispute is in progress, item stays in Unallocated Suspense.**

**If dispute is successful (AMEX issues credit):**
```
Dr.  AMEX Clearing                  500
   Cr.  Unallocated Suspense                       500
```

The credit will appear on the next AMEX statement, reducing the cash payment on the 19th.

**If dispute is denied:**
- Escalate to management
- Treat as a write-off if no other party is liable:
```
Dr.  Expense — Bad Debt / Loss      500
   Cr.  Unallocated Suspense                       500
```

### Pattern E3: Item Confirmed but Owner No Longer at Firm

Item belongs to a former employee whose AMEX card wasn't cancelled in time. They cannot be charged back.

**Management write-off required:**
```
Dr.  Expense — Compensation / HR    500
   Cr.  Unallocated Suspense                       500
```

Document the control failure for next audit cycle (cardholder offboarding process).

## Pattern F: Personal Card / Out-of-Pocket Expense Lifecycle

Personal card and out-of-pocket expenses follow a different flow from AMEX because **the Company has not yet paid anyone** at the point of submission. Suspense accounts are not needed — if the employee never submits, no entry exists.

### Pattern F1: Submitted, Reviewed, Approved as Reimbursable

Standard happy path. Frank pays HK$3,000 for client meeting transport on personal card on April 5. Submits April 8. Sally approves April 10. Xero auto-posts.

**April 10 — Xero auto-post (automatic on approval):**
```
Dr.  Expense — Reimbursable             3,000
   Cr.  Employee Reimbursement Payable             3,000
```

**Later — Company pays Frank via bank transfer (typically weekly/monthly batch):**
```
Dr.  Employee Reimbursement Payable     3,000
   Cr.  Cash                                       3,000
```

**Net effect:**
- P&L: +3,000 expense (in April)
- Cash: -3,000 (when reimbursement paid)
- Employee Reimbursement Payable: 0 (raised and cleared)

### Pattern F2: Submitted, Reviewed, Identified as PEP

Grace pays HK$5,000 for PEP fund LP conference registration on personal card. Submits, tagged as PEP. Approved.

**Xero auto-post (automatic, naively books to Expense):**
```
Dr.  Expense                            5,000
   Cr.  Employee Reimbursement Payable             5,000
```

**Sally's reclassification:**
```
Dr.  Receivable from PEP Fund III       5,000
   Cr.  Expense                                    5,000
```

**Company pays Grace:**
```
Dr.  Employee Reimbursement Payable     5,000
   Cr.  Cash                                       5,000
```

**Later — PEP Fund III pays quarterly recharge:**
```
Dr.  Cash                               5,000
   Cr.  Receivable from PEP Fund III               5,000
```

**Net effect:**
- P&L: 0 (raised then reclassified)
- Cash: 0 (paid Grace, received from PEP fund)
- Receivable from PEP Fund III: 0 (raised and settled)
- Employee Reimbursement Payable: 0 (raised and cleared)

### Pattern F3: Submitted, Reviewed, Rejected as Non-Reimbursable

Henry submits HK$2,000 for personal shopping on personal card. Sally rejects.

**No entry needed.** The Company never paid Henry. Xero does not auto-post (rejected items don't sync). Henry simply absorbs the cost on his personal card.

**This is the key operational advantage of personal card over AMEX:** rejections create no accounting work because no cash ever moved. With AMEX, rejections create a Staff Receivable that requires chasing.

### Pattern F4: Submitted but Not Yet Approved at Month-End (Personal Card Accrual)

Grace submits HK$8,000 conference fee on April 28. By April 30 month-end, Sally has not reviewed. The submission represents Grace's assertion that this is a business expense, so accrual is appropriate.

**April 30 — Manual accrual:**
```
Dr.  Expense — Reimbursable             8,000
   Cr.  Accrued Expenses                           8,000
```

**P&L impact in April: +8,000** ✓ (correctly in period of incurrence)

**May 5 — Sally approves, Xero auto-posts:**
```
Dr.  Expense — Reimbursable             8,000
   Cr.  Employee Reimbursement Payable             8,000
```

**May 5 — Sally's manual reversal of accrual:**
```
Dr.  Accrued Expenses                   8,000
   Cr.  Expense — Reimbursable                     8,000
```

**Net May P&L impact: zero.** ✓ (Auto-post nets with accrual reversal.)

**May — Company pays Grace:**
```
Dr.  Employee Reimbursement Payable     8,000
   Cr.  Cash                                       8,000
```

### Pattern F5: Submitted Awaiting Approval, Later Reclassified to PEP

Same as F4 but during Sally's review in May, the item is identified as PEP-related.

**April 30 — Manual accrual (assumed reimbursable):**
```
Dr.  Expense — Reimbursable             8,000
   Cr.  Accrued Expenses                           8,000
```

**May — Xero auto-posts on approval:**
```
Dr.  Expense                            8,000
   Cr.  Employee Reimbursement Payable             8,000
```

**May — Sally's three corrections:**

Entry 1: Reverse the accrual
```
Dr.  Accrued Expenses                   8,000
   Cr.  Expense                                    8,000
```

Entry 2: Reclassify to PEP
```
Dr.  Receivable from PEP Fund           8,000
   Cr.  Expense                                    8,000
```

Entry 3: Pay Grace (when reimbursement batch runs)
```
Dr.  Employee Reimbursement Payable     8,000
   Cr.  Cash                                       8,000
```

**Net P&L by month:**
- April: +8,000 (accrual)
- May: +8,000 (auto-post) -8,000 (reverse accrual) -8,000 (reclassify PEP) = -8,000
- **Cumulative: 0** ✓ (correct — PEP never hits Company P&L)

### Pattern F6: Submitted Awaiting Approval, Later Rejected

Same as F4 but Sally rejects on May 5.

**April 30 — Manual accrual:**
```
Dr.  Expense — Reimbursable             8,000
   Cr.  Accrued Expenses                           8,000
```

**May — Sally rejects (no Xero auto-post). Reverse the accrual:**
```
Dr.  Accrued Expenses                   8,000
   Cr.  Expense — Reimbursable                     8,000
```

**No further entries.** Cash never left the Company. Employee absorbs cost on personal card.

**Net P&L impact:**
- April: +8,000
- May: -8,000
- **Cumulative: 0** ✓

### Personal Card Pattern Summary

| Pattern | Submission status | Resolution | Cash movement |
|---|---|---|---|
| F1 | Approved as reimbursable | Standard reimbursement | Cash out when employee paid |
| F2 | Approved as PEP | Reclassify to PEP receivable | Cash out (employee), in (PEP fund) |
| F3 | Rejected | **No entry** | None |
| F4 | Submitted-not-approved at month-end (reimbursable) | Accrual + reversal | Cash out next month |
| F5 | Submitted-not-approved, later PEP | Accrual + reversal + reclassification | Cash flows offset |
| F6 | Submitted-not-approved, later rejected | Accrual + reversal | None |

### Key Operational Principles for Personal Card

1. **No suspense accounts needed.** Cash has not left the Company. If the employee never submits, no entry exists — the expense simply doesn't appear in the books.

2. **Accrue only what's submitted.** Without a submission, there's no employee assertion that an expense exists. Don't accrue speculatively for personal-card expenses unless using a documented trailing-average methodology for materially-sized populations.

3. **Rejections are clean.** Unlike AMEX (where rejection creates Staff Receivable), rejected personal-card expenses require no entry.

4. **PEP reclassification works identically.** The classification logic is the same; only the credit account differs (Employee Reimbursement Payable instead of AMEX Clearing/Cash).

5. **Two-stage cash flow.** Personal card expenses involve two cash movements separated in time: (a) employee pays vendor with personal card immediately, (b) Company reimburses employee later. The accounting only touches Company cash at stage (b).

## Pattern G: Mixed Reclassification (Partial PEP, Partial Reimbursable)

**Scenario:** March accrual for HK$20k as reimbursable. Approved in April. Sally identifies HK$15k as PEP, HK$5k as truly reimbursable.

**March 31 (accrual):**
```
Dr.  Expense                     20,000
   Cr.  Accrued Expenses                         20,000
```

**April (Xero auto-post):**
```
Dr.  Expense                     20,000
   Cr.  AMEX Payable                             20,000
```

**April (manual corrections — three entries):**
```
Entry 1: Reverse full accrual
Dr.  Accrued Expenses            20,000
   Cr.  Expense                                  20,000

Entry 2: Reclassify PEP portion
Dr.  Receivable from PEP Fund    15,000
   Cr.  Expense                                  15,000

Entry 3: [Nothing — the 5k reimbursable stays as expense via Xero auto-post]
```

**Net April P&L impact: 20,000 - 20,000 - 15,000 = -15,000**

**Cumulative across March + April:** 20,000 - 15,000 = 5,000 (the truly reimbursable portion). ✓

## Pattern H: Prior Period Adjustment for Material Items

**Scenario:** Material expense identified in a closed period. Auditor materiality threshold is HK$X.

If amount > materiality threshold AND prior period is still open:
- Reopen prior period
- Post correcting entry to prior period
- Re-close

If amount > materiality threshold AND prior period is closed:
- Discuss with auditors
- May require prior-period adjustment disclosure
- Or treat as current-period correction with note

If amount < materiality threshold:
- Treat as current-period item
- Document the timing difference for audit trail

## Pattern I: PEP Fund Quarterly Recharge Receipt

**Scenario:** PEP fund pays quarterly recharge of HK$70,000 covering accumulated receivables.

```
Dr.  Cash                        70,000
   Cr.  Receivable from PEP Fund                 70,000
```

No P&L impact. Receivable balance reduces by HK$70,000.

**Watch for:**
- If recharge amount differs from receivable balance (e.g., dispute, FX), the difference must be investigated before posting
- Recharge should clear specific items in the PEP receivable ledger, not generic FIFO — maintain aging by item

## Pattern J: Staff Receivable Settlement

**Scenario:** Employee repays HK$10,000 of non-reimbursable charges.

```
Dr.  Cash                        10,000
   Cr.  Staff Receivable                         10,000
```

If payroll deduction is used:
```
Dr.  Payroll / Salaries Payable  10,000
   Cr.  Staff Receivable                         10,000
```

## Self-Correcting Nature of Accruals

A critical concept: **the accrual mechanism is self-correcting over time.** When Sally over-accrues (e.g., accrues 20k as Company expense when 15k is actually PEP), the subsequent reclassification entries automatically correct the cumulative P&L.

| Month | What Happens | P&L Impact |
|---|---|---|
| March | Accrue 20k as reimbursable | +20k |
| April | Identify 15k as PEP, reclassify | -15k |
| **Cumulative** | | **+5k** ✓ |

The cumulative +5k matches the truly reimbursable portion. The March P&L is initially overstated by 15k; April corrects it. Over a multi-month view, the books are correct.

**This is acceptable because:**
1. Sally made the best estimate available at March 31
2. The correction happens promptly in April (not December)
3. The amount is typically immaterial for any single month
4. Auditors are comfortable with consistent estimation methodology

## Reclassification Frequency Watch

If reclassifications are a frequent occurrence (>10% of accrued items per month), the root cause is **upstream tagging failure**. Recommend:
- Mandatory PEP tag at Expensify submission (required field, not optional)
- Sally's review at submission stage to catch misclassifications before accrual
- Pre-approval for any expense > HK$5,000 to force classification clarity

The downstream accounting can absorb occasional reclassifications. It cannot absorb systematic mis-tagging.
