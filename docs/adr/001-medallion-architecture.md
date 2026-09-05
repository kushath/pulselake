# ADR-001: Use Bronze / Silver / Gold data layers

## Status
Accepted

## Context
PulseLake needs a clear separation between raw source fidelity, validated canonical data and business-facing analytics models.

## Decision
Use a three-zone medallion architecture:
- Bronze: immutable raw ingestion
- Silver: validated, typed, deduplicated data
- Gold: dimensional/business models

## Alternatives considered
- Single warehouse schema
- Raw + curated only

## Consequences
Benefits:
- replayability
- clearer quality boundaries
- easier debugging
- independent business modelling

Costs:
- additional storage
- more pipeline stages
- more operational complexity
