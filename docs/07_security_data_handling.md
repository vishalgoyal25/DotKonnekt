<!-- Synthetic sample document, written for a RAG take-home assignment.
     Northbay Commerce AI is a fictional company. No factual claims here
     describe any real organization. -->

# Northbay Commerce AI — Security & Data Handling

## Data residency

Customer data processed by Northbay Studio stays within the cloud region
the customer selects at deployment time. Northbay currently supports
deployments in North America (US-East, US-West) and Europe (EU-Central).
Data does not move between regions once a deployment is provisioned,
including for backup or disaster-recovery purposes — backups are kept
within the same region as the primary deployment.

## Encryption

All customer data is encrypted at rest using AES-256 and in transit using
TLS 1.2 or higher. Encryption keys are managed through the customer's
chosen cloud provider's native key management service (AWS KMS, Azure Key
Vault, or Google Cloud KMS) rather than a Northbay-managed key store,
so the customer retains the ability to revoke access independently of
Northbay.

## Access control

Access to a customer's Northbay deployment is governed by role-based access
control (RBAC) configured by the customer's own administrators. Northbay
support staff do not have standing access to a customer's data or agent
configurations; temporary access for a support case must be explicitly
granted by the customer and expires automatically after 24 hours.

## Model training and data use

Customer data is never used to train or fine-tune any model on behalf of
another customer. Prompts and retrieved context sent to an underlying LLM
provider during agent execution are covered by that provider's zero
data-retention terms, which Northbay requires as a condition of adding any
inference provider to its supported list.

## Vulnerability disclosure

Northbay maintains a responsible disclosure program for security
researchers and commits to an initial response within five business days
of a report being submitted.

## Compliance certifications

Northbay's platform holds SOC 2 Type II certification, renewed annually.
Customers requiring additional compliance documentation (for example, a
signed data processing agreement for GDPR purposes) can request it through
their assigned account team.
