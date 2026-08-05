<!-- Synthetic sample document, written for a RAG take-home assignment.
     Northbay Commerce AI is a fictional company. No factual claims here
     describe any real organization. -->

# Northbay Commerce AI — Platform Overview

Northbay Commerce AI is a vertical AI execution platform built for retail and
consumer businesses. The platform is cloud-agnostic, model-agnostic, and
framework-agnostic: customers can run Northbay agents on AWS, Azure, or GCP,
route inference to whichever LLM provider fits their cost and latency needs,
and integrate with their existing orchestration stack rather than replacing
it.

The core product is called the **Northbay Studio**. It is the control plane
where customers configure agents, connect data sources, set governance
policies, and monitor agent activity in production. Studio is not a chatbot
builder — it is an execution layer, meaning every agent it runs is expected
to complete real business tasks (drafting a campaign brief, updating a
merchandising plan, resolving a support ticket) rather than only holding a
conversation.

## Why Northbay exists

Most retail enterprises can build an AI pilot. Very few can get that pilot
into production and keep it running reliably for a year. Northbay's founding
premise is that this gap — pilot to production — is an execution problem,
not a model-capability problem. The company was founded in 2021 by a team
with a combined background in retail operations and applied machine
learning, after observing the same failure pattern across a dozen retail AI
initiatives: a working demo, followed by a stalled rollout, followed by the
project being quietly shelved within eighteen months.

## The four pillars

1. **Northbay Studio** — the orchestration platform itself (see
   `05_integration_guide.md` for how it connects to customer systems, and
   `06_governance_observability.md` for how activity is monitored).
2. **Domain playbooks** — pre-built operational knowledge for retail and
   consumer verticals, encoded into the agents rather than left to prompt
   engineering per customer.
3. **Agentic templates** — ready-to-deploy agents for marketing,
   merchandising, customer experience (CX), and B2B sales (see
   `03_agentic_template_catalogue.md`).
4. **Forward-Deployed Engineers (FDEs)** — Northbay's own engineers are
   embedded with the customer's team during rollout, rather than handing
   over documentation and disappearing (see `04_embedded_engineering_model.md`).

## Who it's for

Northbay is built for mid-to-large retail and consumer goods companies —
typically organizations with an existing e-commerce or omnichannel
presence, an internal data team, and at least one prior AI pilot that did
not reach production. It is not aimed at very small businesses, which
Northbay's own sales team routes to lighter-weight, self-serve tools instead.
