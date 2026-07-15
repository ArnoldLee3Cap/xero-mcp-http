---
name: 3cp-revenue-recognition
description: Prepare 3 Capital Partners' month-end revenue accrual journals as DRAFT entries and maintain aged receivables. Two fee streams. Management fee — calculated in Addepar on month-end AUM, recognised MONTHLY as accrued income via a manual journal (DR 622 Management fee receivables / CR 200 Revenue), billed QUARTERLY via a real Xero sales invoice with its line coded to 622 (reclassifies accrued to trade receivable DR 610 / CR 622, no revenue re-recognition). The skill books the monthly accrual from the Addepar export + receivable list, runs the quarter-end reconciliation (sum of monthly accruals vs the quarterly invoice per client), and maintains aged receivables for the FRR. Performance fee — not accrued (prudence); recognised only at year-end December on crystallisation. Use at month-end with the Addepar export and receivable list. USD; preparation only (a separate skill posts drafts; the invoice is raised in Xero manually). Do NOT use for expenses, treasury, lease, or depreciation.
---

# 3CP Revenue Recognition (preparation)

> **Important**: Preparation only; not financial advice. Every entry is a DRAFT for a qualified accountant to review and approve in Xero before posting. This skill does not calculate fees (Addepar does) and does not post to Xero (a separate posting skill does). The quarterly client invoice is raised in Xero by the accountant (not by this skill).

> **Precondition — orchestrator gate**: Before preparing revenue journals for a period, check
> whether `3cp-close-orchestrator` (Mode 1) has been run for that period this session. If it
> hasn't, say so and offer to run it first. If the user explicitly says to skip it and proceed
> anyway, proceed — this is a workflow recommendation, not a hard block.

Prepare the month-end fee-income journals and maintain aged receivables for 3 Capital Partners ("the Company"). The Company has **two** fee-income streams, treated very differently.

## Recognition model (accrual basis — Option 2, CONFIRMED)

The Company recognises management fee on an **accrual basis**: revenue is earned monthly and billed quarterly. Two mechanisms, kept strictly separate:

1. **Monthly accrual (this skill).** Each month-end, recognise that month's earned fee with a manual journal, per client:
   - **DR 622 Management fee receivables** (accrued / unbilled)
   - **CR 200 Revenue - Management Fees**
   - USD; amount from the Addepar `Bill Fee Amount` (net). One journal, one line-pair per client.

2. **Quarterly invoice (raised in Xero by the accountant, NOT this skill).** At quarter-end the real client invoice is issued in Xero (letterhead .docx attached) with its line(s) **coded to 622** — not 200. Coding to 622 makes Xero auto-post **DR 610 Accounts Receivable / CR 622**, which **reclassifies** the accrued receivable into a billed trade receivable **without re-recognising revenue** (revenue was already booked monthly). Collection (~1 month later) auto-matches to the invoice at bank rec.

> **Why 622, not 200:** if the invoice line were coded to 200 (as it was historically, on a cash-ish basis), revenue would be credited twice — once by the monthly accruals, once by the invoice. Coding the line to **622** cancels the accrued receivable instead of re-recognising income. **This is the one operational change the accountant must adopt:** quarterly invoice line → 622.

There is **no manual reclass journal** — the invoice itself performs DR 610 / CR 622. This skill's quarter-end job is the **accrual for that month + the reconciliation** (below) + AR aging.

