# Worked Examples

Full walkthroughs showing every double entry for representative scenarios. Use these as reference when the user asks "what's the entry for [scenario]?"

## Example 1: Simple Month-End — All Categories Present

### Setup
- AMEX statement: HK$100,000 paid March 19
- HK$50k PEP-related (submitted, tagged PEP)
- HK$30k reimbursable (20k submitted by Mar 31, 10k still unsubmitted)
- HK$10k Q1 subscriptions (Jan/Feb/Mar)
- HK$10k non-reimbursable (employee will repay)

### March 31 Summary Entry

```
Dr.  Receivable from PEP Fund          50,000
Dr.  Expense (Reimbursable)            30,000   [20k seen in Expensify + 10k seen on AMEX]
Dr.  Prepayment                        10,000
Dr.  Expense (Subscriptions)           10,000   [Q1 amortise all in Mar]
Dr.  Staff Receivable                   8,000   [Assuming 8k identified non-reimb at Mar 31]
Dr.  Unallocated Suspense               2,000   [2k unidentified at Mar 31]
   Cr.  AMEX Clearing                          100,000
   Cr.  Prepayment                              10,000   [Amortise out within Mar]
```

**Verification:**
- Total Dr = 50+30+10+10+8+2 = 110,000
- Total Cr = 100 + 10 = 110,000 ✓
- AMEX Clearing nets to zero ✓
- P&L impact = 30k + 10k = 40,000 ✓

### March 31 Closing Balances

| Account | Balance |
|---|---|
| Cash | -100,000 |
| Receivable from PEP Fund | +50,000 |
| Staff Receivable | +8,000 |
| Unallocated Suspense | +2,000 |
| Prepayment | 0 (in and out) |
| AMEX Clearing | 0 |
| Retained Earnings (via P&L) | -40,000 |

**Balance check:** -100 + 50 + 8 + 2 + 40 = 0 ✓

---

## Example 2: Complex — Reclassification + Suspense Resolution

### Setup (Same as Example 1, with additional twists)
- All of Example 1 setup
- Plus: In April, the 20k submitted reimbursable items get approved. Sally identifies 15k as actually PEP (not reimbursable as originally tagged).
- Plus: In April, the 10k still-unsubmitted item remains unsubmitted (rolls forward).
- Plus: In April, the 2k unidentified turns out to be a non-reimbursable charge by an employee (identified when they finally submit).

### March 31 Summary Entry (same as Example 1)

(see above)

### April 30 Summary Entry

What needs to happen in April:
- Xero auto-posts the approved 20k as Expense (automatic)
- Reverse the prior March accrual for 20k
- Reclassify 15k of that to PEP receivable
- Clear the 2k Unallocated Suspense to Staff Receivable

```
Dr.  Accrued Expenses                  20,000   [Release March accrual for approved items]
Dr.  Receivable from PEP Fund          15,000   [Reclassify PEP portion]
Dr.  Staff Receivable                   2,000   [Suspense resolution]
   Cr.  AMEX Payable                            20,000   [Net effect of Xero auto-post]
   Cr.  Expense (Reimbursable)                  15,000   [Reverse over-accrual for PEP]
   Cr.  Unallocated Suspense                     2,000   [Clear suspense]
```

Wait — let me unpack this more carefully. The Xero auto-post and reversal nets to zero in P&L, but the entries still need to appear. Restructured:

**April individual entries:**

```
[Automatic — Xero auto-post on approval]
Dr.  Expense                           20,000
   Cr.  AMEX Payable                            20,000

[Manual — release March accrual]
Dr.  Accrued Expenses                  20,000
   Cr.  Expense                                 20,000

[Manual — reclassify PEP portion]
Dr.  Receivable from PEP Fund          15,000
   Cr.  Expense                                 15,000

[Manual — clear suspense]
Dr.  Staff Receivable                   2,000
   Cr.  Unallocated Suspense                     2,000
```

**April aggregate summary entry (manual entries only):**

```
Dr.  Accrued Expenses                  20,000
Dr.  Receivable from PEP Fund          15,000
Dr.  Staff Receivable                   2,000
   Cr.  Expense                                 35,000   [20k reversal + 15k reclassification]
   Cr.  Unallocated Suspense                     2,000
```

