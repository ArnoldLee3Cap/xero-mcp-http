---
name: expense-monthly-close-builder
description: Build month-end journal entries for the 3 Capital Partners expense cycle — AMEX clearing, accruals, reversals, PEP reclassifications, prepayment amortisation, non-reimbursable receivables, and suspense items. Use this skill whenever the user provides an Expensify report, AMEX statement, or expense data and wants to build the monthly journal, understand accrual flow when expenses lag approval, reconcile Expensify auto-postings against manual accruals, or classify expenses across Company P&L / PEP receivable / staff receivable / prepayment / suspense. Triggers include "build the monthly journal", "AMEX accrual entry", "reclassify PEP expenses", "month-end close for expenses", "reconcile AMEX clearing", or any expense scenario involving timing differences or reclassification. Handles multi-currency activity (AMEX settled in HKD; personal/cash in original currency, Xero translates); prepares DRAFT journals only (separate posting skill posts to Xero). Produces an Excel month-end journal with full audit trail.
---

# Expense Monthly Close Builder

## Purpose

This skill packages the accrual and journal-entry logic for 3 Capital Partners Limited's expense cycle. It handles the structural mismatch between **when cash leaves the bank** (AMEX paid by the 19th), **when expenses are submitted** (up to 60 days later under current policy), and **when expenses are approved and auto-posted to Xero** (whenever Sally + Alex clear them).

The goal: every month-end, produce a single Excel-based summary journal that correctly recognises expenses in the period they were economically incurred, regardless of when Expensify approvals clear.

