from __future__ import annotations

import argparse
import json
import os

from confluent_kafka import Producer

from pulselake.streaming.events import (
    load_order_events,
    load_payment_events,
)


DEFAULT_BOOTSTRAP_SERVERS = "127.0.0.1:19092"

TOPICS = {
    "orders": "pulselake.orders",
    "payments": "pulselake.payments",
}


def create_producer() -> Producer:
    return Producer(
        {
            "bootstrap.servers": os.getenv(
                "KAFKA_BOOTSTRAP_SERVERS",
                DEFAULT_BOOTSTRAP_SERVERS,
            ),
            "client.id": "pulselake-python-producer",
            "acks": "all",
            "enable.idempotence": True,
        }
    )


def delivery_report(err, msg) -> None:
    if err is not None:
        print(f"Delivery failed: {err}")
        return

    print(
        f"Delivered "
        f"{msg.topic()} "
        f"partition={msg.partition()} "
        f"offset={msg.offset()}"
    )


def publish_events(
    producer: Producer,
    topic: str,
    events: list[dict],
) -> None:
    for event in events:
        key = (
            event.get("order_id")
            or event.get("customer_id")
            or event["event_id"]
        )

        producer.produce(
            topic=topic,
            key=key.encode("utf-8"),
            value=json.dumps(
                event,
                separators=(",", ":"),
                sort_keys=True,
            ).encode("utf-8"),
            callback=delivery_report,
        )

        producer.poll(0)

    remaining = producer.flush(timeout=10)

    if remaining != 0:
        raise RuntimeError(
            f"{remaining} Kafka messages were not delivered."
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Publish PulseLake PostgreSQL entities to Kafka."
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum records per event type.",
    )

    args = parser.parse_args()

    producer = create_producer()

    order_events = load_order_events(args.limit)
    payment_events = load_payment_events(args.limit)

    print(f"Publishing {len(order_events)} order events...")
    publish_events(
        producer,
        TOPICS["orders"],
        order_events,
    )

    print(f"Publishing {len(payment_events)} payment events...")
    publish_events(
        producer,
        TOPICS["payments"],
        payment_events,
    )

    print("Publishing complete.")


if __name__ == "__main__":
    main()
