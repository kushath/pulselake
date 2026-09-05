# PulseLake

Production-grade e-commerce data platform portfolio project.

## Milestone 0/1 status

This repository currently contains the **system specification**, **event contracts**, **source data model** and a **deterministic synthetic event generator**. The next milestone adds PostgreSQL + Kafka ingestion.

## Project goal

PulseLake simulates the data platform behind a multi-country European e-commerce business ("PulseMart"). It is designed to demonstrate production-style data engineering rather than a notebook-only project.

Target architecture:

```text
PostgreSQL + Event Producers
            |
            v
           Kafka
            |
            v
        Bronze / S3
            |
            v
        PySpark
            |
            v
          Silver
            |
            v
           dbt
            |
            v
           Gold
            |
            +--> Athena / Redshift
            |
            +--> Power BI

Airflow orchestrates batch workflows.
Docker provides a reproducible local environment.
Terraform defines the AWS environment.
GitHub Actions validates code, SQL, dbt and Terraform.
```

## Quick start

Python 3.11+:

```bash
python -m src.pulselake.generator --events 1000 --seed 42 --output data/sample/events.jsonl
```

Run tests:

```bash
python -m unittest discover -s tests -v
```

## Design principles

1. Every technology must solve a real system problem.
2. CV claims are published only after they are measured.
3. Bad data and failure scenarios are intentionally simulated.
4. Local development should cost €0.
5. Cloud resources are ephemeral and reproducible through IaC.
6. Recruiters must be able to verify the project from GitHub.

## Roadmap

- [x] M0: system specification and contracts
- [x] M1a: deterministic event generator
- [ ] M1b: transactional PostgreSQL source
- [ ] M2: Kafka event streaming
- [ ] M3: Bronze object-store ingestion
- [ ] M4: PySpark Silver transformations
- [ ] M5: dbt Gold dimensional models
- [ ] M6: Airflow orchestration
- [ ] M7: data-quality gates
- [ ] M8: AWS/Terraform deployment
- [ ] M9: observability + benchmark suite
- [ ] M10: Power BI executive dashboard
