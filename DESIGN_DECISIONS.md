# Design decisions

**Finmo Door 1 prototype — Siddharth Karmarkar**

This is the reasoning behind `finmo-door1-prototype.html`. It explains what the prototype does and, for every choice that mattered, why I made it that way. A companion document, *Production implementation*, shows how the same demo maps onto Finmo's stack. Read this to understand the choices. Read that to see them ship.

The prototype is one HTML file with no build step, no network calls and no dependencies. All data is fake and lives in the browser, so progress survives a refresh and a reset is one click. That constraint is deliberate: the person reviewing this should be able to open it and walk the whole product alone.

---

## How to read the demo

Signup opens with a choice between a **business account** and a **personal account** (Finmo Remit). The dark *Demo controls* box in the bottom right is the remote: it fills any step with sample data, forces an upload to fail, fast forwards the compliance review, triggers a document request, clears limits, and resets. Everything below is reachable in about three minutes.

The intended path: sign up, complete KYB, get approved with starter limits, use the platform, then reset and try the sanctions and personal paths. If a screen ever seems empty, that is by design and there is a demo button to populate it.

---

## Principles

Five ideas run through every screen. When a decision was ambiguous, these broke the tie.

| Principle | What it means here |
|---|---|
| **One loop** | See the money, decide, move it, learn from the outcome. Every insight ends in a button. |
| **Propose, approve, execute** | The AI never moves money on its own. It proposes, a person approves, the rails execute, the result feeds back. |
| **No silent failures** | Every upload, payment and check ends in a visible state with a reason. Nothing vanishes. |
| **Money words, plumbing hidden** | Navigation reads Pay, Get paid, FX, not wallets and ledgers. Mechanics stay internal. |
| **Configuration, not code** | Countries, limits, rails, funds and rules are data. A new market is a new row, not a new build. |

---

## Two doors, one engine

The account type is chosen at signup because everything downstream differs. KYB collects the entity, its owners and its documents. KYC collects one person, one ID, one selfie. They share the same wizard shell, upload engine, screening pipeline and risk engine. In the code this is two step lists over one state machine, which is exactly how a second product line should look: reuse the whole verification stack, change only the steps.

## Onboarding

**Live checks as you type.** Registration-number format and PO Box detection are deterministic and run inline. The website-versus-description match is a soft check: a mismatch feeds the risk score, it does not block, because a heuristic should never turn away a good customer. The point is to catch at the field what used to surface days later, so nothing is a surprise at submit.

**Prefill, then approve.** Uploading the certificate lets MO prefill the business fields, each marked with a suggestion chip that clears when you edit it. Nothing is submitted until you review it. The first "yes" a customer ever gives Finmo is on their own company data, which is the cheapest possible demonstration of the trust pattern.

**Screening in the background.** Each person is screened the moment their card is saved, shown as a quiet status chip. By the time you reach the review step, most of the work is already done.

**Instant approval with limits.** On submit, MO assembles a KYB or KYC report, scores it, and sends it to the compliance queue. Below the risk threshold the account opens immediately with starter limits and the customer transacts at once, while the team clears the limits within one to two days. Above the threshold, or on any sanctions flag, the file routes to a manual review. Both paths share one state machine; approval-with-limits is simply a state between submitted and approved. This is the economics the brief asked for: low-risk customers move in minute one, the human review runs in parallel instead of in front.

**Pause and resume.** When the review needs a document it pauses, names exactly what it wants and why, shows an inline uploader, and resumes the moment the file verifies. A missing document never costs the customer their place. This was the specific ask, and it is modelled as a request attached to the application, not as a rejection.

## Uploads

Every upload is one component with explicit states: uploading, checking, verified, or failed with a reason and a retry. Validation runs before the upload starts: accepted formats only, a 10 MB cap, empty files rejected with an actionable message. This answers the clearest finding from my testing, a statement upload that failed silently with no error, no record and no retry. Handling failure well is the feature.

## Accounts and collections

Local collection accounts in eight currencies plus one SWIFT account, each labelled as issued through J.P. Morgan. Starter limits open the home-currency account only; full approval opens the grid, so clearing limits has a visible reward. PHP, IDR and THB are handled honestly as collect-only: the payer pays local, the customer is credited in USD, and the transaction says so. The rule that a currency can be collected but not held lives in one config list.

**Collections read as invoices, payouts read as Bill Pay**, matching the Brex shape requested. Invoices support statuses, nudges and MO payin-matching. Bills arrive, MO reads the vendor, amount and due date, and the human approves.

