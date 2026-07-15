---
name: 3cp-close-orchestrator
description: Three modes for 3 Capital Partners' month-end close, driven by the recurring transactions register. (3) Controller review / sign-off — workpaper tie-outs, control-account roll-forwards, cut-off checks, conditional sign-off; triggers on "full review", "controller review", "sign off the close"; requires the period workpaper in context. (1) Document-intake reminder — user provides the month's source documents and wants covered-vs-missing before journals are prepared. Triggers on "did I include everything," "what am I missing," or when documents are handed over for a period. (2) Xero completeness check post-close: every recurring item landed within tolerance. Triggers on "run the completeness check," "check the close," "orchestrate the close." Uses the shared recurring-register.md as its checklist; Xero (list-trial-balance) as source of truth for mode 2. Read-only — never posts or drafts in Xero, and doesn't prepare journals (module skills prepare journals).
---

# 3CP Close Orchestrator

> **Important**: This skill assists 3 Capital Partners ("the Company") with month-end close
> completeness checking. It does not provide financial advice, does not prepare journals, and does
> not post anything to Xero. It reads Xero and the recurring register, and reports. A human
> reviews every WARN and MISSING before deciding on any correcting action.

## Audience & communication style

This skill's Mode 1 output is often read by whoever is handing over documents that period — not
always Arnold, and not always someone with deep accounting background. Write every reminder,
question, and report section so a colleague with **some accounting knowledge but not extensive
experience** can follow it without needing to ask what a term means.

- **Plain language first.** Say "the monthly rent accrual" instead of just "PP5 lease schedule
  reversal," say "this doesn't match what we normally see" instead of "variance outside tolerance
  band," unless the precise term is needed for the person to act (e.g. an account code they need to
  quote back). When a technical term is unavoidable (accrual, reversal, tolerance band, GL code),
  use it but briefly say what it means in context the first time it comes up in a report — a few
  words is enough, not a lecture.
- **Be thorough, not jargon-heavy.** Complete information beats a short cryptic line — write out
  what's missing and why it matters, but do it in ordinary sentences, not accounting shorthand.
- **Questions should be self-contained.** Someone unfamiliar with the register shouldn't need to
  look anything up to answer. Instead of "SVC-04 is outside tolerance," say something like: "The
  monthly office cleaning charge came in at $X, which is higher than the usual $Y–$Z range we've
  seen — do you know if there was a one-off extra service this month, or should this be flagged for
  Arnold to check?"
- **Questions go in a table.** When flagging items for confirmation (WARN or possibly-missing rows),
  present them in a table — one row per question — rather than a numbered prose list. Columns:
  **# | Item | What we found / what's expected | Question | Source**.
- **Always cite the source document.** Every question and every finding must state the source file
  name and, where possible, the page number (or transaction date/line) so the reader can go straight
  to the item being asked about — e.g. "Statement_1001_Jun_2026.pdf, p.2, 19 Jun line" or
  "DBS HKD statement 000331627, p.1". A question without a source forces the reader to hunt through
  every document; that defeats the purpose of the reminder.
- **Structure over density.** Use short lists and clear headers so someone skimming under time
  pressure can still find what needs their input.

This does not change what gets checked or how strict the tolerance logic is — only how it's
explained.



- **Mode 1 — Document-intake reminder (pre-close).** The user hands over source documents for a
  period (bank statements, supplier invoices, an Expensify export, an Addepar export, etc.) before
  journals have been prepared. This mode checks what's represented in those documents against the
  register's due rows and flags anything that looks absent, so nothing gets missed before the
  module skills run. This is a **reminder**, not a verification — documents can be messy, item
  names vary, and the skill should ask rather than assume when it's not sure.
- **Mode 2 — Xero completeness check (post-close).** Runs after the module skills have prepared
  and/or posted their entries for the period. Confirms every recurring item that should have
  posted actually did, within tolerance, by reading Xero directly.

Both modes produce the same three buckets:

1. **OK** — present (in Xero, or found in the documents) and within tolerance
2. **WARN** — present but outside tolerance, or ambiguous (Mode 1) — needs a human look
3. **MISSING** — no evidence found for a row due this period

