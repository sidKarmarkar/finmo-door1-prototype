# Production implementation

**Finmo Door 1 prototype — Siddharth Karmarkar**

The design document defends the choices. This one proves they ship. It maps every part of the prototype onto Finmo's existing stack: AWS hosting, a mix of databases chosen per workload, and Bedrock for AI. The AI side gets the most detail, because that is where the product thesis lives.

The claim is stronger than "feasible." Most of the demo is assembly of patterns that are already routine in production somewhere, and the parts that are not routine are deliberately fenced behind provider interfaces. The demo's AI is ambitious as product and conservative as engineering, which is the right place for a licensed institution to put its ambition.

---

## Architecture at a glance

One platform, organised as services around an event backbone, mirroring the loop: see, decide, move, learn.

- **Frontend.** React served from S3 behind CloudFront. The prototype's render functions become components; its single state object splits into server state and a client store.
- **Services.** API Gateway in front of ECS Fargate for the long-lived services (ledger, payments orchestration, MO runtime) and Lambda for the bursty ones (document processing, webhooks, checks).
- **Event backbone.** EventBridge. Every state transition in onboarding, payments, cards and treasury is an event. This is what makes each later feature a new consumer instead of a schema change.

### Data, chosen per workload

The rule that settles every future storage debate: **money truth lives in the Postgres journal; everything else is a projection that can be rebuilt from it.**

