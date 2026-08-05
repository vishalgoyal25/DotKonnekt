<!-- Synthetic sample document, written for a RAG take-home assignment.
     Northbay Commerce AI is a fictional company. No factual claims here
     describe any real organization. -->

# Northbay Commerce AI — Glossary & FAQ

## Glossary

**FDE** — Forward-Deployed Engineer. A Northbay engineer embedded with a
customer's team during rollout. See the embedded engineering model
document.

**Studio** — Short for Northbay Studio, the platform's control plane for
configuring agents, connecting data sources, and monitoring activity.

**NB-Sync** — Northbay's internal data synchronization layer, connecting
customer systems to Studio. See the integration guide.

**CX** — Customer experience. One of Northbay's four agentic template
categories, alongside marketing, merchandising, and B2B sales.

**RBAC** — Role-based access control. The access model customers use to
govern who can view or modify their Northbay deployment.

**Approval gate** — A configurable checkpoint requiring human review
before a higher-risk agent action takes effect, such as an external
customer communication or a live price change.

**RFP** — Request for proposal. Referenced in the B2B sales templates,
where the RFP Response Agent drafts a first-pass reply.

**SOC 2 Type II** — An independent audit certification covering security
controls over an extended period, which Northbay's platform holds and
renews annually.

**Executive sponsor** — The named individual on the customer's side
accountable for a Northbay deployment, referenced throughout the
governance and onboarding documents.

## Frequently asked questions

**Does Northbay replace our existing agent framework?**
No. Where a customer already has an internal orchestration framework,
Northbay Studio can run as a governance and observability layer on top of
it. See the deployment options document.

**Can we change our LLM provider after deployment?**
Yes. Switching a default model provider is a Studio configuration change,
not a redeployment.

**Do all customers get an embedded FDE?**
Starter tier does not include FDE time by default; Growth includes one FDE
engagement of up to 8 weeks; Enterprise includes a dedicated FDE embed for
the full engagement. See the pricing document.

**What happens to our data if we stop using Northbay?**
See the contract & trial terms document's section on data return upon
termination.

**Who approves an agent's higher-risk actions?**
Whichever human reviewer the customer names when configuring the approval
gate for that action type — this is set per agent, not fixed by Northbay.
