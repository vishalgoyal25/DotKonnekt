<!-- Synthetic sample document, written for a RAG take-home assignment.
     Northbay Commerce AI is a fictional company. No factual claims here
     describe any real organization. -->

# Northbay Commerce AI — Deployment Options

Northbay Studio is cloud-agnostic by design. Customers are not locked into
a single infrastructure provider, and a customer's choice of cloud does not
change which Northbay features are available to them.

## Supported clouds

Northbay Studio deploys into a customer's own cloud account on:

- **Amazon Web Services (AWS)**
- **Microsoft Azure**
- **Google Cloud Platform (GCP)**

The platform runs inside the customer's own cloud account rather than a
shared Northbay-hosted environment. This is a deliberate choice: it means
the customer's data never leaves infrastructure they already control and
already have their own security policies applied to.

## Supported LLM providers

Northbay is also model-agnostic. Agents can route inference to any of the
following, configured per agent or per customer default:

- OpenAI
- Anthropic
- Google (Gemini)
- Any provider reachable through an OpenAI-compatible API endpoint,
  including self-hosted open-weight models

Switching a customer's default model provider is a configuration change
inside Studio, not a redeployment.

## Framework compatibility

For customers who already have an internal agent orchestration framework in
place, Northbay Studio can operate as a governance and observability layer
on top of it rather than replacing it outright — connecting to the
existing framework's execution logs rather than requiring the customer to
migrate their agents onto Northbay's own runtime.

## Provisioning timeline

A standard cloud deployment, once the customer has granted the required
cloud permissions, is typically provisioned within two business days. Most
of the elapsed time in a deployment's first month is spent on data source
connection and mapping (see the integration guide), not on the platform
provisioning itself.

## Sizing

Northbay Studio's compute footprint scales with the number of active
agents and the volume of data flowing through connected sources, not with
the size of the customer's overall business. A single-template pilot
deployment and a twelve-template enterprise deployment differ in scale by
roughly an order of magnitude in underlying compute, and this is reflected
in the customer's infrastructure cost, which is separate from the Northbay
service fee described in the pricing document.