| Store | Holds |
|---|---|
| **Aurora Postgres** | Ledger as an append-only double-entry journal, with balances as materialised views. Accounts, invoices, bills, payouts, cards, treasury holdings. |
| **DynamoDB** | High-write, key-shaped state: onboarding aggregates, wizard progress (the demo's save-and-resume), idempotency keys, limit and usage counters, feature flags. |
| **S3** | Every uploaded document and generated report, immutable and versioned. |
| **OpenSearch** | Fuzzy search: counterparty names for matching, screening-list caches, transaction search. |
| **ElastiCache (Redis)** | FX rates and live quotes. |
| **Timestream** | Rate history for the risk engine. |

---

## The MO runtime

This is the most important decision in the document, so it comes first. **All AI goes through one internal service that fronts Bedrock. No product service calls Bedrock directly.** The runtime has four layers.

### Model routing

Bedrock with a routing table, not a single model. Nothing in Door 1 needs the largest models.

| Work | Model class | Why |
|---|---|---|
| Field extraction, categorisation, intent routing | Haiku | Milliseconds, fractions of a cent, high volume |
| Report narratives, match tie-breaks, AskMO chat | Sonnet | Judgement and language, lower volume |

Prompt caching is on for fixed system prompts. Provisioned throughput is bought only for the two user-facing synchronous paths, live checks and AskMO. Every call is logged with model id, prompt hash, token counts and latency, so cost per feature is a dashboard rather than an investigation.

### Tool registry

How MO touches the platform: a registry of typed tools, each an internal API with a JSON schema, a permission scope and an audit tag. Read tools are broad. **Write tools are narrow, and every one of them returns a proposal, not an action.** The model literally has no tool that moves money; it has tools that create proposals, which the product surfaces as the approval cards you see in the demo, and a human click converts a proposal into a command handled by deterministic services. The only standing exceptions are rules the human already approved, FX triggers and auto-categorisation, both writing to reversible or advisory state. A new AI capability is a new tool plus an evaluation set, no new architecture.

### Safety

Bedrock Guardrails plus our own: PII redaction before prompts leave the VPC; injection hardening on every path where input comes from customer documents or free text, where extracted text is treated as data and never concatenated into instructions; output-schema validation with one retry then a deterministic fallback; and a per-tool kill switch in AppConfig so any capability can be disabled without a deploy.

### Evaluation

What makes the AI shippable rather than demoable. Every capability has a golden set: labelled documents for extraction, labelled payin-invoice pairs for matching, labelled transactions for categorisation, a question bank for AskMO. CI runs the sets on every prompt or model change. Production corrections become new labels, which retune thresholds and few-shot exemplars weekly. The feedback loop the design doc promises is concretely this.

---

## Module mapping

Each row is short on purpose. The pattern, then where the AI sits.

### Onboarding

The application aggregate lives in DynamoDB; the process runs on Step Functions, one definition with the step list injected per product. Pause-and-resume is the built-in `waitForTaskToken` pattern: the execution parks when compliance requests a document and the upload webhook resumes it. Uploads are S3 presigned URLs, then a chain of virus scan, Textract for OCR, then MO extraction, with every document state in the demo driven by that chain and a dead-letter alarm enforcing the no-silent-failure rule.

*AI:* prefill is Textract plus a Haiku-class extraction call returning value and confidence per field against the country pack. Registration format and PO Box checks are deterministic, client and server side, because regex problems should not cost tokens. The website-versus-description check is one small model call returning match, mismatch or unclear with a reason. Extraction and single-question classification are the two most commoditised LLM tasks there are, and Textract plus Bedrock is AWS's own reference pattern.

### Screening, scoring and instant approval

Sanctions and PEP screening is a vendor integration behind a `ScreeningProvider` interface, called asynchronously on person-save, with an OpenSearch prescreen for the instant chip. The scorecard is deterministic and versioned, with weighted signals and reason codes, because MAS expects explainable onboarding and a model must not decide. Approval-with-limits is configuration: the limits object becomes a policy record, counters live in DynamoDB with atomic conditional writes, and clearing limits is one event.

*AI:* a Sonnet-class call assembles the analyst-facing narrative from the signal table, with every claim grounded in a signal id so it cannot invent facts. A future ML risk model slots in as one more signal with its own reason code; it does not replace the auditable frame.

### Accounts and collections

A partner-integration service owns the J.P. Morgan surface: virtual-account issuance, credit webhooks, and daily reconciliation against our journal, with breaks surfacing in an ops queue. Issuance is event-driven off the approval events, matching the demo's unlock moment. Collect-only currencies are a routing-table entry. `VirtualAccountProvider` is an interface, so a second issuer is an implementation, not a redesign.

### Payments

Payouts run as a saga on Step Functions (quote, pre-flight, debit, submit, confirm) with idempotency keys and compensating entries. Rail adapters implement one interface per rail family; the demo's rail picker becomes a pricing service. Bill ingestion reuses the onboarding document chain unchanged.

*AI:* detection is deterministic or statistical and cheap; language is where the model spends. Duplicate detection is a database query first, then embedding similarity on counterparty names to catch near-matches, with the model only writing the warning. Anomaly flags start as statistics against the customer's own history, each a scored signal, and a learned model can replace them later behind the same interface. A wrong block costs trust; a wrong explanation costs a reword.

### Approvals, tracking and savings

**Approvals** are a policy service plus a state machine on the payout saga. A payment above the tenant's threshold, or one created by a role without funding rights, is persisted as a pending authorisation instead of entering the debit leg, so nothing leaves the ledger until a second principal acts. Policy records (threshold, dual-approval flag, per-role rights) live in DynamoDB and are evaluated server side, never in the client, with separation of duties enforced as a rule that the approver principal cannot equal the preparer principal. Every decision writes an immutable audit row, which is what an auditor will ask for. Multi-step and per-amount approval chains are the same machine with more states, so the model extends without redesign.

**Tracking** is a projection over rail webhooks. Each payout carries a status timeline (submitted, checks passed, on rail, delivered) fed by adapter callbacks, with the arrival estimate produced per rail from published SLAs plus our own observed distribution, so the estimate improves as we accumulate history. Delay detection is a scheduled comparison of elapsed time against expected, which raises a customer-facing notification before support hears about it. No AI is required, though the delay explanation is a natural place for MO to write the sentence.

**Savings** is a read model over the same journal that already stores executed FX margin and rail fees. Each transaction records what was charged and the counterfactual (a configurable bank benchmark spread and wire fee, set per market and reviewed by finance rather than invented per tenant), and the dashboard sums the difference over the period alongside treasury yield accrued. The benchmark being configuration rather than a hardcoded number matters: the claim is only defensible if the assumption behind it can be updated, sourced and shown, which is why the method is displayed to the customer.

### Collections

Matching is candidate generation (SQL over open invoices), then ranking (embedding similarity plus amount and reference heuristics), then a model tie-break only for ambiguous pairs, landing as a proposal. Confirmations and rejections are labels. Auto-match above high confidence can be enabled per tenant later as a standing rule. Nudges are a Sonnet draft from invoice facts, queued for approval. Payment links need no AI, which is worth stating in a document about AI: knowing where not to spend a model is part of the argument.

### Cards

An issuer processor (Marqeta or Lithic class) behind a `CardProvider` interface, with authorisation webhooks into the journal in real time. Spend controls evaluate in the authorisation callback against policy records. Categorisation is MCC and merchant rules first, then embeddings against the tenant's corrected history, then a small model call for the long tail. Receipt chasing is an MO standing rule.

### Treasury

Finmo is sub-distributor; Synthesys holds the principal and client-money accounts. The consequence: our journal is the source of truth for customer positions, an omnibus network holding mapped to per-customer rows. That is why the only allowed movement is business account to treasury and back, enforced in the transfer service. The order service batches against the 14:00 SGT cutoff, tracks settlement per fund, and posts daily NAV and yield as journal entries so yesterday's interest is a real ledger line. The suitability gate stores each accepted disclosure with version and timestamp, immutable in S3, because when a fund has a bad quarter the evidence of informed consent is the product. AI here is thin on purpose: investment advice is a regulated act, so the idle-cash suggestion is a threshold rule with a model-written sentence.

### FX and VaR

The demo's engine ports almost line for line; the one upgrade is the covariance input. Rates stream into Redis for quoting and Timestream for history; a nightly job computes volatilities and correlations, and the engine takes a `CovarianceProvider` interface so the demo's representative numbers and production's estimated ones are two implementations of one signature. VaR runs on demand for the screen and nightly for the home tile and backtesting, where realised P&L is compared against the forecast band and the hit rate is shown to the customer. Triggers are standing orders evaluated against the rate stream, with balance pre-checks and loud failure. The cash-tools version widens the position sources to connected banks and forecast flows, which is exactly why the engine was built interface-free.

### Dashboard analytics

The Home metrics, received, paid out and net flow per period, awaiting collection with aging buckets, days sales outstanding, bills pending this month and cash cover, are read models over the journal: projections updated on payment and invoice events, cached in Redis with period cuts (day, month, year to date) precomputed, and a nightly job reconciling them against the ledger. DSO is receivables over billed sales in the standard form; aging buckets fall out of due dates; cash cover is balance over the trailing outflow rate. All of it is arithmetic per tenant, cheap enough to serve on every load. No AI is needed to compute any of it; MO's role is the sentence under the number and the follow-up it proposes, drafted reminders for the slowest payers through the same proposal pattern as everywhere else. New metrics are new projections over events that already exist, which is the analytics flexibility provision.

### AskMO

The conversational face of the runtime: intent routing on a small model, tool calls against the read registry, and the rule that any number in a response must come from a tool, not from generation. Curated prompts are registered against health checks, so a prompt whose backing service is degraded is swapped out before a customer can click it. That turns the failed-marquee-prompt finding into a structural impossibility.

---

## Cross-cutting

**Scale.** The ledger partitions by tenant and posts through an append-only journal, so read load goes to projections and caches while the write path stays narrow. Everything AI is asynchronous except live checks and chat, so Bedrock throughput is a queue-depth question, not an availability one. Step Functions and Lambda absorb onboarding and document spikes without capacity planning.

**Flexibility.** Provider interfaces for screening, virtual accounts, card issuing, acquiring, the fund network and market data, so every partner is swappable. Country packs, scorecards, limits, the fund catalogue and rail tables are configuration. The event backbone means a future lending product, a Door 2 forecaster or an accounting sync each subscribes to events that already exist.

**Compliance.** Data residency per region under the existing licence map; reproducible decisions and immutable documents for the audit trail; model risk handled by the deterministic scorecard frame with AI in assembly and language roles; human accountability preserved by the proposal pattern wherever money moves.

---

## Build sequence and honest risks

A credible order: the document chain and MO runtime first, since onboarding, bills and receipts all ride on it; then scored onboarding with limits; then JPM accounts and the payout saga; then matching and categorisation, the highest visible AI value per unit of effort; then cards, treasury, and the risk service. Each stage ships customer-visible value on its own.

The real risks are not the AI. They are partner timelines (JPM onboarding, the issuer processor, the Synthesys integration) and the operational load of reconciliation and compliance queues. Every AI component here is a pattern with public production precedent on Bedrock, and every one degrades to a manual path, because the manual path is what the proposal pattern falls back to by construction.