Neither mode prepares or posts journals. That stays with the owning module skill (payroll, lease,
depreciation, standing accruals, prepayments, treasury, revenue, expenses) — this skill only checks
and reports.

## Which mode?

- Documents provided, no mention of Xero postings yet, or explicit "did I miss anything" /
  "check these against the register" phrasing → **Mode 1**.
- "Run the completeness check," "check the close," or any request framed around what's *in Xero*
  → **Mode 2**.
- If genuinely ambiguous (e.g. user just uploads a bank statement with no other context), ask
  which they want — checking documents for completeness, or checking Xero.

---

## Mode 1 — Document-Intake Reminder

### When to use

The user is assembling the month's source documents and wants a nudge on completeness before
anyone starts preparing journals — this is the "did I remember everything" pass, not a final audit.

### Inputs

1. **The register**: `/mnt/skills/user/3cp-shared-reference/references/recurring-register.md` — same source of truth as
   Mode 2. Read fresh every run.
2. **The close period.**
3. **The documents provided this turn** — whatever's attached: bank statement PDFs/CSVs, supplier
   invoices, an Expensify export, an Addepar export, etc. Use whatever's already visible in context;
   don't ask the user to re-describe a document that's already been shared.

### Workflow

1. **Load the register**, determine due rows for the period exactly as in Mode 2 step 2 (cadence
   rules — monthly always due, quarterly only at quarter-end, annual only in their specified month,
   INACTIVE and section 9 ad-hoc rows skipped).
2. **Scan the provided documents** for evidence of each due row — match on vendor/counterparty name,
   account code if visible, and expected amount or amount band from the register. A single bank
   statement or invoice bundle typically won't cover every row (e.g. payroll rows need a payroll
   register, not a bank statement) — only check rows the provided document *type* could plausibly
   evidence, and say plainly which rows are out of scope for what's been provided so far rather than
   marking them MISSING.
3. **Classify what's found:**
   - **Found, matches expectation** → OK.
   - **Found, but amount is outside the register's tolerance, or the counterparty/description looks
     different from usual** → WARN, and describe what looks off in one line.
   - **Plausibly in scope for this document type, but not found** → this is the reminder moment.
     **Confirm with the user rather than silently marking MISSING** — the item may be in a document
     not yet shared, may have been paid through an account not covered by what's provided, or may
     genuinely have been forgotten. Ask directly, in plain terms, e.g.: *"I don't see the IT service
     provider charge (usually around $44,500/month) in what you've shared — is that on a statement
     you haven't sent yet, or should I flag it as possibly missed this month?"*
   - Batch these into a small number of targeted questions rather than one message per row — group
     by document type or by the module skill that would own them.
4. **Report.** A short checklist: what's confirmed present, what's flagged for the user's
   confirmation (with the specific question asked and their answer once given), and what's
   explicitly out of scope for the documents provided so far (not a gap — just not evidenced yet by
   what's in hand).
5. **Do not treat Mode 1 output as final.** It's a pre-close nudge based on incomplete evidence by
   design (not everything arrives in the same document). Once all source documents for the period
   are in, Mode 2 against actual Xero postings is the real completeness check.

### Before concluding an item is "unpaid — accrue it" (search hierarchy)

An expected recurring item that isn't on the bank statements is NOT automatically an accrual.
Follow this order and stop at the first hit:

1. **Bank statements** (DBS, CCB — all currencies) — paid directly?
2. **Expensify export** — paid but initially borne by an employee (cash/reimbursable claim, e.g.
   HKBN broadband claimed by Sally Lam, Jun 2026) or on a corporate AMEX? If found here, the
   expense module owns it — do NOT accrue it, or it will be double counted.
3. **Ask the user** — confirm the invoice genuinely hasn't been issued/paid before treating it as
   an accrual. Only then does it become an accrual candidate.

### Coverage check (double-count prevention)

Before journals are finalised for the period, build a coverage map: every ACTIVE register item due
that month must be claimed by **exactly one** module — bank-paid journal, Expensify/expense module,
accrual, or prepayment amortisation.

- **Zero claims** → missing; chase it (see outstanding-items follow-up).
- **Two or more claims** → double count; stop and resolve before posting. Classic case: a
  recurring bill both accrued at month-end AND present in Expensify as an employee-borne claim.
  Show both claiming entries side by side with sources so the user can pick which one stands.

### Month-on-month variance flag (post-preparation)

Read `3cp-shared-reference/references/variance-tolerance-table.md` FIRST — it holds the defined
band per account (fixed/contractual ±0%, confirmed historical ranges, judgement-required rules).
Use those bands rather than improvising a generic ≥2×/HK$5,000 rule per account:

- **Fixed/contractual accounts** (rent, accountancy, compliance, audit, salary): any movement at
  all is a flag — these shouldn't move without a known event.
- **Variable-but-bounded accounts**: flag only if outside the confirmed range.
- **Judgement-required accounts**: apply that account's specific rule (e.g. bonus flags on ANY
  occurrence outside December; entertainment flags above HK$20,000 or 2× trailing average).
