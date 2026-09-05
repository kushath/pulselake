from __future__ import annotations

import argparse
import random
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP

from pulselake.db import get_connection


COUNTRIES = ["FR", "DE", "ES", "IT", "NL", "BE"]
CITIES = {
    "FR": ["Paris", "Lyon", "Marseille", "Lille", "Bordeaux"],
    "DE": ["Berlin", "Munich", "Hamburg", "Cologne", "Frankfurt"],
    "ES": ["Madrid", "Barcelona", "Valencia", "Seville", "Bilbao"],
    "IT": ["Milan", "Rome", "Turin", "Bologna", "Florence"],
    "NL": ["Amsterdam", "Rotterdam", "Utrecht", "Eindhoven", "The Hague"],
    "BE": ["Brussels", "Antwerp", "Ghent", "Liege", "Bruges"],
}

SEGMENTS = ["consumer", "premium", "business"]
CATEGORIES = [
    "electronics",
    "home",
    "fashion",
    "beauty",
    "sports",
    "books",
    "toys",
    "grocery",
]

PAYMENT_METHODS = ["card", "paypal", "apple_pay", "google_pay"]
REFUND_REASONS = [
    "customer_return",
    "damaged_item",
    "wrong_item",
    "delivery_issue",
    "duplicate_charge",
]

WAREHOUSES = ["WH-FR-01", "WH-DE-01", "WH-NL-01"]

START_TIME = datetime(2026, 1, 1, 8, 0, tzinfo=timezone.utc)


def money(value: float | Decimal) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def deterministic_uuid(namespace: str, index: int, seed: int) -> uuid.UUID:
    return uuid.uuid5(
        uuid.NAMESPACE_URL,
        f"pulselake:{seed}:{namespace}:{index}",
    )


def clear_existing_data(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            TRUNCATE TABLE
                refunds,
                payments,
                order_items,
                orders,
                inventory,
                products,
                customers
            CASCADE
            """
        )


def seed_customers(conn, rng: random.Random, count: int, seed: int):
    rows = []

    for i in range(count):
        customer_id = deterministic_uuid("customer", i, seed)
        country = rng.choice(COUNTRIES)
        city = rng.choice(CITIES[country])
        segment = rng.choices(
            SEGMENTS,
            weights=[75, 18, 7],
            k=1,
        )[0]

        created_at = START_TIME + timedelta(
            days=rng.randint(0, 180),
            seconds=rng.randint(0, 86399),
        )

        updated_at = created_at + timedelta(
            days=rng.randint(0, 90),
            seconds=rng.randint(0, 86399),
        )

        rows.append(
            (
                customer_id,
                f"customer{i:05d}@pulsemart.example",
                country,
                city,
                segment,
                created_at,
                updated_at,
            )
        )

    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO customers (
                customer_id,
                email,
                country,
                city,
                segment,
                created_at,
                updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            rows,
        )

    return rows


def seed_products(conn, rng: random.Random, count: int, seed: int):
    rows = []

    for i in range(count):
        product_id = deterministic_uuid("product", i, seed)
        category = rng.choice(CATEGORIES)

        unit_price = money(
            rng.uniform(4.99, 799.99)
        )

        created_at = START_TIME + timedelta(
            days=rng.randint(0, 120),
            seconds=rng.randint(0, 86399),
        )

        updated_at = created_at + timedelta(
            days=rng.randint(0, 120),
            seconds=rng.randint(0, 86399),
        )

        active = rng.random() > 0.03

        rows.append(
            (
                product_id,
                f"SKU-{i:06d}",
                f"{category.title()} Product {i:04d}",
                category,
                unit_price,
                active,
                created_at,
                updated_at,
            )
        )

    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO products (
                product_id,
                sku,
                product_name,
                category,
                unit_price_eur,
                active,
                created_at,
                updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            rows,
        )

    return rows


def seed_inventory(conn, rng: random.Random, products):
    rows = []

    for warehouse_id in WAREHOUSES:
        for product in products:
            product_id = product[0]

            quantity = rng.randint(0, 500)

            updated_at = START_TIME + timedelta(
                days=rng.randint(150, 240),
                seconds=rng.randint(0, 86399),
            )

            rows.append(
                (
                    warehouse_id,
                    product_id,
                    quantity,
                    updated_at,
                )
            )

    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO inventory (
                warehouse_id,
                product_id,
                quantity_on_hand,
                updated_at
            )
            VALUES (%s, %s, %s, %s)
            """,
            rows,
        )

    return rows


