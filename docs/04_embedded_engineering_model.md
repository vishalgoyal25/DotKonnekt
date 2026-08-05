<!-- Synthetic sample document, written for a RAG take-home assignment.
     Northbay Commerce AI is a fictional company. No factual claims here
     describe any real organization. -->

# Northbay Commerce AI — Forward-Deployed Engineering Model

Northbay's Forward-Deployed Engineers (FDEs) are the mechanism the company
relies on to close the gap between a working pilot and a production
deployment the customer's own team trusts.

## What an FDE actually does

An FDE is not a project manager and not a pure support engineer. They write
code — adjusting agent configurations, building custom connectors,
debugging integration failures — while working from inside the customer's
own environment and, where practical, the customer's own tools (Slack,
Jira, whatever the team already uses). The intent is for the FDE to feel
like a temporary member of the customer's team, not an outside vendor
checking in periodically.

## Engagement phases

1. **Discovery (week 1–2)** — the FDE shadows the customer's existing
   workflow for the process being automated, before writing any
   configuration.
2. **Build (week 3–6)** — the FDE customizes the relevant agentic template,
   iterating directly with the team members who will use it.
3. **Pilot (week 7–10)** — the agent runs alongside the existing manual
   process, with outputs reviewed but not yet acted on automatically.
4. **Handover (week 11–14)** — approval gates are relaxed as trust builds,
   and the FDE begins training the customer's internal team to maintain
   the deployment without the FDE present.

Timelines vary by the complexity of the process being automated; a single
well-scoped CX template can complete all four phases in under ten weeks,
while a multi-system merchandising deployment can run considerably longer.

## When an FDE engagement ends

Northbay's stated goal is for every FDE engagement to end with an internal
handover, not an indefinite embed. An FDE's engagement is considered
complete when the customer's own team can make configuration changes to
the deployed agent without escalating to Northbay. In practice this
handover point is judged jointly by the FDE and the customer's named
executive sponsor (see the governance and observability document), not by
a fixed calendar date alone.

## Working with existing customer teams

FDEs report to a Northbay engagement lead but work day-to-day under the
direction of whoever owns the automated process on the customer's side —
typically a marketing operations lead, a merchandising manager, or a CX
operations manager, depending on which function is being deployed into.