### Quarter-end reconciliation (CONFIRMED — required)
In the quarter-end month, per client, check: **Σ (the quarter's three monthly accruals) = the quarterly invoice total.** They should tie exactly for Addepar clients (same Addepar source feeds both). Surface any gap in the Review section **before** the invoice is finalised; do not silently absorb it. Prior-month restatement is not expected, so a non-zero residual is a flag, not a routine true-up.

## Two income streams

### 1. Management fee — accrued monthly, billed quarterly
- **Calculated externally in Addepar** on each client's **month-end AUM**. The skill does **not** compute the fee — it reads the Addepar export (`Bill Fee Amount`, net, USD).
- **Recognised monthly** as earned: `DR 622 / CR 200`, per client, in USD.
- **Billed quarterly:** the real Xero invoice (line → 622) reclassifies accrued (622) to trade (610); **no revenue re-recognition, no manual reclass journal.**
- The skill books the monthly accrual, runs the **quarter-end reconciliation**, and **maintains the aged receivables summary**.
- **Amy Sadick is the one non-Addepar client** — estimate monthly (prior-quarter actual ÷ 3), adjust at quarter-end to her standalone-Excel actual. See `references/non-addepar-estimation.md`.
- **EXCLUSION — SP and 3CP-managed vehicles (no 622 accrual):** management fees from SP investment vehicles and any entity with **"TriBridge"** or **"3 Capital Partners"** in its name are 3CP's own investment vehicles, not external clients. They are recognised on **invoice basis only** — do NOT book a monthly `DR 622 / CR 200` accrual for them, even if they appear in the Addepar export. Exclude them from the monthly accrual journal, the quarter-end reconciliation, and the 622 balance. (Standing open policy item: these may move to accrual basis in future — if that decision is made, this exclusion is removed and the change applies going forward only.)

### 2. Performance fee — year-end only, on crystallisation
- On **prudence grounds the Company does NOT accrue** performance fees during the year.
- Recognised **only at year-end (December close)**, once the fee actually **crystallises**.
- **No monthly entry.** In the December close, book crystallised performance fee `DR 623 Performance Fee Receivables / CR 220 Revenue - Performance Fee`. Outside December, performance fee is out of scope — do not accrue it.

## Usage

```
/3cp-revenue-recognition <period> [--mgmt-fee --ar-aging --perf-fee]
```

- `period` — a single **month** (e.g. `2026-01`); period end is the last calendar day.
- Default runs the management-fee accrual + AR-aging maintenance. `--perf-fee` only applies in the December close.

### Monthly cadence — ONE workpaper per month
This skill runs **every month** and produces **one workpaper per month**:
- **Ordinary months (Jan, Feb, Apr, May, Jul, Aug, Oct, Nov):** book that month's **accrual only** (`DR 622 / CR 200`) from the Addepar figure. No invoice, no reclass, no reconciliation.
- **Quarter-end month (Mar / Jun / Sep / Dec):** book that month's accrual **plus** run the **quarter-end reconciliation** (Σ monthly accruals vs quarterly invoice, per client) and the **AR aging**. The invoice reclass (DR 610 / CR 622) is done in Xero by the invoice, not by a skill journal.
- **December** additionally carries the **performance-fee** crystallisation entry.

So Q1 2026 = three workpapers: Jan (accrual), Feb (accrual), Mar (accrual + reconciliation + aging).

### Modules

| Flag | Module | Produces |
|---|---|---|
| `--mgmt-fee` | Management fee monthly accrual | DRAFT accrual journal `DR 622 / CR 200` from that month's Addepar export (+ Amy Sadick estimate); in the quarter-end month, also the reconciliation and (for Amy) the true-up adjustment |
| `--ar-aging` | Aged receivables maintenance | Updated aged receivables summary (accrued 622 + billed 610), reconciled, for FRR — run at quarter-end |
| `--perf-fee` | Performance fee (December only) | DRAFT crystallised performance-fee entry (CR 220); no-op in other months |

Read the relevant reference before building: `references/management-fee.md`, `references/client-mapping.md` (LOCKED tracker↔Addepar↔Xero-contact map), `references/non-addepar-estimation.md` (Amy Sadick), `/mnt/skills/user/3cp-shared-reference/references/gl-accounts.md` (authoritative Xero account codes — shared, not a local copy), `references/ar-aging.md`, `references/performance-fee.md`.

## Inputs (provided monthly)

- **Addepar export** — per-client management fee for the month (Addepar billing view, all USD). Header on row 5; aggregate `Bill Fee Amount (USD)` (net) by `Billable Portfolio`; **exclude the "Total" row**; resolve blank-portfolio rows. See `references/management-fee.md`.
- **Revenue receivable list** — the Company's running list of fee receivables (accrued/unbilled and billed), by client, with amounts and dates. Source for AR aging and for reconciling the accrual.
- **(Quarter-end) the quarterly invoice total per client** — from the invoice(s) raised in Xero / the `3cp-invoice-generator` output — for the reconciliation.
- **(Amy Sadick)** her standalone Excel actual at quarter-end.
- **(December)** crystallised performance-fee schedule.

## Currency

Management fees are **accrued and invoiced in USD** (the Addepar export is USD throughout). Book the monthly accrual in **USD**; Xero translates for HKD reporting on posting — never convert in the skill, never fetch a rate. The accrual journal is single-currency USD (`…-MGMT-USD`).

Clients **occasionally pay in HKD** instead of USD. That settles a USD receivable in HKD, creating a **realised FX difference — which is Xero's** (computed at settlement from the receivable's carrying rate), not recomputed here. Keep the receivable in USD and let the HKD collection and its FX flow through Xero (as seen on INV-0607, a small HKD currency loss).

