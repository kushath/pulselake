import unittest
import uuid

from pulselake.db import get_connection
from pulselake.streaming.events import (
    load_order_events,
    load_payment_events,
)


class StreamingEventTests(unittest.TestCase):
    def test_order_event_contract(self):
        events = load_order_events(limit=5)

        self.assertEqual(len(events), 5)

        required = {
            "event_id",
            "event_type",
            "event_version",
            "occurred_at",
            "customer_id",
            "order_id",
            "order_status",
            "currency",
            "order_value_eur",
        }

        for event in events:
            self.assertTrue(required.issubset(event))
            self.assertEqual(event["event_type"], "order_created")
            self.assertEqual(event["event_version"], 1)
            self.assertEqual(event["currency"], "EUR")
            self.assertGreaterEqual(event["order_value_eur"], 0)

            uuid.UUID(event["event_id"])
            uuid.UUID(event["order_id"])

            if event["customer_id"] is not None:
                uuid.UUID(event["customer_id"])

    def test_payment_event_contract(self):
        events = load_payment_events(limit=5)

        self.assertEqual(len(events), 5)

        required = {
            "event_id",
            "event_type",
            "event_version",
            "occurred_at",
            "customer_id",
            "order_id",
            "payment_id",
            "amount_eur",
            "payment_method",
            "payment_status",
        }

        for event in events:
            self.assertTrue(required.issubset(event))
            self.assertIn(
                event["event_type"],
                {"payment_succeeded", "payment_failed"},
            )
            self.assertEqual(event["event_version"], 1)
            self.assertGreaterEqual(event["amount_eur"], 0)

            uuid.UUID(event["event_id"])
            uuid.UUID(event["order_id"])
            uuid.UUID(event["payment_id"])

    def test_order_events_reference_existing_database_rows(self):
        events = load_order_events(limit=20)

        with get_connection() as conn:
            with conn.cursor() as cur:
                for event in events:
                    cur.execute(
                        """
                        SELECT COUNT(*)
                        FROM orders
                        WHERE order_id = %s
                          AND customer_id = %s
                        """,
                        (
                            event["order_id"],
                            event["customer_id"],
                        ),
                    )

                    self.assertEqual(
                        cur.fetchone()[0],
                        1,
                    )

    def test_payment_events_reference_existing_database_rows(self):
        events = load_payment_events(limit=20)

        with get_connection() as conn:
            with conn.cursor() as cur:
                for event in events:
                    cur.execute(
                        """
                        SELECT COUNT(*)
                        FROM payments
                        WHERE payment_id = %s
                          AND order_id = %s
                        """,
                        (
                            event["payment_id"],
                            event["order_id"],
                        ),
                    )

                    self.assertEqual(
                        cur.fetchone()[0],
                        1,
                    )

    def test_order_event_generation_is_deterministic(self):
        first = load_order_events(limit=10)
        second = load_order_events(limit=10)

        self.assertEqual(first, second)

    def test_payment_event_generation_is_deterministic(self):
        first = load_payment_events(limit=10)
        second = load_payment_events(limit=10)

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