**Net April P&L impact:**
- Auto-post: +20,000
- Reversal: -20,000
- Reclassification: -15,000
- **Total: -15,000**

This -15,000 corrects the March over-accrual (where 15k was wrongly booked as Company expense).

### April 30 Closing Balances

| Account | March 31 | April Δ | April 30 |
|---|---|---|---|
| Cash | -100,000 | — | -100,000 |
| Receivable from PEP Fund | +50,000 | +15,000 | +65,000 |
| Staff Receivable | +8,000 | +2,000 | +10,000 |
| Unallocated Suspense | +2,000 | -2,000 | 0 |
| AMEX Payable | 0 | -20,000 | -20,000 |
| Accrued Expenses | 0 | +20,000 (released) | 0 |
| AMEX Unsubmitted Suspense | 0 (none at Mar 31) | — | 0 |
| Retained Earnings | -40,000 | +15,000 | -25,000 |

Wait — there's still the 10k still-unsubmitted from March that hasn't been addressed. Let me revisit.

Actually, in Example 1, the 10k unsubmitted was accrued to Expense at March 31. That was the simple version. In the corrected approach (using AMEX Unsubmitted Suspense), the 10k should have gone to suspense, not expense.

Let me redo Example 1 with the conservative approach:

---

## Example 1 Revised — Conservative Treatment for Unsubmitted Items

### March 31 Summary Entry (Conservative)

```
Dr.  Receivable from PEP Fund          50,000
Dr.  Expense (Reimbursable)            20,000   [Only the submitted 20k — assertion present]
Dr.  AMEX Unsubmitted Suspense         10,000   [Unsubmitted 10k — no assertion yet]
Dr.  Prepayment                        10,000
Dr.  Expense (Subscriptions)           10,000   [Q1 amortise]
Dr.  Staff Receivable                   8,000
Dr.  Unallocated Suspense               2,000
   Cr.  AMEX Clearing                          100,000
   Cr.  Prepayment                              10,000
```

**P&L impact at March 31: +30,000** (down from +40,000 in non-conservative version)

Then if the 10k turns out to include a 5k PEP and 5k truly reimbursable when finally submitted in May:

### May Summary Entry (clearing the AMEX Unsubmitted Suspense)

```
[Xero auto-posts the 10k]
Dr.  Expense                           10,000
   Cr.  AMEX Payable                            10,000

[Manual: clear suspense, reclassify split]
Dr.  AMEX Unsubmitted Suspense (Cr direction)
                                       10,000  [release suspense]
Wait this is wrong — let me restart this entry

[Manual: clear the suspense and route to correct accounts]
Dr.  Receivable from PEP Fund           5,000   [PEP portion]
Dr.  Expense (Reimbursable)             5,000   [Stays in May P&L — first time recognised]
   Cr.  AMEX Unsubmitted Suspense                10,000
```

Then to offset the Xero auto-post (which double-counted with the manual entry above):
```
Dr.  AMEX Payable                       5,000   [Offset auto-post for the reimbursable portion]
Dr.  Receivable from PEP Fund (already booked)
... 
```

This is getting tangled. Let me simplify.

**The simpler approach for AMEX Unsubmitted Suspense:**