## Posting boundary & handoff (preparation only)

Emits the common journal contract consumed by `3cp-xero-journal-poster`:
- **Status DRAFT**; never auto-approve.
- **Unique reference per journal:**
  - `3CP-REV-<period>-MGMT-USD` — monthly Addepar accrual (lines per client).
  - `3CP-REV-<period>-MGMT-AMYS-USD` — Amy Sadick monthly estimate (separate stream).
  - `3CP-REV-<period>-TRUEUP-AMYS-USD` — Amy Sadick quarter-end adjustment to actual.
  - `3CP-REV-<period>-PERF-USD` — December performance-fee crystallisation.
  - There is **no** `-BILL-` reclass journal: the Xero invoice (line → 622) performs DR 610 / CR 622.
  - Idempotent on the reference.
- **Structured payload:** reference, period/date, narration, currency, reversal flag, lines `{account, debit, credit}`. Amounts in the journal's currency (USD).
- **Reconcile before post:** the accrual must tie to the Addepar export and the revenue receivable list; at quarter-end Σ accruals must tie to the invoice per client; AR aging must reconcile to the receivable GL (622 + 610); anything unreconciled is held back.
- A separate posting skill owns the Xero API/MCP connection. The quarterly invoice can now be
  prepared as a **DRAFT ACCREC invoice via the poster's `create-invoice`** (line coded to 622,
  unique reference) for the accountant to review, approve, and send in Xero — or raised manually
  as before; either way approval/sending stays human. Client receipts settle at bank reconciliation
  (matching the statement line to the invoice), not via journals — receipts to accrued (unbilled)
  balances are RECEIVE bank transactions crediting 622.

## Shared conventions

1. **Reconcile to source** — accrual ties to Addepar (fee per client) and to the revenue receivable list; at quarter-end Σ accruals tie to the invoice per client; AR aging total ties to the receivable GL balance (622 accrued + 610 billed).
2. **Account mapping (CONFIRMED codes):** 622 Management fee receivables (accrued/unbilled), 610 Accounts Receivable (billed trade — Xero system AR), 200 Revenue - Management Fees, 220 Revenue - Performance Fee, 623 Performance Fee Receivables (confirmed via shared GL reference — no longer TBD).
3. **Balance discipline** — every draft balances within its currency; expose a balance check.
4. **Draft + sign-off**; never imply posted/final.
5. **Flag, don't fix** — AUM/fee mismatches, reconciliation residuals, new or departed clients, FX questions, aging anomalies → a Review section.
6. **Output** — Calibri, navy bands, light-blue subtotals, yellow for attention; build with the `xlsx` skill; recalc; zero formula errors; share via `present_files`.

## Workflow

