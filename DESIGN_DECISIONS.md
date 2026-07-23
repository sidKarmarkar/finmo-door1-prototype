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

## What I took from Brex, Ramp and Wise

Three patterns are borrowed deliberately, one per company, each named here so the lineage is explicit.

**Approvals, from Brex.** Payments above a configurable threshold need a second person, and whoever prepared a payment cannot be the one who releases it. This turns two things that were previously decorative, the Wise-style roles and MO's large-payment flag, into actual product: a Preparer creates and an Admin or Payer releases, money leaves the balance only on approval, and every decision is recorded with who and when. Finance teams buy controls, and controls are the cheapest credibility a payments product can carry. The demo lets you switch acting role to see both sides of the same payment.

**Proving the saving, from Ramp.** Ramp's growth motion is telling customers what they saved. The Home dashboard now carries a Saved with Finmo figure, itemised into FX margin avoided (our 0.5 percent against a typical 2.5 percent bank spread), wire fees avoided (local rails against a wire), and treasury yield earned, with the method written underneath. Every number traces to a real transaction in the ledger and the assumptions are deliberately conservative, because a savings claim that cannot be audited is worth less than no claim at all. It also weaponises the transparent pricing the product already practises.

**Tracking, from Wise.** Wise treats a transfer like a parcel, and that is the most loved pattern in consumer money movement. Every payout now has a staged tracker, submitted, checks passed, on the rail, delivered, with an arrival estimate that reflects the chosen rail, minutes for FAST or NPP, dated for SWIFT. If something slows down, the product says so before the customer asks, which is the same no-silent-failures rule applied to money in transit rather than documents.

The point of borrowing openly is the sentence that follows it. Brex and Ramp are US only and card led. Wise moves money everywhere with no view on whether you should. Finmo is treasury first, cross border, on its own licences, with an AI that proposes and rails that settle. The others recommend without executing or execute without recommending, and closing that loop is the whole thesis.

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

## What I took from Sourav's prototype

Sourav built a business account prototype in parallel, strongest on the accounting data layer. Three ideas from it are better than what I had, so I took them and said so.

**Cash runway.** His framing ties everything to the number an owner actually feels: how long the money lasts. Home now carries a forward projection built from the due dates on unpaid invoices and upcoming bills, with a period switch of 7, 14 or 30 days, the projected balance as a line, and the tightest point in the window called out. One deliberate difference: **overdue receivables are excluded from the projected line.** Money you were already promised and did not receive is not money you can plan around, and a forecast that counts it flatters the customer into a cash crunch. They appear instead as an insight with a chase button, which is where they can actually be acted on.

**Insights as sentences.** Above the chart sit plain statements rather than metrics: what is more than thirty days overdue, where cash dips and when, the largest outflow ahead, and whether the window ends up or down. Each one that can be acted on ends in a button, which is the same rule as everywhere else in the product.

**Aging as charts.** Receivables and payables aging were a line of text; they are now bucketed bar charts, receivables by how late (not due, 1 to 30, 31 to 60, 60+) and payables by when due (overdue, this week, 8 to 30, 31+), with colour carrying the risk. The buckets sum exactly to the underlying totals, which is asserted in the tests, because a chart that does not reconcile to the ledger is worse than no chart.

**List depth.** Invoices and bills both got search, status filters, a due date range, per row day counts, and amounts shown in their own currency with the home equivalent underneath. Manual upload sits alongside the accounting sync as a fallback, because the sync will always miss something and the user should never be stuck.

## Where his architecture was pointing, and what I built next

Sourav's screen states his thesis plainly: bring receivables and payables into Finmo to collect and pay in one place. The accounting system stays the record of what you owe and are owed, and Finmo becomes the layer that acts on it. Follow that one step further and the gap is obvious. Both prototypes could show you a beautiful payables aging chart and then make you pay the bills one at a time. No finance team works that way. So I built the three things the architecture implies.

**Contacts, the counterparty master.** He has it in his navigation; this is what it is for. Every customer and vendor, built automatically from invoices and bills including everything synced from the accounting system, with payment details saved once so a payout is never a retyped account number. It also carries payment behaviour: measured from when each customer actually paid against when the invoice was due. That number is not decoration, it is what makes a cash forecast honest, and it is what lets the chasing sequences start firm with a customer who is reliably thirty days late.

**The payment run.** The thing a finance team actually does on a Friday. Select everything due, and the product does the work around it: totals per currency, a funding check across your balances, MO's pre-flight on the whole batch (duplicates, missing payee details, size against your balance), then one approval covering the run rather than one per bill. Each payment still executes and tracks individually, and anything that came from the accounting system is written back as paid.

