<!-- Synthetic sample document, written for a RAG take-home assignment.
     Northbay Commerce AI is a fictional company. No factual claims here
     describe any real organization. -->

# Northbay Commerce AI — Onboarding Runbook

This runbook describes the standard sequence for a new customer's first
30 days on Northbay, from contract signature through the first agent going
live.

## Step 1 — Kickoff call (day 1–3)

The customer's assigned account team and Forward-Deployed Engineer hold a
kickoff call with the customer's technical lead and executive sponsor.
This call confirms which cloud provider the deployment will use, which
data sources will be connected first, and which agentic template the
customer wants to pilot.

## Step 2 — Cloud access provisioning (day 2–5)

The customer grants Northbay Studio the required cloud permissions inside
their own account. This step runs in parallel with kickoff and typically
does not block it, since the FDE can begin discovery work before
provisioning completes.

## Step 3 — Data source connection (day 3–10)

The FDE connects the first one or two data sources agreed on during
kickoff, using the connectors described in the integration guide. This is
the step most likely to surface a schema mismatch requiring discussion
with the customer's data team before it can complete.

## Step 4 — Discovery shadowing (day 5–14)

The FDE observes the customer's existing manual process for the workflow
being automated, without yet configuring the agent. This step exists
specifically so the agent's initial configuration reflects how the
customer's team actually works, rather than an assumed best practice.

## Step 5 — Agent configuration (day 10–20)

The FDE configures the chosen agentic template, iterating with the
customer's team members who will use the agent day to day.

## Step 6 — Pilot run (day 15–30)

The agent runs alongside the existing manual process. Outputs are reviewed
by the customer's team but do not yet take effect automatically — this
overlaps with step 5, since configuration continues to be refined based on
pilot output.

## Step 7 — Go-live decision (around day 30)

The customer's executive sponsor and the FDE jointly decide whether to
relax the agent's approval gate and let it act with reduced human review,
extend the pilot period, or adjust the configuration further before
another pilot cycle. There is no fixed requirement to go live at exactly
30 days — the runbook's timeline is a default expectation, not a
contractual deadline.

## What can extend this timeline

The most common cause of onboarding running past 30 days is data source
connection taking longer than expected at step 3, usually due to a schema
mismatch of the kind described in the integration guide's troubleshooting
section.
