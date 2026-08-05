<!-- Synthetic sample document, written for a RAG take-home assignment.
     Northbay Commerce AI is a fictional company, and this case study is
     entirely fictional. It does not describe any real company, product,
     or business outcome. -->

# Case Study — Consumer Packaged Goods Manufacturer

## Customer profile

A consumer packaged goods manufacturer selling household products through
both major retail partners and its own direct-to-consumer channel,
referred to here as "the manufacturer." Unlike the regional apparel
retailer described in the retail case study, the manufacturer's primary
challenge was on the B2B side of the business — managing renewal
conversations with its retail buying partners — rather than in
merchandising or CX.

## The problem

The manufacturer's B2B sales team managed roughly 200 active retail
partner accounts, and renewal risk was typically identified only when a
partner's order volume had already dropped noticeably — often too late in
the relationship to meaningfully change the outcome before the next
renewal decision.

## The engagement

The manufacturer deployed the Renewal Risk Agent from the B2B sales
template category on Northbay's Enterprise tier, connected to their CRM
and order management system. Because the manufacturer already ran an
internal orchestration framework for several existing tools, the
deployment used Northbay Studio primarily as a governance and
observability layer (see the deployment options document) rather than
migrating their broader agent stack onto Northbay's runtime.

## What changed

The Renewal Risk Agent monitors order volume trends across all active
partner accounts and flags accounts showing an early decline pattern,
well before the volume drop would have been noticed through the sales
team's existing quarterly account review process. Flagged accounts are
prioritized for the account team's attention, along with a summary of
which product lines are declining and any comparable pattern from past
accounts that later churned.

## Outcome — and a comparison to the retail case study

Where the retail case study's outcome was measured in margin recovered
on markdown timing, the manufacturer's outcome was measured differently:
in the two quarters following deployment, the manufacturer's account team
reported successfully re-engaging 11 of 14 flagged at-risk accounts before
their next renewal date, compared to an estimated 4 of roughly a similar
number of at-risk accounts identified (after the fact) in the prior year.
The manufacturer did not adopt any merchandising or CX templates during
this engagement, reflecting Northbay's general guidance that most
customers start with one or two templates in a single business function
rather than deploying broadly at once.

## What the manufacturer said

"The volume drop was always visible eventually. What we needed was to see
it while there was still time to have the conversation."
