# Skill Changelog (one line per change — what's installed and why)

Purpose: with 8+ skills repackaged repeatedly, this is the single place to check "what version is
installed and what changed." Add an entry EVERY time any 3CP skill is edited and repackaged.
Pairs with the standing rule: re-apply the xero-mcp-server tool-factory.ts allowlist after any
upstream repo upgrade (16-tool lockdown reverts to 51 silently otherwise — check that separately).

| Date | Skill | Change | Why |
|---|---|---|---|
| Jul 2026 | 3cp-close-orchestrator | Plain-language style, table+source citation rules, active follow-up, accrual search hierarchy, coverage check (1 claim per item), MoM variance flag, Draft/cut-off checks, 835 reversal integrity | New-staff usability + double-count prevention |
| Jul 2026 | 3cp-close-orchestrator | Workpaper self-audit gate (structural/arithmetic/cross-tab/traps/live-flags) | June close: user review caught a stray value + dead check formula + stale refs the build missed |
| Jul 2026 | 3cp-close-orchestrator | Mode 2 control-account tie-out (15 balance-sheet accounts vs subledger schedules) | P&L-only completeness isn't enough; balance sheet can drift silently |
| Jul 2026 | 3cp-close-orchestrator | Two-direction cut-off + source-citation completeness checks | 5-Jul item inside a June-named report; empty-Source rows slipping through |
| Jul 2026 | 3cp-close-orchestrator | Cross-module signal routing (consumes expense-skill signals) | Laptops/prepayments surfaced by Expensify scan need a routing owner |
| Jul 2026 | 3cp-close-orchestrator | Variance flag reads variance-tolerance-table.md instead of one generic rule | Per-account bands needed, not a single ≥2×/5,000 rule |
| Jul 2026 | 3cp-payroll-close | 802 MPF Payable model, intern (Leo Zhang) → 477CI, bonus on crystallisation | June payroll build |
| Jul 2026 | 3cp-shared-reference | 471 A/C account, LSE-04/05, SVC-09 Xero sub, 651 SP1, TD-as-bank-account rule, FX single-transfer rule, TRS-06/07/08 | June treasury/lease findings |
| Jul 2026 | 3cp-shared-reference | 640 corrected to cash-only; 870 interest accrual added | Live ledger screenshot showed the actual split |
| Jul 2026 | 3cp-shared-reference | subledger-schedules.md, variance-tolerance-table.md, skill-changelog.md created | Month-to-month continuity + defined variance bands + version tracking |
| Jul 2026 | 3cp-shared-reference | Register: printer leases (461, Mitsubishi 398 + HP 194.10, monthly recurring); wine-vault amortisation (469, 3,467.50/mo from Jul-26); GP I Ltd corrected quarterly (÷3, not ÷12) | Arnold's Direct Payments classifications, 9-Jul |
| Jul 2026 | 3cp-monthly-journals | Mandatory accrual search hierarchy (bank→Expensify→ask); stale skill-name refs fixed (→ expense-monthly-close-builder) | HKBN double-count near-miss |
| Jul 2026 | expense-monthly-close-builder | AMEX one-month-arrears model (was assumed same-period) | May/June autopay tie-out proved the lag |
| Jul 2026 | expense-monthly-close-builder | Two-layer approval recognition gate (Draft/Sally/Alex) | Arnold's clarification on the approval workflow |
| Jul 2026 | expense-monthly-close-builder | Cross-module signal scan + rolling-export dedup | Laptops/prepayments found via Description field scan |
| Jul 2026 | expense-monthly-close-builder | AMEX Clearing completeness tie-out (must equal full statement total) | Suspense leg was omitted in a rebuild — caught in review |
| Jul 2026 | 3cp-investment-treasury-close | --principal module (TD placements, fund investments, mandatory sweep) | SP1 380k + TD 350k both missed by income/valuation-only modules |
| Jul 2026 | 3cp-investment-treasury-close | MTM = price-only (never combined incl. "Other"); dividends by ex-date; interest split 640/870; WHT by ex-date; CCB interest = bank account | Multiple corrections from Arnold's review against source statements |
| Jul 2026 | 3cp-revenue-recognition | Investment-vehicle accrual: monthly on prior invoice ÷3 (quarterly) or ÷12 (annual), true-up on invoice; June-forward only, no catch-up | Policy change, confirmed by Arnold |
| Jul 2026 | 3cp-revenue-recognition | GP I Ltd corrected: quarterly (÷3), not annual (÷12) — confirmed from Q4-2025 invoice | Arnold, 9-Jul |
| Jul 2026 | 3cp-xero-journal-poster | Demo→live migration checklist (COA diff, opening-state checks, parallel run) | Entire pipeline validated on Demo only |
| Jul 2026 | 3cp-expense-journal-entry | UNINSTALLED — superseded by expense-monthly-close-builder | Consolidation |

| Jul 2026 | 3cp-shared-reference | Entity due-from account map (658/659/660/663/666/667; GP III TBC); Addepar quarterly prepayment (SVC-12); vehicle accrual moved to JE-Revenue presentation | Arnold's item-6 resolutions, 9-Jul |

| Jul 2026 | expense-monthly-close-builder | Per-card AMEX model deprecated; clearing+suspense adopted go-forward; migration steps documented | Arnold decision 9-Jul after live-ledger review |
| Jul 2026 | 3cp-xero-journal-poster | Migration checklist §F: AMEX transition (seed suspense from card balances, Expensify integration reconfig, archive card accounts) | Same |
| Jul 2026 | 3cp-shared-reference | 665 = SMA GP III; suspense opening = seeded by migration reclass; AMEX convention + entity-map policy notes | Same |

| Jul 2026 | 3cp-xero-ui-operator | NEW SKILL — sole browser-writer (claude-in-chrome) for the 8 UI-only ops: statement CSV import, reconcile-OK clicking (double-confirmed tier), DRAFT promotion, void/delete (per-item), repeating ACCPAY bill setup, contact default-currency, invoice reference backfill, FX transfers. Mirror of the poster for the browser; safeguards S1–S6 (org check, screenshot-before-click, API verify-after-write) | Bridge xero-3cp MCP gaps; Arnold request 15-Jul |

## Pending (not yet built)
- Post-posting diff + idempotency check (poster skill) — build after first live posting run proves out
