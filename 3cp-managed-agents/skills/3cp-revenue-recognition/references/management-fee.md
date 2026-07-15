# Module: Management Fee — monthly accrual (`--mgmt-fee`)

Recognise management fee monthly as earned, from the Addepar export. The skill does not calculate
the fee; it reads it.

## Inputs
- **Addepar export** (view "[3CP] Monthly Management Fee - Addepar Billing View"). Header rows
  precede the table; columns include: `Top Level Holding Account` · `Top Level Client` ·
  `Billable Portfolio` (= the client/family) · `3CP - Invoice Chargeable` · `3CP - Invoice Tiering` ·
  `Assets Billed On (USD)` · `Billing Period` · `Bill Gross Fee Amount (USD)` ·
  `Bill Fee Amount (USD)` — **all USD**.
- **Revenue receivable list** — to reconcile the accrual and roll the receivable forward.

## Which fee column — use NET (`Bill Fee Amount`)
The export carries **two** fee columns: **`Bill Gross Fee Amount (USD)`** (before tiering) and
**`Bill Fee Amount (USD)`** (after the `Invoice Chargeable`/`Invoice Tiering` adjustments — the
**chargeable/invoiced** figure). **Use `Bill Fee Amount` (net)** for the accrual — it is the billed
basis and gives the smaller residual against the invoiced tracker. Ignore the gross column (kept
for reference only). The gross↔net gap is per-client tiering, material only for a few clients
(e.g. W&H, Zheng, JP/Paul Fan, and a one-off Jan spike on T&L Family - Y).

## Accrual amount per client (handling rules)
- **Find the header row** by locating "Billable Portfolio" (metadata rows precede it).
- **Exclude the grand-total row** (`Top Level Holding Account == "Total"`) — including it doubles
  the accrual.
- **Group by `Billable Portfolio`**; net within each (negative rebate/offset lines included).
- **Blank `Billable Portfolio` rows** resolve via the in-export `Top Level Client` (e.g. `EHI-*` →
  Jerry Lu = "Jerry Total AUM for Invoice"). Do not drop.
- **Tracker↔Addepar name differences:** apply `references/client-mapping.md` (LOCKED) — several
  names differ (Amy Li→L&Y Family, Henry Chen+Mae Chang→Mae Family, etc.).
- **Reconcile** computed net total to the export's Total row each month.
- Everything is **USD**.

## Recognition — monthly manual journal, per client (CONFIRMED model)
**Each month-end, book one manual journal per client:**
- **DR 622 Management fee receivables** (accrued / unbilled)
- **CR 200 Revenue - Management Fees**
- USD; amount = that month's Addepar `Bill Fee Amount` (net). One journal, one line-pair per
  client (lines grouped by `Billable Portfolio`).
- Reference: `3CP-REV-<period>-MGMT-USD` (one journal covering all Addepar clients that month;
  Amy Sadick is a separate stream, see below).

**At quarter-end, the real client invoice is raised in Xero by the accountant (not by this
skill), with its line(s) coded to 622 — not 200.** Coding to 622 makes Xero auto-post
`DR 610 Accounts Receivable / CR 622`, which reclassifies the accrued receivable into a billed
trade receivable **without re-recognising revenue** (already booked by the three monthly
accruals). There is no manual reclass journal — the invoice itself performs the reclass.

> **Historical note (Q1 2026):** the Q1 client invoices actually posted (INV-0603, INV-0604,
> INV-0609 — confirmed in Xero) were coded directly to **200**, not 622, with three line items
> (Jan/Feb/Mar) on a single quarter-end invoice, and **no monthly manual journal was booked**.
> That was the process *before* this accrual model was confirmed. **Going forward, the operational
> change is: monthly manual journal to 622, and the quarter-end invoice line recoded to 622**
> (not 200) so revenue isn't double-counted. Flag this transition explicitly in the first period
> this skill runs, since the accountant needs to adopt the 622 invoice-coding change.

### Quarter-end reconciliation (required)
In the quarter-end month, per client, check: **Σ (the quarter's three monthly accruals) = the
quarterly invoice total.** They should tie exactly for Addepar clients (same Addepar source feeds
both). Surface any gap in the Review section **before** the invoice is finalised; do not silently
absorb it. Prior-month restatement is not expected, so a non-zero residual is a flag, not a
routine true-up.

*Worked example — Q1 2026 (USD, NET, updated Addepar exports):* Jan 222,396.26 + Feb 220,000.12 +
Mar 216,644.25 = **659,040.64** accrued; would tie to a Q1 invoice total of the same figure had the
622-coding process been in place. Actual Q1 invoices (coded to 200, per the historical note above)
totalled a comparable figure — treat Q1 as the pre-change baseline, not a live reconciliation
example.

## Non-Addepar exceptions
**Amy Sadick** is billed via a separate calculation, not Addepar — not in the Addepar export, so
exclude her from the Addepar accrual/true-up and book her as her own stream (own manual journal,
ref `…-MGMT-AMYS-USD`): monthly estimate = 1/3 of the prior quarter's actual, with a quarter-end
true-up to the standalone Excel actual. Full method in `non-addepar-estimation.md`.

**Not an exception — new Addepar clients:** a client new this period IS in Addepar from their join
month. Paul Fan is an Addepar client (Billable Portfolio "JP Family"), new in March 2026 — so JP
Family appears in the March export only (Jan/Feb = 0) and is already inside the March accrual.
Treat new clients as ordinary Addepar clients from their first month; do not mistake "new this
quarter" for "non-Addepar".

### Blank Billable Portfolio → resolve via Top Level Client
Blank `Billable Portfolio` rows are resolved through the mapping file (`Client Account Mapping`, by
Top Level Holding Account → Top Level Client). Confirmed: all `EHI-*` accounts → Jerry Lu ("Jerry
Total AUM for Invoice"). These are inside Addepar (already in the monthly total) — Jerry Lu is
**not** a non-Addepar exception. Granular EHI→Jerry resolution matters at quarter-end AR aging, not
for the monthly total.

## Flags
- New/departed client — appears/leaves in Addepar from their join/exit month (e.g. Paul Fan / JP
  Family new Mar 2026); flag, treat as ordinary Addepar client.
- Blank `Billable Portfolio` rows — resolve via Top Level Client mapping (EHI-* → Jerry Lu);
  included in monthly total; never drop.
- Currency: fees are USD (invoiced USD). Occasional HKD payment → realised FX is Xero's.
- AUM or fee that moves materially vs prior month — flag for sanity.
- **Quarter-end invoice coding** — confirm with the accountant that the quarter's client invoice
  line is coded to 622 (not 200, the historical Q1 2026 pattern). If it's coded to 200 again,
  revenue will double-count; flag before the reconciliation is signed off.
- **Invoice TaxType — confirmed OUTPUT.** The Q1 2026 invoices used TaxType `OUTPUT`, and this is now the confirmed convention for client management-fee invoices — not `Tax Exempt` (which remains the manual-journal default elsewhere in the skill suite). Pass this on to whoever raises the quarter-end invoice.
