# Classification Template

Every AMEX line item and Expensify submission must be classified into one of five categories. This file defines the rules for each category and the data structure to use.

## The Five Categories

### 1. Company Reimbursable Expense

**Definition:** A valid business expense incurred for the Company's own activities, where the Company is the economic bearer.

**Examples:**
- Client dinner attended by Company staff (not a PEP fund client)
- Office supplies
- Internal team meals (OT meals)
- Business travel for Company business
- Software subscriptions used by Company staff

**Treatment:** Dr. Expense (P&L) / Cr. AMEX Clearing or Cash or Accrued Expenses

**Risk:** Initial classification may turn out to be PEP after Sally's review. This is normal; reclassification entries handle it.

### 2. PEP Fund Expense

**Definition:** An expense economically borne by a PEP fund (Private Equity Programme fund), where the Company is acting as paying agent only. The Company fronts the cash; the PEP fund reimburses (typically quarterly with management fees).

**Examples:**
- Travel for due diligence on a PEP portfolio investment
- Legal fees specific to PEP fund activities
- Marketing or fundraising costs for a specific PEP fund
- Meals with PEP fund prospects or LPs

**Treatment:** Dr. Receivable from PEP Fund (Balance Sheet) / Cr. AMEX Clearing or Cash

**Never hits P&L.** Not at any stage. When the PEP fund pays, it clears the receivable.

**Identification:** Must be tagged "PEP-related" in Expensify at submission. If not tagged, Sally must identify during review.

### 3. Non-Reimbursable (Employee Owes Firm)

**Definition:** Expense charged on Company AMEX or submitted for reimbursement that fails policy review — personal expense, exceeds policy limit, missing receipt, outside business purpose.

**Examples:**
- Personal shopping on corporate card
- Meal exceeding per diem with no business justification
- Expense lacking receipt where receipt was required
- Travel outside approved scope

**Treatment:** Dr. Staff Receivable (Balance Sheet) / Cr. AMEX Clearing or Cash

**Never hits P&L.** Employee must repay the firm directly. Do not net against future reimbursable expenses (creates negative AMEX balance issues).

### 4. Prepayment (Multi-Period)

**Definition:** Payment for goods or services covering multiple accounting periods. Common examples: quarterly or annual subscriptions, insurance, software licences.

**Examples:**
- Q1 software subscription paid in January (covers Jan–Mar)
- Annual professional membership fee
- Quarterly cloud service prepayment

**Treatment:**
- Step 1: Dr. Prepayment (Balance Sheet) / Cr. AMEX Clearing
- Step 2: Each period, amortise: Dr. Expense (P&L) / Cr. Prepayment

**Materiality rule:** For items under HK$10k, simplify and book to expense in month of submission. Only material prepayments (>HK$10k) warrant proper amortisation.

**Routing rule:** Material recurring prepayments (annual insurance, large software contracts) should not go through Expensify at all. They should be handled directly by Cornerstone via invoice.

### 5. Unidentified / Unsubmitted

There are **two distinct sub-categories**, each routing to a different suspense account.

#### 5a. Unsubmitted (AMEX Unsubmitted Suspense)

**Definition:** AMEX charge exists on the statement with a clearly identifiable cardholder, but the employee has not yet submitted to Expensify.

**Examples:**
- Carol Chan's corporate AMEX shows a HK$3,000 hotel charge — she's a known frequent traveler, hasn't submitted yet
- Brian Lee's AMEX shows a HK$500 taxi charge from last week, awaiting his expense submission

**Treatment:** Dr. AMEX Unsubmitted Suspense / Cr. AMEX Clearing

**Action:** Chase the employee. Expected resolution time: days to weeks.

#### 5b. Unidentified (Unallocated Suspense)

**Definition:** AMEX charge exists on the statement but cannot be tied to a specific employee or business purpose from available information.