This skill **prepares** DRAFT journals only — it does **not** post to Xero (a separate posting skill pushes approved drafts). It handles multi-currency activity: AMEX items post in HKD (settled at AMEX's rate); personal/cash items post in their original currency and Xero translates. See "Currency" below and "Posting boundary & handoff". Not financial advice — every entry requires qualified-accountant review.

> **Precondition — orchestrator gate**: Before building the monthly journal, check whether
> `3cp-close-orchestrator` (Mode 1) has been run for this period this session. If it hasn't, say so
> and offer to run it first. If the user explicitly says to skip it and proceed anyway, proceed —
> this is a workflow recommendation, not a hard block.

## Core Accounting Framework

### The Five Expense Categories

Every AMEX charge and Expensify submission must be classified into one of five buckets. The treatment differs for each.

| Category | P&L Impact? | Balance Sheet Account |
|---|---|---|
| **Company reimbursable expense** | Yes — period of incurrence | Expense (P&L) |
| **PEP fund expense** | Never | Receivable from PEP Fund |
| **Non-reimbursable (employee owes firm)** | Never | Staff Receivable |
| **Prepayment (multi-period)** | Spread over benefiting periods | Prepayment → amortised to Expense |
| **Unidentified / unsubmitted** | Hold | AMEX Unsubmitted Suspense or Unallocated Suspense |

### The Three Bridging Accounts

Three balance sheet accounts act as bridges to handle timing differences and identification gaps:

1. **AMEX Clearing Account** — receives cash payment to AMEX on the 19th; cleared as each charge is
   classified. The payment leg itself is a **BANK TRANSACTION, not a journal** (journals cannot
   touch bank accounts): SPEND from DBS HKD, DR 135, reference `AMEXPAY-<MMMYY>`, posted via the
   poster's `create-bank-transaction` and reconciled against the FPS AMEX line on the DBS feed.

2. **AMEX Unsubmitted Suspense** — parks AMEX charges where the **cardholder is identifiable** but no Expensify submission exists yet. The action required is chasing the employee. Resolves when the employee submits to Expensify.

3. **Unallocated Suspense** — parks AMEX charges where the **cardholder or business purpose cannot be identified** from the AMEX statement alone (former employee, shared card, billing error, suspicious activity). The action required is investigation. Resolves when Sally identifies the owner / purpose.

**Critical distinction:**
- AMEX Unsubmitted = "Who submitted this? We know whose card it is, just waiting for them to submit."
- Unallocated = "We don't even know who owns this charge. Investigate."

A growing AMEX Unsubmitted balance signals submission discipline issues. A growing Unallocated balance signals control problems that may require AMEX dispute filing or fraud investigation.

The combined balance of both suspense accounts is a control metric for the month-end close.

### Payment Method Affects the Credit Side

Two distinct expense paths require different bridging accounts. Always determine the payment method before constructing the journal entry.

| Payment Method | Bridging Account | Cash Outflow Timing | Suspense Account? |
|---|---|---|---|
| Corporate AMEX | AMEX Clearing | 19th of next month (Company pays AMEX) | Yes — AMEX Unsubmitted + Unallocated |
| Personal card | Employee Reimbursement Payable | Post-approval when Company pays employee | **No** — cash hasn't left Company |
| Cash / out-of-pocket | Employee Reimbursement Payable | Post-approval when Company pays employee | **No** — cash hasn't left Company |

**Critical implications:**

1. AMEX expenses follow the AMEX Clearing flow. Personal card and out-of-pocket expenses use Employee Reimbursement Payable. The category classification (PEP, Reimbursable, Non-reimbursable, etc.) is the same; only the credit side of the entry changes.

2. **A rejected personal card expense requires NO entry.** The Company never paid anything. Compare to a rejected AMEX expense which requires a Staff Receivable entry (Company already paid AMEX; employee owes the firm).

3. **Personal card expenses never go to suspense.** If an employee doesn't submit a personal card expense, no entry exists — the expense simply doesn't appear in the books. This is fundamentally different from AMEX, where unsubmitted charges still represent cash that left the Company.

4. **Personal card accruals only apply to submitted-but-unapproved items.** Without a submission, there's no employee assertion that an expense exists, so no accrual basis. (Optional: trailing-average accruals for material populations — see Template 4b.)

See `references/journal_templates.md` Template 4 for full personal card treatment and `references/reclassification_patterns.md` Pattern F for the six personal-card lifecycle sub-patterns.

### Currency — AMEX settles HKD; personal/cash post in original currency

Expense activity is mostly HKD but some lines are USD. Currency handling follows the **payment method**, because the FX happens in two different places:

- **Corporate AMEX → HKD.** The AMEX statement settles in **HKD**; AMEX has already converted any foreign charge to HKD **at AMEX's own rate**, and the Company pays HKD. Post AMEX items in **HKD at the settled amount** — use the **report-currency amount (`Amount` / Report Currency = HKD)**. The original merchant currency is informational; the FX is AMEX's and Xero does nothing. **AMEX Clearing therefore stays HKD** and zeroes in HKD.
- **Personal card / cash (Employee Reimbursement Payable) → original currency.** Keep the expense in its **original currency** and post to Xero in that currency; **Xero applies the rate on posting**, exactly like 3CP's treasury and direct-expense USD items. Use the **`Original Amount` (col AA) in `Original Currency` (col Z)** — **not** Expensify's HKD-converted `Amount` (col C). The skill never converts these itself and **never fetches a rate**.

**Consequences:**
- **Option B split applies only to the reimbursement (personal/cash) side.** AMEX-side journals and both suspense accounts are HKD-only. The Employee-Reimbursement journals split by currency — a HKD journal and, where USD out-of-pocket items exist, a USD journal — each balancing in its own currency. **Never sum HKD and USD into one total.**
- The five-category classification (Company / PEP / Staff receivable / Prepayment / Suspense) is **orthogonal to currency** — a USD cash PEP item still goes to PEP Receivable, just in USD.
- **Source columns** (Expense-Level export): AMEX/HKD amount → **C `Amount`** (D `Report Currency`); original-currency amount for personal/cash → **AA `Original Amount`** (Z `Original Currency`); card-vs-cash identified from `Transaction Type` / `Reimbursable` / `Card Details`. Confirm these before a live run.

### The Conservative Classification Rule

| Source of information | Treatment |
|---|---|
| AMEX charge AND Expensify submission AND Sally classification | Book to correct account (full classification available) |
| AMEX charge AND Expensify submission, awaiting approval | Book to expense based on submission assertion (5% reclassification risk acceptable) |
| AMEX charge but no Expensify submission | Park in AMEX Unsubmitted Suspense — do NOT book to expense |
| AMEX charge but cannot identify employee | Park in Unallocated Suspense |

**Rationale:** Once an employee submits to Expensify, they have asserted the expense is a business expense. Without that assertion, no P&L recognition.

## Workflow

When invoked, follow these steps:

### Step 1: Gather Inputs

Ask the user for, or extract from the conversation:
- AMEX statement (total + line items if available)
- Expensify **Expense-Level** export for the month
- Prior month suspense balances (if any items rolled forward)
- Known prepayment items (subscriptions, annual fees) being recharged
- **Amendment inputs** when prior reports were reviewed this period — see "Prior-period amendments" below.

If any of these are missing, note the assumption and proceed. Flag the gap in the output.

#### Reading the Expensify Expense-Level export (confirmed column map, Apr 2026)

| Need | Column | Rule |
|---|---|---|
| Card vs cash (**source**) | **W `Transaction Type`** | `Company Card` → **AMEX** (post HKD); `Cash` → **reimbursable** (post original currency). Authoritative single source. |
| (cross-check only) | X `Reimbursable`, AE `Card Details` | `Company Card`⟺`X=N`⟺card details present; `Cash`⟺`X=Y`⟺no card details. **Re-run this consistency check each month**; if W, X, and AE disagree on any row, flag it rather than guessing. (April: 177/177 consistent.) |
| HKD amount (card) | **C `Amount`** (D `Report Currency`=HKD) | AMEX-settled HKD figure. |
| Original amount (cash) | **AA `Original Amount`** (Z `Original Currency`) | post cash items in original currency; Xero translates. |
| Report status | **BO `Report Display Status`** | **Only `Outstanding` is eligible to post.** **Exclude `Draft`** — draft reports may still change substantially. (April: Outstanding 139, Draft 38.) |
| PEP flag | **N `Tag2`**, value **`PE Program`** | `N == "PE Program"` → PEP category (→ Receivable from PEP Fund). Other N values (Company, Company – <name>, individual names) are company/staff allocations, not PEP. |
| Report identity | **AY `Report ID`** | key for amendment diffing across months. |

Note: column Y is `Billable` (not a cash flag); do not use it for card/cash.

#### Prior-period amendments (non-routine review)

3CP reviews/approves/rejects Expensify reports on a **non-routine** basis — e.g. March and April reports may both be reviewed in May. Adjustments are booked in the **month of review** (the current close), not back-dated.

Each month the user provides: the **current** month's Xero export, plus — for any prior month whose reports changed — **both** the **updated** and the **original** prior-month Expensify exports. Diff them on **AY `Report ID`** to find what changed (status flips, amount changes, rejections), and book the corresponding adjustment entry in the current period (e.g. a rejected expense previously accrued → reverse it now; an amount revised on approval → book the delta). Reference these `3CP-EXP-<current-period>-ADJ-<CCY>`. See `references/reclassification_patterns.md`.

### Step 2: Classify Every Item

For each AMEX line and Expensify submission, classify into one of the five categories. Build the classification table — see `references/classification_template.md` for the exact structure.

When classification is ambiguous, default to the **most conservative** treatment (suspense over expense, receivable over expense). Surface ambiguous items for user judgment rather than guessing.

### Step 3: Detect Reclassifications and Double-Counts

Two critical checks:

**Reclassification check:** Has any item been previously accrued as one category but should now be reclassified? Most common: previously accrued as Company expense, now identified as PEP. This requires reversing the prior accrual AND posting to the correct account.

**Double-count check:** Has Xero auto-posted any expense that was already accrued in a prior month? If yes, the auto-post must be neutralised by releasing the prior accrual.

See `references/reclassification_patterns.md` for the full set of correction patterns.

### Step 4: Build the Summary Journal

Construct the month-end summary journal. The structure depends on the inputs but always follows the principle: **debits = credits, and balance sheet must reconcile** — checked **within each currency**. Split by currency per Option B: the AMEX-side journal is HKD; the personal/cash reimbursement journal splits into HKD and (where USD out-of-pocket items exist) USD. Post each in its own currency; Xero translates the USD journal on posting.

See `references/journal_templates.md` for standard journal structures. *(The journal templates and `scripts/build_close_template.py` currently assume a single currency; they need the currency dimension threaded through — per-currency sub-journals and a `currency` field — to fully emit the Option B output. Flag this as a follow-up if running before that update.)*

### Step 5: Generate Excel Output

Use the Python script `scripts/build_close_template.py` to generate a structured Excel workbook. The workbook contains:

1. **Inputs** — AMEX statement and Expensify reports captured as data
2. **Classification** — every item classified into one of the five categories
3. **Reclassifications** — corrections from prior months identified
4. **Summary Journal** — single Dr/Cr entry ready to post to Xero
5. **Balance Sheet Check** — verifies the entry balances and reconciles
6. **Suspense Aging** — outstanding suspense items by age

Before running the script, read `/mnt/skills/public/xlsx/SKILL.md` for the xlsx skill — this skill produces an Excel file and the xlsx skill has the environment-specific guidance.

## Critical Rules

1. **PEP expenses never hit the Company P&L.** Always route to Receivable from PEP Fund. If Xero auto-posts a PEP item to expense, reverse immediately.

2. **Non-reimbursable expenses never hit P&L.** Route to Staff Receivable. The employee must repay separately — do not net against future reimbursements.

3. **Unsubmitted AMEX charges go to suspense, not expense.** Without an employee assertion, no P&L recognition.

4. **The AMEX Clearing Account must net to zero each month (in HKD).** AMEX settles in HKD, so clearing is a HKD account. If it doesn't zero, an AMEX charge has not been allocated. Find it before closing.

5. **Reclassifications create two entries, not one.** First release the prior accrual, then post to the correct account. Maintain audit trail.

6. **Auto-post + accrual reversal must net to zero in the new month.** When Xero fires an auto-post, the prior accrual release must equal the auto-post. If it doesn't, either the accrual was wrong or the auto-post is for a different item.

7. **Imperfect accruals are acceptable and self-correct.** Do not chase 100% accuracy. Conservatism and consistency matter more than precision on individual items.

## When to Ask vs. Proceed

**Ask the user when:**
- An AMEX line item cannot be classified from available data
- A prior-month accrual amount is needed but not provided
- The PEP fund identity is unclear (which fund bears the cost)
- A prepayment item's period coverage is ambiguous (Q1? annual? semi-annual?)
- The materiality threshold for retroactive prepayment corrections is unclear

**Proceed with documented assumption when:**
- Standard subscriptions with clear period (e.g., "Microsoft 365 January–March")
- Single-period reimbursable expenses with clear merchant and employee
- Items the user has previously classified in the conversation

## Output Quality Checklist

Before delivering, verify:
- [ ] AMEX Clearing nets to zero (HKD)
- [ ] Only `Outstanding` reports posted (BO); `Draft` excluded
- [ ] Card/cash source taken from W; W/X/AE consistency re-checked, mismatches flagged
- [ ] PEP items = N `Tag2` == "PE Program"
- [ ] Prior-period changes diffed on AY (Report ID); adjustments booked in current period
- [ ] Total debits = Total credits **within each currency** (HKD and USD journals each balance; nothing summed across currencies)
- [ ] Personal/cash items posted in original currency (cols Z/AA), not Expensify's HKD conversion; no rate fetched
- [ ] Each journal carries a unique DRAFT reference for the posting handoff
- [ ] P&L impact matches the truly Company-incurred portion only
- [ ] PEP-related items are on Balance Sheet, not P&L
- [ ] Suspense balances are aged and flagged
- [ ] Any reclassifications from prior months are clearly documented
- [ ] Excel workbook opens correctly and all sheets are populated

## Posting boundary & handoff (preparation only)

This skill **prepares** the month-end journal; it does **not** post. A separate posting skill pushes approved drafts to Xero. Structure the output so that handoff is clean and idempotent:

- **Status: DRAFT.** Never post or imply posting; a human approves in Xero.
- **Unique reference per journal**, so a re-run cannot double-post: `3CP-EXP-<period>-<segment>-<CCY>` — e.g. `3CP-EXP-2026-04-AMEX-HKD` (AMEX-side: clearing, expense, PEP, staff receivable, suspense), `3CP-EXP-2026-04-REIMB-HKD` and `3CP-EXP-2026-04-REIMB-USD` (personal/cash reimbursement side), `3CP-EXP-2026-04-RECLASS-HKD` (prior-period corrections). The posting skill checks the reference does not already exist before posting.
- **One currency per journal (Option B).** AMEX-side journals are HKD; reimbursement journals split HKD / USD. Post in original currency and let Xero translate; never convert in-skill or fetch a rate. This matches the other prep skills (treasury = USD; monthly-journals = HKD +USD for USD supplier invoices), so the posting skill consumes one common contract keyed on currency.
- **Structured payload.** Each journal is expressible as: reference, period/date, narration, **currency**, reversal flag (+ reversal date — accruals reverse at period-end/next-period start), and lines of {account name, debit, credit}. Amounts are in the journal's currency.
- **Reconcile before post.** Only a close whose AMEX Clearing zeros (HKD), whose suspense is aged, and whose checks pass is posting-eligible; ambiguous/suspense items are held back, not posted to expense.
- The posting skill owns the Xero API / MCP connection and authorization — not this skill.

## References

- `references/classification_template.md` — How to build the item-level classification
- `references/journal_templates.md` — Standard journal structures by scenario
- `references/reclassification_patterns.md` — Correction entries for common scenarios
- `references/worked_examples.md` — Full worked examples (simple → complex) with all double entries
- `scripts/build_close_template.py` — Generates the Excel output workbook


## Recognition build (confirmed on May 2026 data)
P&L account per line = **GL Category (col K)** of the Expensify expense-level export (Xero code, e.g. Entertainment=420, Overseas Transport=494, SaaS=413SAAS). Filter **Report Display Status == 'Outstanding'** (exclude Draft). All amounts are **HKD** (Report Currency) — the ManualJournal CSV (HKD-only) works directly; no FX.
- **Company Card** (Transaction Type / Reimbursable=N): `DR <GL Category> / CR 135 AMEX Clearing`.
- **Cash** (Reimbursable=Y): `DR <GL Category> / CR 801 Unpaid Expense Claims`, **one journal per Report ID** so 801 is tracked per report for settlement (open-item schedule).
- **PE Program** (Tag2 == 'PE Program'): DR reclassed to **664** Private Equity Program Expense Receivables.
- Recognition is at **submission** (provisional; amendments handled next month by diffing reviewed prior-month exports on Report ID).
Outputs (all retained): review **workpaper** (.xlsx: summary, AMEX by card, 801 open-item schedule by Report ID, line detail, checklist), **ManualJournal Xero CSV**, and the **contract payload JSON** (for the poster). Run: `scripts/build_expense_recognition.py`.
**Still to add:** AMEX Suspense (855) plug + AMEX statement Bill (need the month's AMEX statements + GL opening 855); the payment/Bill step (DR 801 or 135 / CR AP); numeric account code for Staff Receivable (Non-reimbursable) — when built, use **624 Employee Receivables** (confirmed via the shared GL reference), not 623 (that code now belongs to Performance Fee Receivables, renamed 2026 — do not confuse the two).

## Cross-module signal scan (added Jul 2026 — mandatory every close)

While parsing the export, scan every line's **Category + Description/Comment** for signals that
belong to OTHER modules, and emit a signals list for the orchestrator (detection here, routing there):

| Signal | Trigger | Routes to |
|---|---|---|
| CAPEX | Category in (I.T. Equipment, Computer, Furniture, Office Equipment, Leasehold) AND amount ≥ 5,000; or description mentions laptop/notebook/equipment purchase | Fixed-asset register addition + catch-up depreciation |
| DEPOSIT/BALANCE | Description contains "deposit", "balance of" — link the deposit line to its balance payment and capitalise the TOTAL | Fixed assets |
| PREPAYMENT | Description contains "annual", a coverage period ("2026-2027", "Mar 2026-2027"), "12 month" AND amount ≥ 5,000 (per-item floor, confirmed Jul 2026) | Prepayment (620) + amortisation; below floor → expense immediately |
| PEP | PE Program tag or "for PE Program" in description | PEP receivable |

Real case: Jun 2026 scan surfaced 3 unrecorded fixed assets (X1 G14 20,590 incl. 500 deposit;
ThinkPad x13 16,990; Mac Mini 13,599) and 4 annual subscriptions. Category GL 740 maps to the
Computer Equipment FIXED ASSET code, so such lines capitalise via coding — but the register update
and catch-up depreciation still need routing. Note: the Expensify MCP returns no receipt-image URLs;
coverage periods come from descriptions, else ask the user.

## Rolling-export scope & dedup (added Jul 2026)

Exports now cover everything since the last Approved/Reimbursed report (e.g. Apr 1 – latest), not
just current-month activity. Consequences:
1. **Dedup before recognising**: check each line against prior months' close workpapers (and/or
   Xero) — recognise only items NOT previously recognised. Real case: Allianz 30,220 was recognised
   in the April close; re-recognising it in June would have double-counted.
2. **Prior-month changes** (recoding, amount edits, retractions) made in the current month are
   booked as CURRENT-month adjustments — never reopen closed months.
3. Catch-up depreciation/amortisation for late-surfaced items books in the current month, with the
   asset/prepayment recorded at its true purchase date.

## AMEX Clearing completeness tie-out (added Jul 2026 — a real omission was caught in review)

The credit to AMEX Clearing each month MUST equal the sum of that month's statements exactly —
the liability to AMEX is complete regardless of Expensify submission status. Three legs:
DR expenses/PEP (submitted + past approval gate) + DR AMEX Unsubmitted Suspense (everything else on
the statements) / CR AMEX Clearing [full statement total]. June 2026: 14,597.48 recognised +
100,734.01 suspense = 115,331.49 = five statements to the cent. Suspense releases to P&L/PEP as
items later pass the gate (the standard Part B mechanics). HARD CHECK before finishing: if the
Clearing credit ≠ statement total, the journal is incomplete.

## Convention transition — per-card model DEPRECATED (Arnold, 9-Jul-26)

The live books historically used a DIFFERENT model: one Xero bank account per AMEX card
("AMEX - Alex (x3001)" etc.), approved Expensify expenses auto-posting as Spend Money credits on
the card account (refs EXPENSIFY-R00...), and each statement payment booked as a bank transfer
DBS → card account. No clearing account, no suspense — the card account balance absorbed the
timing gap (e.g. Alex's account at 102,363.39 DEBIT = payments running ahead of approvals).

That convention is deprecated as incorrect. The CLEARING + UNSUBMITTED SUSPENSE model in this
skill is the go-forward treatment, effective from the June 2026 close. Do NOT mix models.

**Migration steps (one-time, on live books — see also poster skill migration checklist §F):**
1. For each card account, verify its balance composition: it should equal cumulative statement
   payments − cumulative approved recognitions = charges paid but not yet approved (suspense-like).
2. One-time reclass: DR AMEX Unsubmitted Suspense / CR each card account, zeroing them (reverse
   signs if any card is in credit). This seeds the suspense OPENING BALANCE — resolving the
   "opening unknown" flag in the subledger schedule.
3. **Reconfigure the Expensify→Xero integration**: it must STOP posting Spend Money to the card
   accounts. Otherwise the integration credits card accounts while the skill credits Clearing —
   double-counting every expense. Either point the integration's export account at AMEX Clearing
   with a reconciliation step, or disable auto-posting and let the skill journals be the sole path
   (preferred — one writer, consistent with draft-first).
4. Archive the per-card accounts once zeroed.
5. Statement payments thereafter: DR AMEX Clearing / CR DBS (the five per-card transfers become
   one clearing settlement, reconciled to the five statements).