One case in there is worth calling out because it only appears once you build it. If the run needs USD you do not have, the obvious move is to convert from your largest balance. But that balance may already be committed to its own bills in the same run, so converting quietly creates a second shortfall. The funding check therefore only offers a source with surplus **after** its own share of the run, and says so plainly when nothing qualifies. Fixing one currency should never break another.

**Chasing.** The symmetric half. Overdue invoices get an escalating reminder sequence, friendly at day one, firm at day seven, final at day fourteen, drafted by MO from the invoice and adapted to that customer's known payment behaviour. You approve the sequence once rather than each email, and it stops by itself the moment the invoice is paid. Approving a policy instead of approving every message is the only version of this that saves anyone time, and it is the same propose, approve, execute pattern applied to collections.

Together these close his loop: the accounting system says what is owed, the intelligence says what matters, and the product moves the money in one action instead of twenty.

One place I deliberately diverged: his invoice screen has a receivables and payables toggle in one list. Since collections is money in and payouts is money out, I kept receivables under Collections and payables under Payouts, and gave both the same list depth rather than merging them. Same capability, without breaking the split.

## Navigation: money out, money in, and FX outside both

The sidebar now names things the way the business thinks about them. **Payouts** is money going out (send a payout, approvals, bills). **Collections** is money coming in (invoices, payment links). Calling the first one Payments was wrong, because a collection is also a payment, just in the other direction, so the pair had no symmetry.

**FX sits outside both.** Converting money is not a kind of payment, it is something you do to money you already hold, and it applies equally to money on its way in and on its way out. It gets its own section with three sub-options: Convert, Stablecoins, FX risk.

**Convert** is the Wise pattern applied honestly: pick what you hold, pick what you want, see the mid market rate, the fee as a separate line, and what you actually receive, then it happens instantly because the money never leaves Finmo. On fiat pairs it also shows what a bank would have charged, which is the same savings logic as the dashboard card.

**Stablecoins** treat USDC and USDT as two more currencies in the same account rather than a crypto annex. That single choice is what makes everything else free: they appear in balances, in conversions, in the risk engine, in analytics and under the same approval rules, with no separate plumbing. You get a deposit address per coin per network, and the network is chosen *before* the address is shown, because sending USDT on the wrong chain is the most common way people lose money on chain. The margin is tighter between two stablecoins (0.1 percent) than between a stablecoin and a currency (0.5 percent), because one is a swap and the other is real FX.

## Insights: the data layer that drives the account

Finmo has two products. The business account, which this prototype is, is regulated and moves money. Cash tools is an unregulated data layer that reads external banks and accounting systems. The strategy is that the data layer drives usage of the account, and the Insights surface is where that meets the account the prototype already has.

Connect external accounts (read-only, simulated here) and the product surfaces specific, quantified nudges: international wires that could have gone on local rails and what that would have saved, FX paid at a wide external spread versus Finmo's 0.5% and the delta in money, an unhedged currency mismatch pointing at the FX risk screen, and a coming liquidity gap with a way to bridge it. Every insight ends in a business-account action. This is the difference between selling an account, which Airwallex and Revolut do, and wrapping the account in intelligence that grows it. It is also, deliberately, the clearest expression of the AI Payments role: turning transaction data into reasons to move money through Finmo.

## Forecast drivers, scenarios, and honest confidence

The cash forecast now models the recurring flows a real business runs on, payroll, rent, a vendor contract, a customer retainer, shown as editable drivers rather than inferred silently. Each carries an end-date, which fixes the specific failure a naive forecast makes: a detected payroll gets assumed to run forever, and a vendor contract that ends in two months keeps being counted. Giving the contract an end-date stops it, and toggling any driver off models a what-if instantly. This is the honest, low-friction alternative to a treasury system demanding uploaded contracts.

Confidence is stated, not faked. With thin data the forecast says so plainly, "about two of six months of history, we will not put a false accuracy number on it," and only claims seasonal confidence once there is enough history. This matters as a distinction: statistical confidence, as used in the VaR screen, is legitimate because FX exposure is a known distribution, whereas a cash-flow forecast cannot honestly carry a confidence percentage without data. Conflating the two is how forecasting products lose trust, so the prototype keeps them separate.

Accuracy is then shown the way a treasury practitioner actually reads a forecast: not one number, but a curve by horizon. The prototype sets a target per band, 99% at 0 to 5 days, 95% at 6 to 14, 85% at 15 to 30, 70% beyond, and shows measured against target where there is enough history to measure, and an honest "building" state where there is not. The near term hits its high target because it is driven by committed flows; the far term degrades and is allowed to say so. This tiered framing came from a treasury practitioner's feedback, and it is a better answer than a single accuracy figure precisely because it matches how the people who live with forecasts judge them.

## The welcome screen: value before the form

Marketing feedback, relayed through the team: onboarding should be more conversational, and the benefits should be explained before signup begins, the way Airwallex does it. Right, and the fix is a value-first welcome screen that now sits before the form.