When the suspense item is finally submitted and approved:
1. Xero auto-posts to Expense as normal
2. Manual entry: Dr. AMEX Unsubmitted Suspense (release) / Cr. AMEX Payable (because Xero's auto-post credited AMEX Payable, but the AMEX was actually paid back in March from cash to AMEX Clearing — the AMEX Unsubmitted Suspense is what holds the value)
3. Then PEP reclassification if applicable

Net result for the 10k item:
- May P&L: +10k (Xero) - 5k (PEP reclassification) = +5k truly reimbursable
- AMEX Unsubmitted Suspense: cleared
- Receivable from PEP: +5k

That's correct. The P&L recognition happens in May (the period of submission), not March (the period of incurrence). This is the trade-off of using the conservative AMEX Unsubmitted Suspense approach — you get correct classification but at the cost of timing.

---

## Example 3: Pure PEP Quarterly Recharge

### Setup
- Over Q1, accumulated Receivable from PEP Fund = HK$170,000 (50k Jan + 60k Feb + 60k Mar)
- PEP fund pays HK$170,000 on April 15

### April 15 Entry

```
Dr.  Cash                             170,000
   Cr.  Receivable from PEP Fund              170,000
```

**P&L impact: zero.**

If the PEP fund disputes and pays only HK$160,000:

```
Dr.  Cash                             160,000
Dr.  [Investigate — Disputed Receivable]
                                      10,000
   Cr.  Receivable from PEP Fund              170,000
```

The HK$10,000 disputed amount stays on the books pending resolution. Do NOT write off without management approval.

---

## Example 4: Prepayment Over Multiple Periods

### Setup
- Annual software subscription paid in February: HK$120,000
- Covers Feb 1, 2025 – Jan 31, 2026 (12 months)
- Monthly amortisation: HK$10,000

### February Entry (initial booking)

```
Dr.  Prepayment                       120,000
   Cr.  AMEX Clearing (or Cash)               120,000
```

### Each Month-End (Feb through Jan 2026)

```
Dr.  Expense (Subscriptions)           10,000
   Cr.  Prepayment                              10,000
```

By Jan 31, 2026, the Prepayment balance for this item is zero. Total expense recognised: HK$120,000 evenly across 12 months.

**Note:** This kind of material annual prepayment should generally NOT go through Expensify. It should be invoiced and paid directly via Cornerstone. The Excel template should flag any prepayment >HK$30,000 for review.

---

## Example 5: Non-Reimbursable Employee Charge

### Setup
- Employee charges HK$5,000 personal shopping on corporate AMEX in March
- Identified as non-reimbursable on submission
- Employee repays via bank transfer in April

### March Treatment

```
Dr.  Staff Receivable                   5,000
   Cr.  AMEX Clearing                            5,000
```

(Part of the AMEX statement allocation. The Company paid AMEX in March; the employee now owes the Company.)

### April (employee repays)

```
Dr.  Cash                               5,000
   Cr.  Staff Receivable                         5,000
```

**P&L impact at any point: zero.** ✓

---

## Example 6: Shared Meal (Two Employees)

### Setup
- Two Company employees have dinner together while travelling. Bill: HK$2,000.
- One employee pays on AMEX. Both employees submit half via Expensify (HK$1,000 each).

### Treatment in Expensify

Employee A (payer): submits HK$2,000 to Expensify, marks as "shared meal" and assigns HK$1,000 to Employee B
Employee B: receives the HK$1,000 allocation; no out-of-pocket

### Accounting Treatment

```
Dr.  Expense (Meal — Employee A)        1,000
Dr.  Expense (Meal — Employee B)        1,000
   Cr.  AMEX Clearing                            2,000
```

Both employees get their share allocated to their cost centre/department. Single AMEX charge fully cleared.

**Note:** Under the recommended flat per diem policy, this whole exercise disappears. Each employee receives their per diem; what they spend it on (shared meal or otherwise) is irrelevant.

---

## Example 7: FX Conversion

### Setup
- Employee travels to London. Hotel charged on AMEX: GBP £500
- AMEX converts at GBP/HKD 9.85 = HK$4,925
- OANDA mid-market rate on transaction date: 9.80

### Treatment

For AMEX charges, **use the AMEX rate**:
```
Dr.  Expense (Travel)                   4,925
   Cr.  AMEX Clearing                            4,925
```

For personal card or cash expenses, use OANDA mid-market on transaction date:
```
Dr.  Expense (Travel)                   4,900
   Cr.  Accrued Expenses / Employee Payable      4,900
```

The HK$25 difference (AMEX rate vs OANDA) is an FX cost embedded in the AMEX charge. Acceptable — do not separately track unless the spread is unusually wide.

---

## Example 8: Personal Card Reimbursement — Full Lifecycle

### Setup
- Employee Frank pays HK$3,000 for a client dinner on personal credit card on March 25
- Submits to Expensify on April 5
- Sally reviews, approves on April 10
- Xero auto-posts on April 10
- Company pays Frank via bank transfer on April 25 (monthly reimbursement batch)

### March 31 (Month-End)

Frank has not yet submitted. Sally has no AMEX statement to spot it.

**Treatment options:**

**Option A — No accrual (if immaterial):**
```
No entry. Accept the timing difference.
```

**Option B — Trailing average accrual (if material):**
```
Dr.  Expense (Accrual estimate)         [Estimate based on history]
   Cr.  Accrued Expenses                            [Same amount]
```

For this example, assume Option A (HK$3,000 is immaterial).

### April 5 (Frank Submits)

No accounting entry. Submission is a workflow event, not a journal entry.

### April 10 (Approval — Xero Auto-Posts)

```
Dr.  Expense (Client Entertainment)        3,000
   Cr.  Employee Reimbursement Payable               3,000
```

**P&L impact in April: +3,000.**

### April 25 (Company Pays Frank)

```
Dr.  Employee Reimbursement Payable        3,000
   Cr.  Cash                                          3,000
```

**P&L impact: zero.** The expense was already recognised on April 10.

### Final Position

| Account | Net Movement |
|---|---|
| Cash | -3,000 (paid to Frank) |
| Expense | +3,000 (recognised April) |
| Employee Reimbursement Payable | 0 (raised then paid) |

**Timing imperfection:** The expense was economically incurred March 25 but landed in April's P&L. Acceptable for immaterial amounts.

---

## Example 9: Personal Card — Submitted but Not Yet Approved at Month-End

### Setup
- Employee Grace incurs HK$8,000 conference fee on personal card on April 8
- Submits to Expensify on April 15
- At April 30, still awaiting Sally's review
- Approved May 5

### April 30 (Month-End — Submitted but Not Approved)

Grace has submitted, so the assertion exists. Sally accrues:

```
Dr.  Expense (Training & Development)      8,000
   Cr.  Accrued Expenses                              8,000
```

**P&L impact in April: +8,000.** ✓ (Correctly in the month of incurrence.)

### May 5 (Approval — Xero Auto-Posts)

```
Dr.  Expense (Training & Development)      8,000
   Cr.  Employee Reimbursement Payable               8,000
```

### May 5 (Sally's Manual Reversal)

```
Dr.  Accrued Expenses                      8,000
   Cr.  Expense (Training & Development)              8,000
```

**Net May P&L impact: zero.** ✓ (Auto-post +8,000 nets with reversal -8,000.)

### May (Company Pays Grace)

```
Dr.  Employee Reimbursement Payable        8,000
   Cr.  Cash                                          8,000
```

### Cumulative

| Month | P&L | Cash | Employee Payable |
|---|---|---|---|
| April | +8,000 | 0 | 0 |
| May | 0 | -8,000 | 0 (raised then paid) |
| **Total** | **+8,000** | **-8,000** | **0** |

Expense correctly sits in April. Cash flows in May. Everything reconciles.

---

## Example 10: Personal Card PEP Expense

### Setup
- Employee Henry pays HK$5,000 for legal advisory on personal card for PEP Fund III
- Tagged as PEP in Expensify at submission
- Approved in April

### April (Xero Auto-Posts)

```
Dr.  Expense                               5,000
   Cr.  Employee Reimbursement Payable               5,000
```

### April (Sally Reclassifies to PEP)

```
Dr.  Receivable from PEP Fund III          5,000
   Cr.  Expense                                       5,000
```

### April (Company Pays Henry)

```
Dr.  Employee Reimbursement Payable        5,000
   Cr.  Cash                                          5,000
```

### Later — PEP Fund III Pays Quarterly Recharge

```
Dr.  Cash                                  5,000
   Cr.  Receivable from PEP Fund III                  5,000
```

### Final Position

| Account | Net Movement |
|---|---|
| Cash | 0 (paid Henry, received from PEP fund) |
| Expense | 0 (booked then reclassified) |
| Employee Reimbursement Payable | 0 |
| Receivable from PEP Fund III | 0 (raised then settled) |

**P&L impact: zero** — correct, as the expense was never economically the Company's.

---

## How to Use These Examples

When a user asks "what's the entry for [X]?", find the closest matching example and adapt. Always:

1. Identify the category (5 categories from classification_template.md)
2. Apply the relevant journal template (journal_templates.md)
3. Check if any reclassifications are needed (reclassification_patterns.md)
4. Verify Debits = Credits and Balance Sheet reconciles
