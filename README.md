# Finmo Door 1 prototype

A clickable, single-file prototype of Finmo's **Door 1** journey: from signup to using the platform, for both **businesses** and **individuals** (Finmo Remit). Built as a take-home for the AI Payments PM role, in response to Akhil's brief to build Door 1 with a best-in-class KYB flow modeled on Brex, that pauses and asks for documents when needed.

**Live demo:** _(GitHub Pages URL appears here once deployed)_

## What's inside

- **`index.html`** — landing page (the Pages entry point).
- **`finmo-door1-prototype.html`** — the prototype. One file, no build, no network, no dependencies. All data is fake and lives only in your browser (localStorage), so progress survives a refresh and a full reset is one click.
- **`DESIGN_DECISIONS.md`** — every design choice and its defense, edge cases, and where each simulated seam swaps for production. Rendered for the web as **`design-decisions.html`**.
- **`PROD_IMPLEMENTATION.md`** — how the demo ships on Finmo's stack (AWS, polyglot databases, Bedrock), focused on the AI side, proving feasibility. Rendered for the web as **`production.html`**.
- **`build-docs.py`** — regenerates the two `.html` docs from the markdown source (`python3 build-docs.py`). Edit the `.md`, rerun, commit both.

## What it covers

- **Two doors, one engine** — business (KYB) and personal remit (KYC) over one wizard shell, screening pipeline and risk engine.
- **AI onboarding** — MO pre-fills from the uploaded certificate, live checks as you type (registration format, website vs description, PO-box rejection), background sanctions screening, a generated KYB/KYC report, and a risk score that yields **instant approval with starter limits** when low, or routes to a manual review that pauses and resumes on document upload.
- **Money** — payouts (Bill Pay), collections (invoices), payment links, JPM local accounts in 8 currencies plus SWIFT, PHP/IDR/THB collect-to-USD, card top-up with an itemized fee.
- **Cards** — virtual and physical on the expense-management route, auto-categorized spend, MO chasing receipts.
- **Treasury** — Synthesys tokenised money-market funds, daily yield, disclosure gate for higher-risk funds, movement only between the business account and treasury.
- **FX risk** — Value at Risk computed from your own ledger, toggleable parameters (confidence, horizon, method, exposure basis), scenario chips, and MO hedge proposals ending in a conversion or an auto-executing target-rate trigger.

## Try it in ~3 minutes

Use the dark **Demo controls** box (bottom-right):

1. **Signup** — keep Business, hit *Fill demo details*, continue; the verification code is shown in the banner.
2. **KYB** — on each step, *Fill this step with demo data*. Try uploading to see MO pre-fill; toggle *Make next upload fail* to see the loud failure + retry.
3. **Approval** — low risk approves instantly with starter limits; open *View the report*.
4. **Platform** — *Team clears limits now* unlocks everything; explore Payments, Collections, Cards, Treasury.
5. **FX risk** — *Load sample FX exposure*, then toggle the VaR parameters and arm a rate trigger.
6. **Other paths** — reset, then *Force a sanctions hit* for the manual-review path, or pick Finmo Remit at signup for the personal flow.

## Hosting

Deployed with **GitHub Pages** via GitHub Actions (`.github/workflows/deploy.yml`). On push to `main`, the workflow publishes the folder as a static site.

**One-time setup:** in the repo, go to **Settings → Pages → Build and deployment → Source → GitHub Actions**. The next push to `main` deploys automatically; the live URL then appears under the workflow run and in Settings → Pages.

## Notes

Prototype only — not production code, no real credentials, no real money movement. The accompanying docs describe the production path.