It follows the pattern that converts: a benefit headline, one clear line of what the product does, and an immediate call to action, then hard proof points (a live balance in minutes, nine local currencies plus SWIFT, 0.5% FX against a bank's 2.5%, same-day first payment), four benefit cards, a trust row naming the licences and that funds are safeguarded, and a repeated call to action at the end. Two consumer-psychology levers do the real work. Reciprocity: the fee-waiver offer is stated up front and repeated inside the wizard, so the user is completing signup to claim something rather than just to comply. Reduced friction and reassurance: "free to open, about ten minutes, no sales call, approved on the spot," which pre-empts the three anxieties that cause abandonment, cost, effort, and delay.

The signup itself is now conversational, one question per screen the way a good mobile app asks, rather than a wall of fields. Name, then email that greets you by that name, then password, then market, each a single large input with a progress indicator, a back arrow, and Enter to advance. Asking one thing at a time lowers the perceived effort of every step and is the single biggest lever on completion, which is why every app that depends on signups converged on it. The email verification screen follows the same one-thing pattern.

Inside the wizard, completion psychology is made explicit: a progress bar with the step count and an encouraging line that changes as you advance ("over halfway, keep going"), the incentive reminded at the foot of every step, and the note that progress saves automatically. The goal throughout is that the person always knows how far they are, what they get, and that stopping loses nothing. That is what turns a compliance form into something people finish.

## Making it intuitive, and pricing tiers

Two smaller asks that both matter for how the product reads.

**Intuitiveness.** The single loudest note was that you could not tell your balances without leaving the dashboard. Beyond the fix on Home, the header now carries your live balance at all times, so no screen ever hides how much money you have. The sidebar gained a quiet icon per section for scannability, the active item gets a left accent so you always know where you are, and cards got a faint shadow so the page reads as layers rather than a flat wall. None of it is decoration for its own sake: the goal was that a first-time viewer can find anything in one glance, which is exactly what a busy finance person needs.

**Pricing tiers.** The accounting integration is a paid capability, not a free one, so the product now carries three plans: Essential (the account, payments, cards, treasury and FX), Plus (accounting sync, payment runs and automated chasing), and Enterprise (multi-entity groups, dedicated FX pricing, API). On Essential the accounting connect is visibly gated behind an upgrade rather than hidden, because a locked feature you can see is a sales prompt and a feature you cannot see is a missed one. The current plan sits in the header. This keeps the demo honest about where the monetisation is without turning it into a paywall maze.

## Balances on the dashboard

The first version buried the money: you could see a total, but you had to open Accounts to find out what you actually held in each currency. That is backwards for a business account, where the first question every morning is what have I got and in what.

Home now lists every open wallet with its balance, its home equivalent and buttons to convert or send from that currency directly. Underneath sits a convert box, so the most common action in a multi currency account never requires leaving the page. Opening a new currency is one click from the same place, and a new wallet appears immediately with a zero balance rather than being hidden until it has money in it. That last detail matters: an empty wallet you can see is an invitation to fund it, and a wallet you cannot see until it is funded is a chicken and egg problem.

## Currencies you can actually hold

Nine local currencies (USD, CAD, GBP, EUR, HKD, AUD, SGD, NZD, AED) plus the two stablecoins, and conversion works between any pair, not just into and out of the home currency. Previously the conversion source was limited to currencies that already had a balance, which made the screen look like it only supported one direction. Now any open wallet is a valid source, which is the Wise behaviour: hold what you like, move between them instantly, see the fee as a line item.

## Multiple entities

A group signs up once and then grows: the Singapore company, then the Australian one. The design follows Brex, where entities live under one organisation rather than as separate logins.

**Ownership decides the speed, not the paperwork.** When you add an entity you say whether it has the same owners as its parent. If it does, we already screened those people and nothing about the risk picture changed, so we check the new registration and the entity opens immediately. If the owners are different, we collect and screen the new people first, which takes about a day. This is the honest reason one path is instant and the other is not, and it is a better answer than a blanket promise about speed.

**Structures nest.** Parent, child, and child of child, as deep as the real group goes, because a holding company above operating companies in three markets is the normal shape of the customer we are describing, not an edge case. Each entity shows its own balance and, where it has companies beneath it, the rolled up total of everything below. The market list marks where Finmo holds its own licence (Singapore, Australia, the UK, Dubai, Hong Kong) since those open fastest.

**Each entity keeps its own books.** Separate balances, transactions, invoices and bills, because mixing two companies' ledgers is exactly what an auditor will not accept. The entity switcher sits in the top bar next to the account name.

**Combined view for seeing, single entity for acting.** You can look at the whole group's balances at once, but every action happens inside one entity. Seeing is safe to aggregate; moving money is not.

**Intercompany transfers settle inside Finmo.** Moving money from the Singapore company to the Australian one is a ledger movement with an FX conversion if the currencies differ, not an external wire. No rail fee, no waiting. This is also the foundation of the treasury chain from the original report, where the AI spots one entity short for payroll while another sits on surplus and proposes the transfer.

**Roles scope to entities.** A bookkeeper can be given the Australian company only. Access is a pair, what you can do and where you can do it.

## Accounting integrations

Finance teams live in Xero or QuickBooks and treat the bank as a place to retype numbers into. So the product connects to the books, pulls in unpaid bills and outstanding invoices, lets you pay them from your Finmo balance, and then **writes the payment back** so the books reconcile themselves.

The write-back is the part that matters and the part most integrations skip. Pulling data in is a convenience; pushing the result back is what removes the manual reconciliation where duplicate payments are born. Everything that came from the accounting system carries a source badge, and disconnecting removes only the synced items and leaves yours alone, because a customer should never lose their own data by turning off an integration.

**Scheduled and recurring invoices.** An invoice can go out now or on a future date, and can repeat weekly, monthly or quarterly. A scheduled invoice is deliberately excluded from receivables, from the aging buckets and from the cash forecast until it actually goes out, because counting money you have not yet asked for is the fastest way to make a forecast lie. It also cannot be scheduled to send after its own due date, which is the kind of small validation that stops a support ticket.

There is a second reason this exists: due dates. Bills with real due dates from the accounting system are what make a cash forecast credible rather than decorative.

## AskMO

One entry point, no agent picker, because routing is the product's job. The suggested prompts are guaranteed to answer from the same ledger the dashboard reads, and anything out of scope gets a graceful boundary instead of a hallucination. This turns the sharpest finding from my testing, a marquee prompt that failed live, into something that cannot happen.

## Dashboard analytics

Home leads with the numbers a customer checks most, computed live from the ledger: money received and paid out with a period toggle for today, this month and year to date, money awaiting collection with overdue flagged, a seven-day in-and-out chart, and an invoice breakdown of paid, pending and overdue by count and value.

The set is chosen around the four questions an owner actually asks: what came in, what went out, what is stuck, and how long can we breathe. **Received, paid out and net flow** answer the first two per period, with net flow signed and coloured because direction matters more than magnitude. **Awaiting collection**, **days sales outstanding** and an **aging line** (current, 1 to 30 days late, over 30) answer the third: DSO is open receivables over total billed scaled to a thirty-day period, the standard form, with the slowest payer named and how late they are, and aging tells you where the money is stuck rather than just that it is. **Bills pending this month** and a **cash cover** estimate, how many days the balance lasts at the current pace of outgoings, answer the fourth. Each metric ends in a button, follow up on the slowest payer or review and pay the bills, keeping the rule that every metric leads somewhere.

This is deliberately the operator's cut of analytics rather than the treasurer's: the cash-flow summary on the treasury side reads bank and ERP data, while these read the account's own invoices and bills, which is what a Door 1 customer actually acts on. What was left out is as deliberate as what went in, no vanity charts, no metrics without an action, and nothing that duplicates the treasury view. Everything recomputes as money moves, because it reads the same ledger the rest of the product writes to.

## Navigation

The sidebar follows the current dashboard's format: parent options that expand into sub-options. Accounts, Payments, Collections and Cards each hold their specific surfaces; Home, Treasury and Team stand alone. The grouping keeps the money-words rule, locks appear at the child level so the reason stays visible, and the personal account keeps a flat three-item nav on purpose.

---

## Edge cases handled

Invalid email and short password; wrong verification code with resend; future incorporation dates; minors as directors; ownership over 100 percent; no qualifying owner; PO Box addresses; unsupported, oversized and empty file uploads; upload failure with retry; refresh mid-wizard; back-navigation without data loss; double-submit on the application; insufficient balance and duplicate payouts; starter-limit enforcement per transfer and per month; locked features shown with a reason rather than hidden; zero FX exposure; negligible VaR; a rate trigger that cannot fund itself failing loudly; and a full reset.

## Deliberately out of scope

Real authentication, document OCR, registry and sanctions checks, multi-currency settlement, and bank connections. Each has a marked seam. The upload timer swaps for presigned URLs and an async verification vendor; prefill swaps for a real extraction service returning the same shape; the review machine swaps timers for case-management webhooks; the rails config swaps for a quoting API. Historical-simulation VaR was left out knowingly, because faking a return history would undermine credibility.

## What I would measure

Completion rate per wizard step and where people drop; time from signup to submitted and submitted to approved; document-failure rate by reason; share of applications that hit a pause and how fast they recover; time to first payment; and the acceptance rate of every MO proposal, prefill fields kept versus edited, matches confirmed, warnings heeded. That last family is the number the whole AI thesis lives on.