1. Resolve period and modules; read the Addepar export and revenue receivable list (Xero export for reconciliation).
2. **Management fee (every month):** for each client, take the month's fee from Addepar (`Bill Fee Amount`, net); accrue `DR 622 Management fee receivables / CR 200 Revenue - Management Fees` in USD (one journal, lines per Billable Portfolio). Amy Sadick: separate estimate journal (prior-quarter ÷ 3).
3. **Quarter-end month only:** run the **reconciliation** — per client, Σ (Jan+Feb+Mar accruals) vs the quarterly invoice total; flag any residual. For **Amy Sadick**, book the **true-up adjustment** (`DR/CR 622 / 200`) to bring her cumulative accrual to her standalone-Excel actual. Do **not** book a reclass journal — the Xero invoice (line → 622) reclassifies 622 → 610.
4. **AR aging:** update the aged receivables summary (accrued 622 + billed 610), age by invoice/accrual date into buckets, reconcile to the receivable GL and the revenue receivable list. See `references/ar-aging.md`.
5. **December only:** book crystallised performance fee (CR 220).
6. Build the workpaper; recalc; verify zero errors; emit the contract payload; present and summarise (entries, reconciliation, aging, flags). Note all entries are DRAFT.

## Standing notes

- **No fee calculation, no FX rate fetch, preparation only.**
- **Quarterly invoice line MUST be coded to 622** (not 200) — the one operational change under accrual basis; without it, revenue double-counts. **Confirmed via live Xero check (3 Jul 2026): Q1 2026 invoices (INV-0603, INV-0604, INV-0609) were coded to 200 on a single quarter-end invoice with three monthly line items, and no monthly manual journal was booked.** That was the pre-change process — flag this transition explicitly the first time this skill runs for a live period.
- **Performance fee never accrues outside December** — prudence basis.
- **Aged receivables feed the FRR** (aged fee receivables attract haircuts / concentration tests) — keep the aging accurate and reconcilable; coordinate with the FRR skills downstream.
- **Boundary** — expenses, treasury, lease, depreciation each have their own skill; this skill is fee income and fee receivables only.

## Investment-vehicle accrual (policy change, Jul 2026 — supersedes invoice-basis carve-out)

SP/TriBridge/3 Capital Partners vehicles are now ACCRUED MONTHLY using the last invoice as the
estimate, trued-up when the next invoice is raised:
- Quarterly-invoiced (SP1/SP2/SP3; **GP I Ltd — corrected 9-Jul-26, was wrongly treated as annual**):
  monthly accrual = last quarterly invoice ÷ 3 (basis: SP1 58,904.58; SP2 10,231.15; SP3 5,861.82;
  GP I Ltd 6,546.74 from Q4-2025 invoice 19,640.22 ÷ 3 — per month, USD).
- Annually-invoiced (PP GP I Ltd; Private Program I LP): monthly accrual = last annual invoice ÷ 12
  (basis: 29,845.00; 14,097.52 per month, USD).
- **Do not assume invoicing frequency — confirm from the actual invoice period shown** (Jul 2026
  lesson: GP I Ltd's invoice period read "10/01/2025–12/31/2025", i.e. Q4 only, which means
  quarterly; the skill had wrongly defaulted it to annual alongside PP GP I Ltd because the names
  are similar — "GP I Ltd" ≠ "PP GP I Ltd").
- Entry: DR 622 / CR 200, USD, one line per vehicle, ref 3CP-REV-<period>-VEHICLES.
- True-up on invoicing: recognise invoice vs cumulative accruals difference in the invoice month.
  Performance fees are NEVER accrued (prudence) — recognise 100% in the invoice/crystallisation
  month even when a management-fee true-up is booked in the same receipt (Jul 2026 worked example:
  GP I Ltd Q4-2025 receipt = 16,978.88 receivable cleared + 2,661.34 mgmt true-up + 36,015.21
  performance fee, all in the invoice month).
- Effective June 2026 FORWARD ONLY — no catch-up for earlier unaccrued periods (Arnold, Jul 2026:
  prior-period accruals assumed made; do not book retrospective catch-up).
