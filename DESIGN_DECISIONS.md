# Door 1 prototype, design decisions

Siddharth Karmarkar, July 2026. Companion doc for finmo-door1-prototype.html. Every choice below is written the way I would defend it in a room.

## What this is

A clickable prototype of the Door 1 journey from the rebuild report: a new SMB signs up, gets verified, and uses the platform, with the KYB flow modeled on Brex. It covers signup, email verification, a six step KYB wizard, a review tracker that can pause and ask for documents, and the post approval product with Home, Accounts, Pay, Get paid, FX and AskMO.

To run it, open the HTML file in any browser. No install, no network, all data is fake and stays on the machine. The dark panel bottom right holds demo controls: fill any step with demo data, force an upload to fail, fast forward the review, trigger the document request pause, approve instantly, reset. A prototype that needs a narrator is a broken prototype, so the demo controls exist to let Akhil walk the whole loop alone in about three minutes.

## One HTML file, vanilla JS

The deliverable is a single file because the audience is one person on WhatsApp. No build step, no hosting dependency, nothing to break between my machine and his. The internal structure still mirrors production: pure render functions per view (these become React components), one state object (this becomes server state plus a client store), and a config object per country (this becomes a data driven country pack). The prototype is disposable, the shape of it is not.

State persists to localStorage with a try catch fallback, so closing the tab mid application and reopening resumes exactly where you left off. That is not a convenience feature, it is a Brex onboarding pattern: nobody finishes KYB in one sitting, so save and resume is table stakes and I wanted the prototype to prove it rather than claim it.

## Why the flow is shaped like Brex

Four Brex patterns are copied deliberately.

First, the checklist before the form. Before the wizard starts, an intro screen lists exactly what to have ready: certificate, address proof, IDs. Abandonment in KYB comes from surprise requirements, so you surface them when the user still has zero sunk cost.

Second, progressive disclosure. Six small steps with a rail showing position, not one long form. Completed steps stay clickable for edits, future steps do not, so the user can go back without being able to skip ahead.

Third, the applicant sees status the whole way through. After submit, the home page is a review tracker with named stages and plain language descriptions of what each stage checks. The report made the point that a timestamp that hides staleness destroys trust; the same logic applies to a review that hides progress.

Fourth, the product opens before approval. From the tracker you can explore the dashboard while the review runs. Moving money is locked with a visible reason, everything else renders. This protects the exact wedge the report says to protect at all costs, value before compliance friction, while keeping the compliance line hard.

## KYB as a state machine

The application is a state machine: draft, in_review, action_needed, approved, with rejected reserved in the design. The pause Akhil asked for is modeled as a document request object attached to the application, not as a rejection or a dead end. When compliance needs something, status flips to action_needed, the tracker shows an amber stage with the specific document, the reason it is needed, and an inline uploader. The moment the upload verifies, status flips back to in_review and the review resumes from the same stage. Requests are a list, so multiple simultaneous asks scale without touching the machine.

This mirrors how case management actually works at a regulated institution, so wiring it to a real compliance backend later is a webhook per transition, not a redesign.

## Uploads can fail loudly, never silently

This is a direct answer to my testing finding, the SoFi statement that vanished without an error, a record, or a retry path. Every upload slot in the prototype is one component with explicit states: empty, uploading with a progress bar, checking, verified, failed. Failed always carries a human readable reason and a Retry button, and a failed document never costs you your place in the flow. Validation runs client side before the fake upload even starts: PDF, JPG or PNG only, 10 MB cap matching Finmo's published limit, zero byte files rejected with an actionable message. The demo control that forces the next upload to fail exists so the failure path can be shown off, because handling failure well is the feature.

## MO prefill: propose, then approve

Step one offers to read the certificate of incorporation and prefill the business fields. Every prefilled value gets a visible MO suggested chip, editing a field removes the chip, and nothing submits until the human reviews it. This is the trust pattern from the report applied to onboarding: the AI proposes, the person approves, and the system learns. It is also the cheapest possible demonstration of the role one liner, making the AI trustworthy enough that users say yes to what it proposes, because the first yes a customer ever gives Finmo is on their own company data.

## Country packs, not hardcoded assumptions

