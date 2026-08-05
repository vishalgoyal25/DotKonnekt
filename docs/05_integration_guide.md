<!-- Synthetic sample document, written for a RAG take-home assignment.
     Northbay Commerce AI is a fictional company. No factual claims here
     describe any real organization. -->

# Northbay Commerce AI — Integration Guide

This document describes how Northbay Studio connects to a customer's
existing systems. It is intended for the technical team standing up a new
Northbay deployment, typically working alongside an assigned
Forward-Deployed Engineer.

## Supported connectors

Northbay ships first-party connectors for the systems retail and consumer
companies most commonly run:

- **Commerce platforms:** Shopify Plus, Salesforce Commerce Cloud, and
  Adobe Commerce (Magento).
- **CRM and support:** Salesforce Service Cloud and Zendesk.
- **Data warehouses:** Snowflake and BigQuery.
- **Messaging:** Slack and Microsoft Teams, used for agent notifications
  and human-in-the-loop approvals.

Each connector is versioned independently of the core platform. As of this
document, the current connector versions are:

| Connector | Current version |
|---|---|
| Shopify Plus connector | `nb-connect-shopify` v4.2 |
| Salesforce Service Cloud connector | `nb-connect-sfsc` v3.1 |
| Snowflake connector | `nb-connect-snowflake` v2.8 |
| Slack connector | `nb-connect-slack` v1.9 |

## Authentication

All connectors authenticate using OAuth 2.0 where the target system
supports it. For systems that do not (some on-premise data warehouses),
Northbay falls back to scoped API keys stored in the customer's own secrets
manager — Northbay never stores a customer's third-party credentials
directly.

## The `NB-Sync` protocol

Data flowing from a connected system into a Northbay agent's context passes
through an internal sync layer called **NB-Sync**. NB-Sync batches updates
every 15 minutes by default for high-volume sources (order data, ticket
queues) and syncs near-real-time for low-volume, high-priority sources
(inventory stockout alerts). The sync interval is configurable per
connector inside Studio's Data Sources panel.

## Adding a custom connector

If a customer's system has no first-party connector, Northbay supports a
custom REST or webhook-based integration through the **Connector SDK**.
Building a custom connector typically takes a Forward-Deployed Engineer two
to four business days, depending on the target system's API design and
whether it supports webhooks (push) or requires polling (pull).

## Common integration failure points

The most frequent cause of a stalled integration is a mismatch between the
customer's data schema and the field mapping Northbay expects — for
example, a commerce platform that stores SKU and variant ID as a single
composite string rather than two separate fields. The FDE assigned to the
deployment resolves this during the mapping step, before any agent goes
live against the connected system.
