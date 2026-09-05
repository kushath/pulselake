# ADR-002: Use Kafka for event streaming

## Status
Accepted for the portfolio architecture.

## Context
PulseMart produces high-frequency behavioural and transactional events that should be processed independently from the OLTP database.

## Decision
Use Kafka-compatible streaming locally and Kafka/MSK-compatible contracts in cloud demonstrations.

## Why
- replayable event log
- producer/consumer decoupling
- partition-based scaling
- realistic streaming semantics
- ability to demonstrate consumer offsets and idempotency

## Cost decision
Kafka is local by default. Managed cloud Kafka is optional and ephemeral to avoid an unnecessary always-on bill.