My test account defaulted to AUD wallets and asked a US user for an ABN. So localization here is structural: a single config object per country drives the home currency, the registration number label and hint (UEN, EIN, ABN, Companies House number, BR number, trade licence), which certificate is requested, whether a state field exists, the local account details format, and the payment rails with their fees and speeds. Adding a jurisdiction is adding data, not code. The country is chosen once at signup and everything downstream inherits it.

## Ask only for what the application needs

The document list is computed, not fixed. A holding company triggers an ownership chart requirement, announced at the moment the user selects the entity type rather than sprung at the document step. The people step enforces the standard banks use: every director listed, every individual at 25 percent or more, adults only, ownership that cannot exceed 100 percent. If no one crosses 25 percent, a checkbox captures the control person fallback instead of blocking the application, which is the real FinCEN and MAS pattern.

## The platform side

Navigation is in money words, Home, Accounts, Pay, Get paid, FX, exactly as the report argues. Wallet plumbing stays invisible. Treasury appears as three ambient tiles on Home, burn, bills due, FX exposure, and each tile ends in a button that starts a payment or a conversion, because doors convert into each other and insights should end in actions.

On approval the account seeds with clearly labeled demo data, one payin, three invoices, three upcoming bills. This is the no empty state dead ends principle from the 90 day plan; a new user should never meet a blank product. The balance card carries a data as of stamp, a quiet nod to the stale balance finding, the number tells you how fresh it is, not just when it was asked for.

Payments intelligence follows propose, approve, execute. A payout to the same payee for the same amount trips a duplicate check that requires an explicit acknowledgment before send. A payment over 60 percent of balance gets a second approver note, showing where the approval matrix plugs in. Rail selection shows cost against speed side by side instead of burying it. On the receivables side, MO matches an incoming payin to an open invoice and asks for one click confirmation, and overdue invoices get a drafted nudge the user approves. When a payment sends, the balance, the activity feed and the burn tile all move at once, which is the one ledger argument made visible.

AskMO ships with four curated prompts that are guaranteed to answer from the same state the dashboard renders, because the marquee prompt failing was one of the sharpest findings. Anything it cannot answer gets a graceful boundary, not a hallucination. There is one MO entry point, no agent picker, routing is the product's job.

## Edge cases covered

Invalid email, short password, wrong verification code with resend, future incorporation dates, minors as directors, ownership over 100 percent, no qualifying UBO, unsupported file types, oversized files, empty files, upload failure with retry, refresh mid wizard, back navigation without data loss, double submit guard on the application, insufficient balance on payouts, duplicate payouts, locked features with stated reasons instead of hidden ones, and a full reset.

## Deliberately out of scope

Real authentication, real document OCR, real registry and sanctions checks, multi currency wallets, user roles and approval chains, and bank connections. Each has a marked seam: the upload engine swaps its fake timer for presigned URLs plus an async verification vendor behind a provider interface, the prefill swaps for a real extraction service returning the same field plus confidence shape, the review machine swaps timers for case management webhooks, the rails config swaps for a quoting API.

## What I would measure

Instrument the seams this prototype already exposes: completion rate per wizard step and where people drop, time from signup to submitted and submitted to approved, document failure rate by reason, share of applications that hit an action_needed pause and how fast they recover, time to first payment after approval, and the acceptance rate of every MO proposal, prefill fields kept versus edited, matches confirmed, duplicate warnings heeded. That last family is the number the whole AI thesis lives on.

# Round 2, Akhil's scope expansion

His asks, verbatim in spirit: individuals and businesses both, AI checks while the user types, sanctions behind the scenes with a KYC report to the team, instant approval with limits when risk is low, JPM collection accounts, Wise style roles, payment links, card top up with a fee, cards on the expense route, Synthesys treasury with daily yield, FX and payout screens like Brex, collections as the invoice module and payouts as bill pay.

## Two doors inside Door 1

Signup now opens with a choice: business account, or personal under the Finmo Remit brand (remit.finmo.net). The split happens at signup because everything downstream differs, KYB collects the entity, its people and its documents, KYC collects one person, one ID, one selfie. Both share the same wizard shell, upload engine, screening pipeline and risk engine, which is the point: a new business line reuses the whole verification stack, only the step definitions change. In code that is two arrays of steps over one machine, in production that is a product config, not a new codebase.

## Checks that run while you type