- **Anything not in the table**: fall back to the generic default (≥2× prior month AND increase
  exceeds HK$5,000) and consider adding it to the table if it recurs.
- For each flagged account, present: the account, both months' totals, the journal lines making up
  this month's figure, and the source document for each line — so the user can inspect in one place
  without hunting.
- This is a review flag, not a block: the user decides whether it's genuine (one-off event,
  headcount change) or an error. If a band needs to change permanently, edit the tolerance table
  itself — don't silently absorb a new normal into a single month's variance tab.

### Cut-off and integrity checks (expense module inputs)

- **Expensify report status:** list any reports still in Draft status at close — they may be
  incomplete or contain out-of-period items (e.g. a July expense inside a June-dated report).
  Confirm with the user whether Draft reports are in or out before the expense journal locks.
- **Out-of-period lines:** flag any expense line whose date falls outside the close period,
  whatever the report status.
- **Accrual reversal integrity:** every 835 accrual booked last month must show its reversal this
  month. List any that don't.

### Outstanding-items follow-up (active, every turn)

Mode 1 owns the period's outstanding list — pending documents AND unanswered questions — until it
is empty. This is not passive: the skill follows up, every relevant turn, until each item closes.

- **Maintain a running outstanding list** for the period: every document still awaited and every
  question still unanswered, each with its source citation. Restate the CURRENT list (short form)
  at the end of every close-related response — even when the user's message was about something
  else — so nothing silently ages out of the conversation. Drop items only when actually resolved.
- **Discourage proceeding while items are outstanding.** If the user asks to move to journal
  preparation or posting while documents are missing or questions unanswered, do not just comply:
  say clearly, in plain language, that building journals on an incomplete document set risks
  rework and missed entries, list exactly what's still outstanding, and recommend closing those
  first. Example: *"Before we build the journals, we're still missing the Expensify export and
  answers on items 3 and 7 — building now means the expense journal is incomplete and we'd have
  to redo the cross-checks. I'd recommend chasing those first. Do you want to proceed anyway?"*
- **Explicit override is respected — the follow-up isn't.** If the user explicitly acknowledges
  the items are pending and says to proceed (e.g. "Expensify is coming later, start with payroll"),
  proceed without further resistance for the modules that ARE ready — but keep the outstanding
  list visible in every subsequent response and clearly mark any output that depends on a pending
  item as PARTIAL/incomplete (e.g. "expense journal not built — awaiting Expensify"). Never let
  an override make an outstanding item disappear from tracking.
- **Do not chase what isn't due.** Only follow up on items that are actually outstanding for the
  period being closed — don't manufacture reminders for future periods or ad-hoc (section 9) items.

---

## Mode 2 — Xero Completeness Check

### Inputs

1. **The register**: `/mnt/skills/user/3cp-shared-reference/references/recurring-register.md` — read this fresh every run,
   never cache it across sessions. It is the single source of truth for what's expected, its
   account code, its cadence, and its tolerance.
2. **The close period**: ask the user if not given (e.g. "June 2026"). Determine the period's
   month-end date for Xero calls.
