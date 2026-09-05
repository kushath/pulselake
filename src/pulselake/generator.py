from __future__ import annotations

import argparse
import json
import random
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

COUNTRIES = ("FR", "DE", "ES", "IT", "NL", "BE")
CHANNELS = ("web", "mobile")
EVENT_TYPES = (
    "page_view",
    "search",
    "add_to_cart",
    "checkout_started",
    "order_created",
    "payment_attempted",
)

def _uuid(rng: random.Random) -> str:
    return str(uuid.UUID(int=rng.getrandbits(128), version=4))

def _payload(event_type: str, rng: random.Random) -> dict[str, Any]:
    product_id = _uuid(rng)

    if event_type == "page_view":
        return {
            "product_id": product_id,
            "page_type": "product",
            "referrer": rng.choice(["search", "homepage", "campaign", "direct"]),
        }
    if event_type == "search":
        return {
            "query": rng.choice(
                ["wireless headphones", "coffee machine", "running shoes", "smart watch"]
            ),
            "result_count": rng.randint(0, 120),
        }
    if event_type == "add_to_cart":
        return {
            "product_id": product_id,
            "quantity": rng.randint(1, 3),
            "unit_price_eur": round(rng.uniform(5, 450), 2),
        }
    if event_type == "checkout_started":
        return {
            "cart_id": _uuid(rng),
            "item_count": rng.randint(1, 8),
            "cart_value_eur": round(rng.uniform(15, 900), 2),
        }
    if event_type == "order_created":
        return {
            "order_id": _uuid(rng),
            "item_count": rng.randint(1, 8),
            "order_value_eur": round(rng.uniform(15, 900), 2),
        }
    if event_type == "payment_attempted":
        return {
            "payment_id": _uuid(rng),
            "order_id": _uuid(rng),
            "amount_eur": round(rng.uniform(15, 900), 2),
            "payment_method": rng.choice(["card", "paypal", "apple_pay"]),
            "status": rng.choices(
                ["authorized", "declined"], weights=[0.93, 0.07], k=1
            )[0],
        }
    raise ValueError(f"Unsupported event type: {event_type}")

def make_event(index: int, rng: random.Random, start_time: datetime) -> dict[str, Any]:
    event_type = rng.choices(
        EVENT_TYPES,
        weights=[45, 15, 16, 9, 8, 7],
        k=1,
    )[0]

    logged_in = rng.random() < 0.72

    return {
        "event_id": _uuid(rng),
        "event_type": event_type,
        "event_version": 1,
        "event_time": (start_time + timedelta(milliseconds=index * 25)).isoformat().replace("+00:00", "Z"),
        "producer": rng.choice(["pulsemart-web", "pulsemart-mobile"]),
        "session_id": _uuid(rng),
        "customer_id": _uuid(rng) if logged_in else None,
        "country": rng.choice(COUNTRIES),
        "channel": rng.choice(CHANNELS),
        "payload": _payload(event_type, rng),
    }

def generate(events: int, seed: int, output: Path) -> None:
    rng = random.Random(seed)
    start = datetime(2026, 9, 5, 10, 0, tzinfo=timezone.utc)
    output.parent.mkdir(parents=True, exist_ok=True)

    seen_event_ids: list[str] = []

    with output.open("w", encoding="utf-8") as fh:
        for i in range(events):
            event = make_event(i, rng, start)

            # Intentional data-quality injections for pipeline testing.
            # ~0.2% duplicate IDs and ~0.1% invalid countries.
            if seen_event_ids and rng.random() < 0.002:
                event["event_id"] = rng.choice(seen_event_ids)
            if rng.random() < 0.001:
                event["country"] = "XX"

            seen_event_ids.append(event["event_id"])
            fh.write(json.dumps(event, separators=(",", ":")) + "\n")

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic PulseLake events.")
    parser.add_argument("--events", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("data/sample/events.jsonl"))
    args = parser.parse_args()

    if args.events <= 0:
        raise SystemExit("--events must be > 0")

    generate(args.events, args.seed, args.output)
    print(f"Generated {args.events:,} events -> {args.output}")

if __name__ == "__main__":
    main()