Three live checks ship in the prototype. Registration number format validates against per country rules the moment it is typed. The website is matched against the business description with a visible pass or a soft warning, soft because a mismatch is signal for the risk score, not proof of fraud, and blocking on a heuristic would burn good customers. A PO Box in the address field is rejected inline and each attempt is counted into the risk score, because regulators require a physical address and because attempting one repeatedly is itself signal. The checks live in a debounced panel that updates as you type without stealing focus. The principle: catch at the field what used to be caught days later by an analyst, and let nothing surprising happen at submit.

## Sanctions in the background, report to the team

Each person is screened the moment their card is saved, with a quiet status chip: screening, clear, or possible match. On submit MO assembles the full report, signal by signal with pass or flag, a numeric score and the outcome, and the applicant can open the exact report the compliance team receives. Showing the customer their own file is a trust decision borrowed from nowhere, most platforms hide it, but if the AI decides in seconds the customer deserves to see why.

## Instant approval with limits

The application is scored, threshold at 30. Below it, the account opens immediately with starter limits, 5,000 per transfer and 10,000 per month for businesses, tighter for individuals, cards held back until full approval. Above it, or on any sanctions flag, the file routes to the manual review tracker from round 1, with the same pause and resume document requests. The two paths share one state machine, approved_limited is just a state between submitted and approved. The team clears limits within 1 to 2 days, simulated with a timer and a demo button. This is the exact economics Akhil described: low risk customers transact in minute one, the human review happens in parallel instead of in front.

## Collection accounts through J.P. Morgan

Local virtual accounts in USD, CAD, GBP, EUR, HKD, AUD, SGD and NZD, each labeled as issued via J.P. Morgan, plus one SWIFT account receiving 35 currencies. Starter limits open the home currency account only, full approval opens the grid, which gives limit clearing a visible reward. PHP, IDR and THB are handled honestly as collect only: the payer pays local through a checkout page or the API, the customer is credited in USD, and the settlement note says so on the transaction itself. The rule that a currency can be collected but not held lives in one config list, adding a market touches data, not flows.

## Roles from Wise

Owner, Admin, Payer, Preparer, Viewer, with one line each describing what the job actually permits. Preparer is the quietly important one, prepare but not fund is the maker checker split that finance teams expect. Invites are by email with a pending state, the owner is unremovable and singular.

## Payment links, top up, cards

Payment links are the checkout page with a shareable name, amount optional, currency any of the eleven, and the collect only currencies visibly settle to USD. Card top up carries its 2.9% fee on the card charge with the fee shown before payment, never discovered after. Cards go the expense management route: virtual cards issued instantly with a monthly limit and an optional category lock, plastic on request with a shipping state, every spend auto categorised, missing receipts chased by MO. Cards are the one feature gated to full approval, card issuing is the highest risk surface in the product and gating it gives the starter tier a clean boundary.

## Treasury on the Synthesys Network

The treasury account opens with the business account, the Wise pattern, nothing to apply for, because the low risk money market products carry no extra onboarding burden. The fund list is drawn from the real Synthesys catalogue, Fidelity ILF, Franklin OnChain, WisdomTree WTGXX, Maybank SGD, Amundi EUR, Federated Hermes GBP, Conduit AUD, ChinaAMC HKD, with each fund's real minimum, settlement window and stablecoin 24/7 flag, and the 14:00 SGT cut off shown. Money moves only between the Finmo business account and treasury, no external transfers touch treasury, that is the safeguard and it is enforced in the transfer function, not just the copy. Higher risk funds, Apollo ACRED, Epoch Treasury Plus, tokenised gold, sit behind an explicit disclosure gate: three separate acknowledgments, value can fall, not deposit insured, risks accepted. Yield accrues and displays daily. Finmo is the sub distributor and keeps the ledger, the funds sit with the managers, and the UI says exactly that.

## Brex shaped money screens

Payouts is Bill Pay: an inbox of bills, upload one and MO extracts vendor, amount and due date for approval, plus a one off payout flow with source currency selection, cross currency delivery quoted with the mid rate and the itemised 0.5% margin, and the duplicate and large payment checks from round 1. Collections is the invoice module: invoice list with statuses and nudges, MO payin matching, payment links, and the local collection details one click away. FX is a proper convert screen with held currency sources, quote breakdown and the exposure alert on top.

# Round 3, FX risk and VaR on the business account

