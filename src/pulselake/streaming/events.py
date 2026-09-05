from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from pulselake.db import get_connection


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _event_id(event_type: str, entity_id: str) -> str:
    return str(
        uuid.uuid5(
            uuid.NAMESPACE_URL,
            f"pulselake:{event_type}:{entity_id}",
        )
    )


def _decimal(value: Decimal) -> float:
    return float(value)


def load_order_events(limit: int = 100) -> list[dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    o.order_id,
                    o.customer_id,
                    o.order_status,
                    o.currency,
                    o.order_value_eur,
                    o.created_at
                FROM orders o
                ORDER BY o.created_at, o.order_id
                LIMIT %s
                """,
                (limit,),
            )

            rows = cur.fetchall()

    events = []

    for (
        order_id,
        customer_id,
        order_status,
        currency,
        order_value_eur,
        created_at,
    ) in rows:
        events.append(
            {
                "event_id": _event_id("order_created", str(order_id)),
                "event_type": "order_created",
                "event_version": 1,
                "occurred_at": _iso(created_at),
                "customer_id": str(customer_id) if customer_id else None,
                "order_id": str(order_id),
                "order_status": order_status,
                "currency": currency.strip(),
                "order_value_eur": _decimal(order_value_eur),
            }
        )

    return events


def load_payment_events(limit: int = 100) -> list[dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    p.payment_id,
                    p.order_id,
                    o.customer_id,
                    p.amount_eur,
                    p.payment_method,
                    p.payment_status,
                    p.created_at
                FROM payments p
                JOIN orders o
                    ON o.order_id = p.order_id
                ORDER BY p.created_at, p.payment_id
                LIMIT %s
                """,
                (limit,),
            )

            rows = cur.fetchall()

    events = []

    for (
        payment_id,
        order_id,
        customer_id,
        amount_eur,
        payment_method,
        payment_status,
        created_at,
    ) in rows:
        event_type = (
            "payment_succeeded"
            if payment_status == "succeeded"
            else "payment_failed"
        )

        events.append(
            {
                "event_id": _event_id(event_type, str(payment_id)),
                "event_type": event_type,
                "event_version": 1,
                "occurred_at": _iso(created_at),
                "customer_id": str(customer_id) if customer_id else None,
                "order_id": str(order_id),
                "payment_id": str(payment_id),
                "amount_eur": _decimal(amount_eur),
                "payment_method": payment_method,
                "payment_status": payment_status,
            }
        )

    return events
