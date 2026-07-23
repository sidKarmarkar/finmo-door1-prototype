# Arnab call — prep (private)

Monday, with Arnab Deb, VP Product at Finmo, Singapore. This is not shared. It is my own prep so I walk in fluent in the architecture and his world.

## Who he is

VP of Product at Finmo, based in Singapore. Ex **Kristal.AI** (Akhil said "Crystal", it is Kristal, a Singapore digital private-wealth platform serving HNIs and family offices with investment products). Before that, structured deals at **Barclays** in London after his MBA at **IIM Bangalore**. So his instincts are capital markets: forwards, swaps, structured products, yield, derivatives.

Akhil's framing on the call: "we'll be working very closely with him once everything goes through." Translation: he is treating me as incoming, and Arnab is the product peer I would report alongside. This call is effectively the senior round. Get the name right, it is Kristal not Crystal.

Finmo recently got a Singapore capital-markets licence (a MAS CMS-type licence). That is what unlocks the yield products, FX hedging, and derivatives (forwards, swaps) Arnab now leads.

## The one thing to own: two products, one thesis

- **Business account** — what I built. Regulated, needs KYB, moves money (collect, hold, payout). Akhil's exact words: this is the *cash cow*, the money-making business.
- **Cash tools** — Arnab's product. Unregulated data layer. Connect external banks and ERPs (Xero, QuickBooks, NetSuite, SAP), aggregate into one cash-flow view, categorise transactions, multi-entity balances, forecasting (needs ~6 months of data).

The thesis that binds them, say it in one line: **the data layer reads everything you do and turns it into specific reasons to run more money through the account.** Airwallex and Revolut sell the account and stop. Finmo wraps it in a data layer that drives it. My role, AI Payments PM, lives exactly at that seam.

## Where my prototype already proves it (lead with this)

I do not need to claim I built cash tools. I built the *business account*, and it already demonstrates the seam Arnab's data layer feeds into:

- **Insights tab** (new): connect external accounts, and it surfaces the exact nudges Akhil described, wire-to-local savings, FX-versus-mid-market savings, an FX hedge prompt, a liquidity-gap bridge, each ending in a business-account action with a number attached.
- **Saved with Finmo card**: FX margin avoided versus a bank, the "you'd have saved Y" insight made concrete.
- **FX VaR with hedge triggers**: the seed of the FX hedging program he leads.
- **SWIFT-versus-local rail choice**: the "use local instead of wire" nudge.
- **Synthesys treasury**: the tokenised-yield product the capital-markets licence unlocks.
- **Forecast drivers** (new): recurring flows with editable end-dates and instant what-if scenarios, plus honest confidence.

The line: "the account is what I built and it is the business. The data layer is what makes it smart. I have already wired the insight-to-action loop into the account, so the two products meet cleanly."

## Forecasting — have a real point of view

Akhil's points, which Arnab will share: forecasting is pattern-based, seasonality needs lots of data, a bad forecast with thin data burns trust, and the killer problem is a detected payroll being assumed to run forever when a contract actually ends in September. TMS platforms solve it by demanding contract documents; Finmo does not collect those.

My POV, the data ladder:
1. **Pattern detection** on transactions (the baseline).
2. **Editable end-dates and scenarios** per recurring flow. This is exactly their fix and it is now in my prototype, the compliance-vendor contract has an end date, and toggling it changes the forecast live. This is the cheap, honest answer to the contract problem without forcing document uploads: let the user tell the engine "this stops in September" transaction by transaction.
3. **AR/AP and contract dates** from the ERP, which is where Sourav's invoices feed in.
4. **Enough history** for seasonality.

The sharp point that will land with a capital-markets person: **distinguish statistical confidence from forecast confidence.** My VaR uses confidence levels legitimately, because FX exposure is a known distribution. A cash-flow forecast cannot claim a confidence percentage without data. So the honest move, and it is now in the prototype, is to flag low-confidence forecasts ("about 2 of 6 months of history, we will not put a false accuracy number on it") rather than bluff. That is both Akhil's "do not give a shitty forecast" principle and my no-silent-failures rule. Do not conflate the two confidences; showing I know they are different is the senior signal.

## His domain: FX hedging, yield, capital markets

This is Arnab's lead and it overlaps my role. Connect my work to it:
- My FX VaR quantifies exposure. The natural next step is a hedging *program*: forward contracts to lock a rate for a known future payable, which is exactly the derivatives the CMS licence enables. I can speak to the customer-facing side (propose a hedge, show the cost, approve, execute) while he owns the instrument side.
- Yield: my Synthesys treasury is the money-market entry. His capital-markets licence extends it to structured yield. Same "idle cash earns" story, deeper instruments.
- The mid-market comparison for FX savings can pull historic rates from an API like currencylayer, compute the delta against Finmo's 0.5%, and show what the customer would have saved. That is a concrete build I can describe.

## Questions to ask him (shows I think like a product peer)

- Where do you draw the line between what cash tools surfaces and what the business account executes? Who owns the handoff?
- For forecasting with thin data, do you prefer to withhold a number or show a wide honest band? I have opinions but want yours.
- With the CMS licence, what is the first hedging instrument you want to expose to customers, and how much of the pricing do we show versus abstract?
- How do you want to measure whether an insight actually drove account usage? That conversion metric feels like the core KPI for my role.

## What to avoid

- Do not claim I built cash tools. I built the account; I have opinions on the seam.
- Do not conflate VaR confidence with forecast confidence.
- Do not oversell the prototype as production. It is a clickable demonstration; the thinking is the point.
- Do not reopen comp. If it comes up, park it to writing and keep the call on product.

## Live-call copilot prompt (paste into the copilot before the call)

```
You are my live copilot for a video call with Arnab Deb, VP of Product at Finmo (Singapore), for the AI Payments PM role. I am Siddharth Karmarkar. Arnab is ex-Kristal.AI (Singapore private wealth, HNIs, family offices) and ex-Barclays structured products, IIM Bangalore MBA. He leads FX hedging, yield, and capital-markets products, newly unlocked by Finmo's Singapore CMS licence. Akhil (CPO) set up this call and treats me as incoming.

CONTEXT: Finmo has two products. Business account = regulated, KYB, moves money, the cash cow, which I built as a clickable prototype. Cash tools = unregulated data layer, connect external banks and ERPs, aggregate cash flow, forecast, which Arnab built. The strategy: the data layer drives business-account usage via AI insights. My prototype already demonstrates the seam (an Insights tab with wire-to-local and FX-savings nudges, a savings card, FX VaR with hedge triggers, treasury yield, and forecast drivers with editable end-dates and honest confidence).

MY GOALS: 1) show I own the two-product architecture, 2) show product judgment on forecasting and FX hedging, 3) build rapport with a future peer, 4) do not reopen comp.

HELP ME LIVE:
- If he asks a factual question about my build, surface the answer in under 8 words.
- If he goes deep on forecasting, remind me: data ladder (pattern, editable end-dates/scenarios, AR/AP + contract dates, then seasonality), and distinguish statistical VaR confidence from forecast confidence.
- If he goes deep on FX hedging, remind me: I own the customer-facing propose/approve/execute; he owns the instrument; forwards lock a rate for a known future payable.
- If he asks what I would build next, prompt: the mid-market FX-savings comparison (currencylayer historic rates vs Finmo's 0.5%) and a hedging program off the VaR.
- Flag if I over-explain; he is senior and terse-friendly.
- Never let me claim I built cash tools or conflate the two confidences.
- If he opens a door on timeline or next steps, prompt: TIMELINE MOMENT.

TONE: concise, product-fluent, peer-to-peer not candidate-to-panel.
```