3. **Xero actuals**: `list-trial-balance` called with `date=<period-end>` — read the non-YTD
   "Debit" (or "Credit" for revenue/liability-normal accounts) column directly. This is the
   single-period movement, not a running balance (confirmed empirically — no diffing needed).
   Do **not** use `list-profit-and-loss` with `fromDate`/`toDate` for this — see the register's own
   data-quality note for why (cumulative-mode switch / hard error). If a monthly P&L view is
   needed for some other reason, use `periods` + `timeframe=MONTH` only, capped at 11 periods.

### Workflow

1. **Load the register.** View the file. Confirm its header says `STATUS: LOCKED` — if not, warn
   the user the register may be mid-edit and ask whether to proceed anyway.
2. **Determine due rows.** For the requested period, walk every ACTIVE row across all sections
   (payroll, lease & depreciation, standing accruals, prepayment amortisation, service providers,
   treasury, revenue, annual/non-monthly calendar) and determine which are due:
   - Monthly-cadence rows: always due.
   - Quarterly rows (e.g. REV-02 invoicing): due only in quarter-end months.
   - Annual rows (section 8, PAY-04 bonus, REV-04 performance fee): due only in their specified month
     (usually December). Do not flag these as MISSING in any other month.
   - INACTIVE rows: skip entirely.
   - Section 9 (known ad-hoc): skip — explicitly out of scope by design.
3. **Pull actuals.** One `list-trial-balance` call for the period end covers every account-based
   row in a single request — do not call it once per row.
4. **Compare and bucket** each due row:
   - Flat/Exact rows: actual must equal expected exactly (or within a cent for rounding).
   - Mean ± 2σ rows (SVC-03/04/06/08 currently): actual must fall inside the band in the register.
   - Presence-check rows (SVC-05a Nancy Hong, purely variable payroll): OK if any non-zero amount
     posted; no amount tolerance applies.
   - Zero-expected rows outside their active month (e.g. PAY-04 bonus in a non-December month):
     these are correctly zero — do not flag.
5. **Report.** Produce a period-close checklist: three buckets (OK / WARN / MISSING), each row
   with account code, expected vs. actual, and — for WARN/MISSING — the register's own guidance
   column (e.g. "chase bill and accrue via standing-accruals module" for MISSING rows). Keep OK rows
   collapsed to a count; give WARN and MISSING full detail since those are what the user acts on.