Akhil's framing: the full risk engine belongs in the cash tools bit, but VaR on the business account using Finmo FX would be great, and look at how Xflow does FX in a payments platform. Xflow's FX AI Analyst pattern is rate insight in plain money terms plus target triggers that execute automatically, convert with insight, not instinct.

## Where it lives and why

Inside the FX tab, business accounts only, plus a home tile that shows the live VaR number and deep links in. No new nav item, risk is a property of the money you already hold, not a separate product to visit. The individual remit account keeps a plain converter, a person sending family support does not need a VaR surface.

## The exposure model is the ledger

Exposure comes from what the platform already knows: foreign currency balances, plus, on a toggle, unpaid foreign currency receivables. That is the customer P&L angle from the chat, no data entry, no uploads, the ledger is the risk input. Netting falls out naturally because exposures are signed sums per currency. Bills are home currency in the prototype and therefore no offset, in production payables in foreign currency would enter with a negative sign through the same function.

## The engine, and the toggles Akhil asked for

A pure function takes an exposure map and parameters and returns VaR, per currency components and portfolio sigma. Toggles: confidence 90, 95, 99, horizon 1 day, 1 week, 1 month with square root of time scaling, method parametric or Monte Carlo, and exposure basis balances only or balances plus expected flows. Parametric is variance covariance with representative annualised vols per currency and a single 0.45 correlation factor. Monte Carlo runs 4,000 one factor paths on a seeded generator, deterministic on purpose so a demo never shows two numbers for one question. Component VaR uses the standard marginal decomposition and sums exactly to the total, which the tests assert. The engine is deliberately UI free so the cash tools bit later gets the same functions with a covariance provider swapped in, production feeds daily market data and backtests against the customer's own history, and the model note in the UI says precisely that. Historical simulation was left out knowingly, faking a return history would undermine credibility with the one person who linked a real risk engine.

## Plain words first

The headline is not a Greek letter, it is: on a bad day for the currencies you hold, 1 in 20 odds, FX could cost you up to this amount this week, a model estimate, not a promise. Below it, per currency contribution bars against their exposures, scenario chips for instant P&L under USD minus 2 percent or all foreign minus 5 percent, and the full parameter row for anyone who wants to interrogate the model. Door 1 tone with Door 2 machinery underneath.

## Closing the loop, the Xflow borrow

The number ends in a button, as every insight in this product should. MO names the currency driving most of the risk, quotes what converting half of it does to the VaR, and offers two actions: convert now, which loads the converter, or arm a target rate trigger that fires automatically when the rate improves half a percent, the Xflow limit order pattern. Triggers persist, show armed, executed or failed states, fail loudly when the balance is short, and can be cancelled. Propose, approve, execute, learn, now applied to risk.

## Edge cases

Zero exposure renders an explanatory empty state with a sample exposure loader for demos, VaR under one unit of currency reads as negligible instead of shouting false precision, the pegged HKD carries an appropriately odd vol, parameters persist across sessions, Monte Carlo is reproducible, component VaR is asserted to sum to the total, and the trigger that cannot fund itself fails with a reason instead of silently dying, which by now is the house rule.

# Round 4, navigation and the production companion

## Options with sub-options

The sidebar now follows the current dashboard's format: parent options that expand into sub-options. Home, Accounts (balances and details, top up), Payments (send a payout, bills, FX and risk), Collections (invoices, payment links), Cards (your cards, spend), then Treasury and Team as single items. The grouping keeps the money words rule, each parent is a thing you do with money, each child is a specific surface. Parents expand and collapse, the group holding the active screen opens itself, locked children show their lock at the child level so the reason stays visible instead of hiding a whole section. The remit account keeps a flat three item nav on purpose, a personal remittance product with grouped navigation would be dressing a studio apartment as a house.

## The production companion

PROD_IMPLEMENTATION.md now sits beside this file. Division of labour between the two: this document defends why each choice was made, that one proves each choice ships on Finmo's stack, AWS, a mix of databases picked per workload, and Bedrock for the AI, with the AI treated in the most depth. The short version of its argument: one MO runtime in front of Bedrock with a typed tool registry, proposals instead of actions everywhere money moves, deterministic decisions with AI in assembly and language roles, and provider interfaces plus configuration everywhere a partner or a market could change. The demo's AI is ambitious as product and conservative as engineering, which is the point.
