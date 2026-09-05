# PulseLake System Specification v0.1

## 1. Business context

PulseMart is a synthetic European e-commerce retailer operating in:

- France
- Germany
- Spain
- Italy
- Netherlands
- Belgium

The platform sells consumer products through web and mobile channels.

PulseLake is the analytical and operational data platform used to answer:

- What is net revenue by market, product and channel?
- Where is conversion deteriorating?
- Which products are trending?
- Which customers are becoming inactive?
- What is the refund rate by category and geography?
- Are payment failures increasing?
- What is customer lifetime value?
- What inventory is at risk of stock-out?

## 2. Non-functional targets

These are **engineering targets**, not CV claims until measured.

| Metric | Initial target |
|---|---:|
| Local synthetic event throughput | >= 5,000 events/sec |
| Streaming end-to-end p95 latency | < 10 sec |
| Duplicate-safe ingestion | Yes |
| Schema validation | 100% of events |
| Invalid record quarantine | Yes |
| Reproducible local environment | Single command |
| Reproducible cloud environment | Terraform |
| CI validation | Every pull request |
| Cloud idle cost | As close to €0 as possible |

## 3. Source systems

### Transactional PostgreSQL

Core source tables:

- customers
- products
- inventory
- orders
- order_items
- payments
- refunds

### Event stream

Kafka topics:

- pulselake.page_views
- pulselake.searches
- pulselake.cart_events
- pulselake.checkout_events
- pulselake.order_events
- pulselake.payment_events
- pulselake.inventory_events

### External API (later milestone)

Candidate source: marketing spend or exchange-rate feed.

## 4. Lakehouse zones

### Bronze

Immutable raw ingested records.

Goals:
- preserve original payload
- append-only
- ingestion metadata
- replay capability

### Silver

Validated and conformed records.

Goals:
- typed schemas
- deduplication
- standardized timestamps
- normalized identifiers
- bad records quarantined

### Gold

Business-ready analytical models.

Initial dimensional model:

Dimensions:
- dim_customer
- dim_product
- dim_date
- dim_location
- dim_channel

Facts:
- fact_orders
- fact_order_items
- fact_payments
- fact_refunds
- fact_sessions
- fact_inventory

## 5. Key business metrics

- Gross Merchandise Value (GMV)
- Net Revenue
- Average Order Value
- Conversion Rate
- Cart Abandonment Rate
- Payment Failure Rate
- Refund Rate
- Repeat Purchase Rate
- Revenue per Customer
- Customer Lifetime Value
- Inventory Turnover

## 6. Data quality rules

Examples:

- order_id must be unique within the canonical orders model
- payment amount cannot be negative
- currency must be EUR in v1
- event timestamp cannot be more than 24 hours in the future
- product_id must resolve to a known product
- order_item quantity must be > 0
- refund amount cannot exceed captured payment amount
- customer country must be one of the supported markets
- duplicate event_id values must not double-count business metrics

## 7. Failure scenarios that must be tested

1. Duplicate payment event
2. Malformed JSON event
3. Unknown product ID
4. Missing customer ID
5. Kafka consumer restart
6. Late-arriving order event
7. Out-of-order payment/order events
8. Schema version mismatch
9. Airflow task retry
10. Partial batch failure

## 8. Verification model

A recruiter/engineer should be able to verify PulseLake by:

1. inspecting source code and architecture decisions;
2. running the local demo;
3. checking green CI workflows;
4. inspecting automated test reports;
5. reproducing published benchmarks;
6. inspecting Terraform plans for cloud infrastructure;
7. viewing the dashboard/demo video;
8. reviewing tagged releases and commit history.

## 9. Cost policy

Default development happens locally.

AWS resources are used for reproducible demonstration and benchmarks, then destroyed.
No always-on managed Kafka or warehouse is required for the portfolio to remain verifiable.
