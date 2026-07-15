# Client name mapping (tracker ↔ Addepar) — LOCKED

The administrator payment tracker, the Addepar export, and the mapping file use **different names** for the same client. This table is the authority. Match tracker→Addepar on this; the new Addepar export also carries **Top Level Client**, which resolves formerly-blank portfolios natively.

| Tracker client | Addepar Billable Portfolio | Notes |
|---|---|---|
| Alice Cheng | A Cheng Family | |
| Emily Lu | Emily Total AUM for Invoice | ⚠ tracker code says "Emily Lu Jerry Lu (2 accounts)"; invoiced far exceeds Addepar — see flag |
| Jerry Lu | Jerry Total AUM for Invoice | formerly blank `EHI-*`; now resolved via Top Level Client |
| Ethan and Yixin | T&L Family - Y (+ T&L Family - E) | one combined invoice; T&L Family - E currently nil |
| Kelvin Pan | Kelvin Pan | |
| Lili Huang | W&H Family | |
| FSGHKN | Gu Family | |
| Ko | Ms. Ko | tracker code "Ms Ko" |
| Robert Wu | Robert Wu | |
| Emily Chen | Emily Chen | |
| Spencer Kuo | Spencer Kuo | |
| Dr. Zheng | Zheng Family | |
| Henry Chen | **Mae Family** (shared) | Chen Tai-Heng rolls into the Mae Family portfolio |
| Mae Chang | **Mae Family** (shared) | Mae Chang + Henry Chen together = Mae Family |
| Qian | W&Q Family | |
| Kang Pei | K&C Family | |
| Amy Li | L&Y Family | tracker code "Vive Shine" is stale — ignore it; amounts confirm L&Y Family |
| Paul Fan | JP Family | new Mar 2026 |
| Amy Sadick | **(non-Addepar)** | own estimation accrual + true-up — see `non-addepar-estimation.md`; excluded from the Addepar true-up |

## Combined portfolios (many tracker clients → one Addepar portfolio)
- **Mae Family** = Mae Chang + Henry Chen (Chen Tai-Heng). Reconcile the *sum* of both tracker invoices against the single Mae Family portfolio.
- **T&L Family - Y / - E**: the "Ethan and Yixin" invoice covers both; T&L Family - E is nil for now.

## How to use
Reconcile invoiced (tracker Column T) to Addepar **net** by Addepar Billable Portfolio after applying this table. With it applied, Q1 2026 residuals are immaterial for every client **except Emily Lu** (see flag), confirming the mapping — most of the headline true-up was a name-matching gap, not a real fee difference.

## Emily Lu (resolved)
An earlier Addepar calc under-stated Emily Lu (invoiced 48,858.80 vs net 16,623.93). The **updated calc resolved this** — Emily now ties to invoiced, and the Q1 true-up fell to an immaterial −486.95. Retained as a reminder to sanity-check Emily Lu when calc versions change.

## Client codes (for per-client journal references)
Revenue posts **one journal per client (Billable Portfolio)**; references use `3CP-REV-<period>-MGMT-<CODE>-USD` and `-TRUEUP-<CODE>-USD`. Codes are stable:

| Billable Portfolio | CODE |
|---|---|
| A Cheng Family | ACHENG |
| Emily Total AUM for Invoice | EMILY |
| Jerry Total AUM for Invoice | JERRY |
| T&L Family - Y | TLY |
| T&L Family - E | TLE |
| Kelvin Pan | KELVIN |
| W&H Family | WH |
| Gu Family | GU |
| Ms. Ko | KO |
| Robert Wu | ROBERTWU |
| Emily Chen | EMILYCHEN |
| Spencer Kuo | SPENCER |
| Zheng Family | ZHENG |
| Mae Family | MAE |
| W&Q Family | WQ |
| K&C Family | KC |
| L&Y Family | LY |
| JP Family | JP |
| Amy Sadick (non-Addepar) | AMYS |

New portfolios: assign a short uppercase alphanumeric code and add it here so references stay stable across months.

## DO NOT TOUCH — parked invoices

- **INV-0625 (KUO, Q2 2026 draft):** has a known date-label bug and a stray junk line. Left untouched **intentionally** — do NOT edit, correct, delete, or include in any reconciliation or reclass until the new billing process takes effect (per Arnold, July 2026). If a Q2 invoice run encounters it, skip and flag; never auto-fix.