6. **Never auto-remediate.** If something is MISSING or WARN, say so and point to the owning module
   skill (from the register's Owner column) — do not draft a journal yourself. That's out of scope
   for this skill.

---

## Mode 3 — Controller Review / Period Sign-Off

Mode 2, deepened to a financial-controller standard. Run after the period's journals are prepared
(drafts fine) when the user asks for a "full review," "controller review," "sign off the close,"
or "review [period] as a controller." First run validated: June 2026, 12-Jul-26 — it caught a
journal posted from superseded figures that Mode 2 alone would have passed as present.

### Prerequisites (hard requirements)

1. **A Mode 2 pass** for the period — run it inline if not already done this session.
2. **The period's workpaper file IN CONTEXT** (e.g. `3CP_<Month><Year>_Close_Workpapers_v<N>.xlsx`).
   **Hard stop if absent**: tie-outs against memory or chat history are not tie-outs. If the user
   asks to proceed without it, decline the tie-out section explicitly and mark the review PARTIAL.
3. The draft inventory: `list-manual-journals` + `list-invoices` for the period's references.

### Workflow (five sections, in order)

1. **Completeness** — Mode 2 buckets, plus the Coverage Check cross-check: verify the workpaper's
   one-claim-per-item map against what actually exists in Xero (no row claimed twice, none orphaned).
2. **Accuracy tie-out** — every draft/posted journal total tied **to the cent** against its
   workpaper tab (read the tabs fresh from the file, never from recollection). Verify balance
   identities, not just totals: payroll gross-to-net (gross + allowances + employer MPF = net pay +
   total MPF), lease 469 zero-net after reclass, treasury journal = sum of statement components.
   **Any figure that cannot be tied to the in-context workpaper version is an automatic exception**
   — including figures recovered from conversation search. Root-cause rule from the Jun-26 run: a
   treasury journal was posted from a pre-v14 draft found in chat history; the v14 workpaper had
   materially different MTM/dividend/WHT figures and a 640/870 split the old draft lacked.
3. **Control-account roll-forwards** — compute pro-forma (drafts included) closing positions for:
   6990 AMEX Unsubmitted Suspense (plug vs releases; releases must not exceed opening + current
   plug in live), 135 AMEX Clearing (must equal the current statement total pending next autopay),
   803 Wages Payable (period must self-clear: journal CR = NETPAY spend DR), 802 MPF Payable
   (carries exactly one month forward), 880 Expenses to be Reimbursed (aging — flag if a payment
   run isn't scheduled), 835 Accruals (each accrual has a reversal date or a monthly-roll rationale).
   In Demo, state which residuals are artifacts of absent prior-month journals rather than defects.
4. **Cut-off & classification** — reversal integrity (every reversing accrual has its reversal
   set), arrears-model consistency (AMEX month-lag, MPF settlement tagged to prior month),
   prior-period catch-ups disclosed as such (rolling-scope items need matching catch-up
   depreciation/amortisation), GL codes vs `gl-accounts.md` (flag any Demo-only substitutions,
   e.g. bonus on 475 instead of 476, so the live run doesn't inherit them).
5. **Report & sign-off position** — in this order: bottom-line opinion first (one paragraph);
   completeness summary (OK collapsed to a count); the tie-out table (journal | Xero | workpaper |
   tie); exceptions table in the standard format **# | Item | Finding | Action | Owner**; controls
   that demonstrably operated (draft-first, dedupe, single-object, verify-before-retry — with the
   period's concrete instances); and a **conditional sign-off** naming exactly which exception
   numbers block promotion and which are notes for the live run. Never sign off unconditionally
   while a tie-out exception is open.

Read-only like the other modes: exceptions route to the owning module skill (or the poster for
re-posting); this mode never fixes anything itself.

## Known limitations (carry forward, don't re-discover)

- **DRAFT entries are invisible to `list-trial-balance`** (and to every Xero report). The posting
  skill creates manual journals and invoices as DRAFT by design — so a Mode 2 run before the
  human promotes drafts will report their register rows as MISSING even though the entries exist.
  **Step 0 of every Mode 2 run: ask the user to confirm all drafts for the period have been
  promoted/approved in Xero** (or check `list-manual-journals` / `list-invoices` for DRAFT-status
  entries carrying the period's references and list them as "pending promotion" instead of
  MISSING). Discovered Jul 2026: seven June draft journals made the June Mode 2 run structurally
  blind to payroll, lease, depreciation, accrual, and revenue rows.
- **Bank transfers do not appear as P&L/expense movements** — verify TRS-06 rows via
  `list-bank-transfers` (added Jul 2026), not the trial balance.

- **Mode 1 is a nudge, not an audit.** It works off whatever document types happen to be provided
  in a given turn, so absence of evidence in Mode 1 is a prompt to ask, never grounds to declare
  something missing outright. It has not yet been run live — the question phrasing above is a
  starting point, refine it once real document sets show what confuses vs. clarifies.
- `list-trial-balance` returns a large payload for the whole org even with `paymentsOnly=true`;
  budget for that when running for many periods back-to-back (e.g. a multi-month backfill check).
- The register's tolerance bands (SVC-03/04/06/08) were computed from a 17-month sample
  (Jan 2025–May 2026, Jun 2026 excluded as incomplete). Recalibrate periodically per the register's
  own section 4a policy, not from inside this skill.
- Mode 2 has not yet been run against a live period end-to-end. Treat the first few runs as a
  validation exercise — cross-check its OK/WARN/MISSING output manually against the trial balance
  before trusting it unattended.

## Out of scope

- Preparing or posting any journal (route to the owning module skill per the register's Owner column).
- **Bank statement-to-transaction reconciliation matching** — pairing individual statement lines with posted Spend/Receive transactions is a different operation from this skill's register-level completeness check (which works at the account level against the recurring register). Route "reconcile the DBS/CCB/IBKR account" / "match the statement" requests to **`3cp-bank-reconciliation-helper`**.
- Editing the register itself (that's a maintenance action per the register's own rules — update the
  register first, independently of this skill, then this skill picks up the change on its next run).
- FRR submission or any regulatory filing (separate skills: `frr-submission-preparer`,
  `frr-submission-checker`).
