<!-- Synthetic sample document, written for a RAG take-home assignment.
     Northbay Commerce AI is a fictional company, and this case study is
     entirely fictional. It does not describe any real company, retailer,
     or business outcome. -->

# Case Study — Regional Apparel Retailer

## Customer profile

A mid-sized apparel retailer operating around 140 stores plus an
e-commerce channel, referred to here as "the retailer" at the customer's
request. The retailer's merchandising team was manually reviewing
markdown timing across roughly 3,000 active SKUs per season, a process
that consumed two merchandisers' time for most of each month.

## The problem

Markdown decisions were being made from a weekly spreadsheet export,
updated by hand, with no systematic way to flag which SKUs were falling
behind their sell-through curve early enough to act on. Markdowns were
frequently triggered later than the historical data justified, eroding
margin on slow-moving inventory that could have been discounted sooner
and sold through at a better recovered rate.

## The engagement

The retailer started on Northbay's Growth tier, deploying the Markdown
Timing Agent from the merchandising template category, connected to their
existing Snowflake sell-through data warehouse. An embedded FDE spent the
first two weeks in discovery, shadowing the merchandising team's existing
manual process before configuring the agent.

## What changed

The Markdown Timing Agent now flags SKUs falling behind their expected
sell-through curve on a daily basis rather than a weekly manual review,
and proposes a markdown percentage and timing based on the historical
curve for similar SKUs in the same category. Recommendations route through
an approval gate to the merchandising team before any price change takes
effect — the agent proposes, a human still approves.

## Outcome

Within the first two full seasons on the platform, the retailer reported
markdown decisions being made an average of 9 days earlier than their
prior manual process, and estimated a 3.2 percentage point improvement in
margin recovered on markdown inventory compared to the prior year's
comparable season. The two merchandisers previously doing manual markdown
review were reallocated to assortment planning work.

## What the retailer said

"We weren't looking to replace the judgment of our merchandising team —
we were looking to stop losing margin because a spreadsheet update was
three days late. That's exactly what changed."