def seed_orders(
    conn,
    rng: random.Random,
    customers,
    products,
    order_count: int,
    seed: int,
):
    order_rows = []
    item_rows = []
    payment_rows = []
    refund_rows = []

    customer_ids = [row[0] for row in customers]
    product_lookup = {
        row[0]: row[4]
        for row in products
        if row[5]
    }
    active_product_ids = list(product_lookup.keys())

    for i in range(order_count):
        order_id = deterministic_uuid("order", i, seed)
        customer_id = rng.choice(customer_ids)

        created_at = START_TIME + timedelta(
            days=rng.randint(181, 240),
            seconds=rng.randint(0, 86399),
        )

        item_count = rng.randint(1, 5)

        selected_products = rng.sample(
            active_product_ids,
            k=min(item_count, len(active_product_ids)),
        )

        order_total = Decimal("0.00")

        for product_id in selected_products:
            quantity = rng.randint(1, 4)
            unit_price = product_lookup[product_id]

            order_total += unit_price * quantity

            item_rows.append(
                (
                    order_id,
                    product_id,
                    quantity,
                    unit_price,
                )
            )

        order_total = money(order_total)

        payment_success = rng.random() < 0.94

        if payment_success:
            order_status = rng.choices(
                ["paid", "shipped", "delivered"],
                weights=[10, 25, 65],
                k=1,
            )[0]
        else:
            order_status = "payment_failed"

        updated_at = created_at + timedelta(
            hours=rng.randint(1, 96)
        )

        order_rows.append(
            (
                order_id,
                customer_id,
                order_status,
                "EUR",
                order_total,
                created_at,
                updated_at,
            )
        )

        payment_id = deterministic_uuid("payment", i, seed)

        payment_status = (
            "succeeded"
            if payment_success
            else "failed"
        )

        payment_created_at = created_at + timedelta(
            minutes=rng.randint(1, 20)
        )

        payment_rows.append(
            (
                payment_id,
                order_id,
                order_total,
                rng.choice(PAYMENT_METHODS),
                payment_status,
                payment_created_at,
            )
        )

        if payment_success and rng.random() < 0.05:
            refund_id = deterministic_uuid("refund", i, seed)

            refund_fraction = rng.choice(
                [
                    Decimal("0.25"),
                    Decimal("0.50"),
                    Decimal("1.00"),
                ]
            )

            refund_amount = money(
                order_total * refund_fraction
            )

            refund_created_at = payment_created_at + timedelta(
                days=rng.randint(1, 30)
            )

            refund_rows.append(
                (
                    refund_id,
                    order_id,
                    payment_id,
                    refund_amount,
                    rng.choice(REFUND_REASONS),
                    refund_created_at,
                )
            )

    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO orders (
                order_id,
                customer_id,
                order_status,
                currency,
                order_value_eur,
                created_at,
                updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            order_rows,
        )

        cur.executemany(
            """
            INSERT INTO order_items (
                order_id,
                product_id,
                quantity,
                unit_price_eur
            )
            VALUES (%s, %s, %s, %s)
            """,
            item_rows,
        )

        cur.executemany(
            """
            INSERT INTO payments (
                payment_id,
                order_id,
                amount_eur,
                payment_method,
                payment_status,
                created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            payment_rows,
        )

        cur.executemany(
            """
            INSERT INTO refunds (
                refund_id,
                order_id,
                payment_id,
                amount_eur,
                reason,
                created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            refund_rows,
        )

    return {
        "orders": len(order_rows),
        "order_items": len(item_rows),
        "payments": len(payment_rows),
        "refunds": len(refund_rows),
    }


def validate_seed(conn) -> None:
    checks = {
        "orphan_orders": """
            SELECT COUNT(*)
            FROM orders o
            LEFT JOIN customers c
                ON o.customer_id = c.customer_id
            WHERE c.customer_id IS NULL
        """,
        "orphan_order_items_orders": """
            SELECT COUNT(*)
            FROM order_items oi
            LEFT JOIN orders o
                ON oi.order_id = o.order_id
            WHERE o.order_id IS NULL
        """,
        "orphan_order_items_products": """
            SELECT COUNT(*)
            FROM order_items oi
            LEFT JOIN products p
                ON oi.product_id = p.product_id
            WHERE p.product_id IS NULL
        """,
        "orphan_payments": """
            SELECT COUNT(*)
            FROM payments p
            LEFT JOIN orders o
                ON p.order_id = o.order_id
            WHERE o.order_id IS NULL
        """,
        "orphan_refunds": """
            SELECT COUNT(*)
            FROM refunds r
            LEFT JOIN payments p
                ON r.payment_id = p.payment_id
            WHERE p.payment_id IS NULL
        """,
        "refund_exceeds_payment": """
            SELECT COUNT(*)
            FROM refunds r
            JOIN payments p
                ON r.payment_id = p.payment_id
            WHERE r.amount_eur > p.amount_eur
        """,
        "order_total_mismatch": """
            SELECT COUNT(*)
            FROM orders o
            JOIN (
                SELECT
                    order_id,
                    ROUND(
                        SUM(quantity * unit_price_eur),
                        2
                    ) AS calculated_total
                FROM order_items
                GROUP BY order_id
            ) oi
                ON o.order_id = oi.order_id
            WHERE o.order_value_eur <> oi.calculated_total
        """,
    }

    failures = {}

    with conn.cursor() as cur:
        for name, sql in checks.items():
            cur.execute(sql)
            value = cur.fetchone()[0]

            if value != 0:
                failures[name] = value

    if failures:
        raise RuntimeError(
            f"Seed validation failed: {failures}"
        )


def get_counts(conn):
    tables = [
        "customers",
        "products",
        "inventory",
        "orders",
        "order_items",
        "payments",
        "refunds",
    ]

    counts = {}

    with conn.cursor() as cur:
        for table in tables:
            cur.execute(
                f"SELECT COUNT(*) FROM {table}"
            )
            counts[table] = cur.fetchone()[0]

    return counts


def seed_database(
    seed: int,
    customers: int,
    products: int,
    orders: int,
):
    rng = random.Random(seed)

    with get_connection() as conn:
        clear_existing_data(conn)

        customer_rows = seed_customers(
            conn,
            rng,
            customers,
            seed,
        )

        product_rows = seed_products(
            conn,
            rng,
            products,
            seed,
        )

        seed_inventory(
            conn,
            rng,
            product_rows,
        )

        seed_orders(
            conn,
            rng,
            customer_rows,
            product_rows,
            orders,
            seed,
        )

        validate_seed(conn)

        counts = get_counts(conn)

        conn.commit()

    return counts


def parse_args():
    parser = argparse.ArgumentParser(
        description="Seed the PulseMart PostgreSQL source database."
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
    )

    parser.add_argument(
        "--customers",
        type=int,
        default=1000,
    )

    parser.add_argument(
        "--products",
        type=int,
        default=500,
    )

    parser.add_argument(
        "--orders",
        type=int,
        default=5000,
    )

    return parser.parse_args()


def main():
    args = parse_args()

    counts = seed_database(
        seed=args.seed,
        customers=args.customers,
        products=args.products,
        orders=args.orders,
    )

    print("PulseMart seed complete")
    print("-----------------------")

    for table, count in counts.items():
        print(f"{table:12} {count:,}")


if __name__ == "__main__":
    main()