## Payments intelligence

Every payout runs the same pattern: the AI proposes, a person approves, the rails execute. A repeat payout to the same payee for the same amount trips a duplicate check that needs an explicit acknowledgement. A payment over 60 percent of balance flags for a second approver. Rail selection shows cost against speed instead of burying it, and defaults to the cheapest rail that meets the deadline. When a payment sends, the balance, the activity feed and the burn number all move at once, which is the one-ledger argument made visible.

## Cards

Virtual cards issue instantly with a monthly limit and an optional category lock; plastic is available on request with a shipping state. Spend lands categorised, and missing receipts are chased by MO rather than by a finance person. Cards are the one feature gated to full approval, because card issuing is the highest-risk surface in the product and gating it gives the starter tier a clean boundary.

## Treasury

The treasury account opens with the business account, the Wise way, because the low-risk money-market products carry no extra onboarding. The fund list is the real Synthesys catalogue with real minimums, settlement windows and stablecoin flags. Money moves only between the business account and treasury, never externally, and that safeguard is enforced in the transfer function, not just the copy. Higher-risk funds sit behind an explicit disclosure gate with three separate acknowledgements. Yield accrues and displays daily. Finmo is the sub-distributor and keeps the ledger; the funds sit with the managers, and the interface says exactly that.

## FX risk and Value at Risk

Exposure is assembled from what the platform already knows: foreign-currency balances, and on a toggle, unpaid foreign-currency receivables. No data entry; the ledger is the risk input.

The VaR engine is a set of pure functions, kept free of the interface so the treasury cash-tools product can reuse it unchanged. It exposes the toggles asked for: confidence (90, 95, 99), horizon (one day, one week, one month), method (parametric or Monte Carlo), and exposure basis (balances, or balances plus expected flows). Parametric is variance-covariance with representative volatilities and a single correlation factor. Monte Carlo runs four thousand seeded paths, deterministic on purpose so a demo never shows two numbers for one question.

The headline is in plain money, not a Greek letter: on a bad day for the currencies you hold, one in twenty odds, FX could cost you up to this amount this week, a model estimate rather than a promise. Below it sit per-currency contribution bars, scenario chips, and the full model disclosure. Then the number ends in a button: MO names the currency driving the risk, quotes what converting half of it does to the VaR, and offers to convert now or arm a target-rate trigger that fires automatically when the rate improves. That closes the loop on risk, the same propose-approve-execute pattern as everywhere else.

## AskMO

One entry point, no agent picker, because routing is the product's job. The suggested prompts are guaranteed to answer from the same ledger the dashboard reads, and anything out of scope gets a graceful boundary instead of a hallucination. This turns the sharpest finding from my testing, a marquee prompt that failed live, into something that cannot happen.

## Navigation

The sidebar follows the current dashboard's format: parent options that expand into sub-options. Accounts, Payments, Collections and Cards each hold their specific surfaces; Home, Treasury and Team stand alone. The grouping keeps the money-words rule, locks appear at the child level so the reason stays visible, and the personal account keeps a flat three-item nav on purpose.

---

## Edge cases handled

Invalid email and short password; wrong verification code with resend; future incorporation dates; minors as directors; ownership over 100 percent; no qualifying owner; PO Box addresses; unsupported, oversized and empty file uploads; upload failure with retry; refresh mid-wizard; back-navigation without data loss; double-submit on the application; insufficient balance and duplicate payouts; starter-limit enforcement per transfer and per month; locked features shown with a reason rather than hidden; zero FX exposure; negligible VaR; a rate trigger that cannot fund itself failing loudly; and a full reset.

## Deliberately out of scope

Real authentication, document OCR, registry and sanctions checks, multi-currency settlement, and bank connections. Each has a marked seam. The upload timer swaps for presigned URLs and an async verification vendor; prefill swaps for a real extraction service returning the same shape; the review machine swaps timers for case-management webhooks; the rails config swaps for a quoting API. Historical-simulation VaR was left out knowingly, because faking a return history would undermine credibility.

## What I would measure

Completion rate per wizard step and where people drop; time from signup to submitted and submitted to approved; document-failure rate by reason; share of applications that hit a pause and how fast they recover; time to first payment; and the acceptance rate of every MO proposal, prefill fields kept versus edited, matches confirmed, warnings heeded. That last family is the number the whole AI thesis lives on.