**Examples:**
- Charge on a card number not currently mapped to any employee (possibly a former employee whose card wasn't cancelled)
- Vendor name that doesn't match any known supplier or employee travel pattern
- Charge that may be fraudulent or a billing error
- Charge on a shared/team card with no description

**Treatment:** Dr. Unallocated Suspense / Cr. AMEX Clearing

**Action:** Investigate. Possible outcomes:
- Identify the employee → move to AMEX Unsubmitted Suspense or directly to a classification
- Confirm fraud or billing error → dispute with AMEX
- Confirm legitimate but employee no longer at firm → write off after management approval

**Never hits P&L** until resolved.

**Why the distinction matters:**

| | AMEX Unsubmitted | Unallocated |
|---|---|---|
| Cardholder known? | Yes | No |
| Action | Chase employee | Investigate |
| Resolution speed | Days–weeks | Weeks–months (or unresolvable) |
| Audit signal if growing | Submission discipline | Control weakness / fraud risk |

A well-managed expense cycle has minimal Unallocated Suspense activity. Persistent Unallocated balances warrant a controls review.

## Classification Data Structure

For each AMEX line and each Expensify submission, capture:

| Field | Type | Notes |
|---|---|---|
| Source | AMEX / Expensify-PersonalCard / Expensify-AMEX / Both | Where the data point comes from. AMEX-only means a charge on the statement; Expensify-PersonalCard means employee fronted on personal card; Expensify-AMEX means an Expensify submission backed by AMEX charge. |
| Payment Method | AMEX / Personal Card / Cash | Critical for choosing the right bridging account |
| Date | Date | Transaction date (not submission/approval date) |
| Employee | Text | Cardholder or claimant |
| Merchant | Text | Vendor name |
| Amount (HKD) | Number | Convert FX at AMEX rate or OANDA mid-market |
| Description | Text | Business purpose |
| Category | Enum | One of the five categories above |
| PEP Fund (if applicable) | Text | Which fund bears the cost |
| Prepayment period (if applicable) | Date range | E.g., Jan 1 – Mar 31 |
| Status | Submitted / Approved / Pending | Workflow state in Expensify |
| Confidence | High / Medium / Low | How sure are we of the classification? |
| Notes | Text | Anything relevant for audit trail |

## Payment Method Determines the Credit Side of the Journal

| Payment Method | Credit account (when expense is recognised) | When cash leaves |
|---|---|---|
| AMEX | AMEX Clearing (allocated from statement) | 19th of next month (Company pays AMEX) |
| Personal Card | Employee Reimbursement Payable | When Company pays employee (post-approval) |
| Cash (out-of-pocket) | Employee Reimbursement Payable | When Company pays employee (post-approval) |

Personal card and out-of-pocket expenses are treated identically — both create Employee Reimbursement Payable. AMEX expenses use the AMEX Clearing flow instead.

## Classification Decision Tree

```
Is the item on the AMEX statement?
├── Yes → Is there an Expensify submission?
│   ├── Yes → Is it approved?
│   │   ├── Yes → Use Sally's classification from Expensify (high confidence)
│   │   └── No (submitted only) → Use employee's category tag (medium confidence)
│   └── No → AMEX Unsubmitted Suspense (do not classify P&L impact)
└── No → Is there an Expensify submission?
    ├── Yes (personal card) → Use employee's category tag, await approval
    └── No → Should not be in this exercise
```

## Common Misclassifications to Watch For

1. **PEP expenses tagged as reimbursable:** Most common error. Always re-check items related to PEP fund activities even if the employee tagged as "Company reimbursable."

2. **Client meals on business trips:** These are separately reimbursable on actuals, NOT covered by per diem. Don't book as Company travel meal.

3. **Annual subscriptions paid mid-year:** Easy to miss the prepayment treatment. Check the period coverage stated on the invoice.

4. **Shared meals (two employees, one bill):** Should be split 50/50 in Expensify. Watch for duplicate-side submissions.

5. **Foreign currency charges:** Confirm FX rate used. AMEX rate for AMEX charges, OANDA mid-market for personal card.

## Output Format

Build the classification as a table that becomes the first content sheet in the Excel output. Each row is one classified item. The Summary Journal sheet aggregates these into the final journal entry.
