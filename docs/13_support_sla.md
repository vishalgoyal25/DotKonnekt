<!-- Synthetic sample document, written for a RAG take-home assignment.
     Northbay Commerce AI is a fictional company. No factual claims here
     describe any real organization. -->

# Northbay Commerce AI — Support & SLA Policy

## Support channels

Northbay offers support through three channels: the in-Studio help widget,
email, and — for Growth and Enterprise tier customers — a shared Slack
channel with the assigned account team.

## Response time targets by tier

| Tier | Standard request | Urgent (production-impacting) |
|---|---|---|
| Starter | 2 business days | 1 business day |
| Growth | 1 business day | 4 hours |
| Enterprise | 4 hours | 1 hour |

"Production-impacting" means an active agent has stopped functioning
correctly in a live customer deployment — not a configuration question or
a request for a new feature.

## Severity classification

Support requests are classified into three severities on intake:

- **Sev 1** — an agent is taking incorrect actions in production, or a
  connected data source has stopped syncing entirely. Sev 1 issues receive
  continuous engagement until resolved or mitigated.
- **Sev 2** — a feature is degraded but the deployment is otherwise
  functional (e.g. one connector is delayed but others are syncing
  normally).
- **Sev 3** — a question, configuration request, or minor issue with no
  immediate production impact.

## Escalation

If a response time target is missed, the request is automatically
escalated to the customer's account team lead. Enterprise customers with a
custom SLA (see the pricing document) have their escalation path defined
in their individual agreement rather than the standard table above.

## Support hours

Standard support channels are staffed during business hours in the
customer's contracted region (US Eastern, US Pacific, or Central European
time, matching the data residency region chosen at deployment). Sev 1
production issues are covered outside standard business hours for Growth
and Enterprise tier customers.

## What support does not cover

Support handles issues with the Northbay platform itself — agent
execution, connector behavior, Studio functionality. Requests to build new
custom connectors or new agent templates are handled through the
Integration & Governance or Agentic AI Development services described in
the service catalogue, not through the standard support channel.
