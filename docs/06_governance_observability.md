<!-- Synthetic sample document, written for a RAG take-home assignment.
     Northbay Commerce AI is a fictional company. No factual claims here
     describe any real organization. -->

# Northbay Commerce AI — Governance & Observability

Enterprises adopting agentic AI need to know what their agents are doing,
why they did it, and who can be held accountable when something goes wrong.
Northbay treats this as a first-class product requirement rather than an
afterthought bolted on after deployment.

## Watching what agents are doing

Every action a Northbay agent takes — a draft it produced, a record it
updated, a message it sent — is written to an activity feed inside Studio,
visible to the customer's own administrators in real time. Nothing an agent
does is invisible or delayed in reporting. Administrators can filter this
feed by agent, by time window, or by the specific customer system that was
touched, and can drill into any single action to see the reasoning the
agent produced leading up to it.

## Approval workflows

For actions Northbay classifies as higher-risk — sending an external
customer communication, changing a live price, or committing a
merchandising plan — the customer can configure a **human approval gate**.
When a gate is active, the agent prepares the action and pauses, and a
named human reviewer must approve or reject it before it takes effect.
Approval requests surface inside Slack or Teams, wherever the customer's
team already works, rather than requiring them to log into a separate
console.

## Auditability

Every agent decision carries a trace: which data sources were consulted,
which internal playbook or template guided the response, and which model
served the underlying inference call. This trace is retained for a
minimum of 12 months and can be exported for a customer's own internal or
regulatory audit. Northbay does not consider an agent's output trustworthy
by default — it considers it auditable by default, and trustworthy once a
customer has verified that audit trail matches their expectations.

## Data boundaries

Northbay agents only read and act on data sources the customer has
explicitly connected (see the integration guide). An agent configured for
the marketing team cannot silently reach into support-ticket data, even if
both data sources happen to sit in the same customer's account — access is
scoped per agent, not per customer.

## Oversight is a shared responsibility

Northbay's position is that governance tooling reduces risk but does not
eliminate the need for a human owner. Every customer deployment names an
internal executive sponsor who is accountable for the agents running in
their organization, and Northbay's own Forward-Deployed Engineers review
the audit trail with that sponsor on a recurring cadence during the first
quarter of any new deployment.
