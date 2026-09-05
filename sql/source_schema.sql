CREATE TABLE customers (
    customer_id UUID PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    country CHAR(2) NOT NULL,
    city TEXT NOT NULL,
    segment TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE products (
    product_id UUID PRIMARY KEY,
    sku TEXT NOT NULL UNIQUE,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    unit_price_eur NUMERIC(12,2) NOT NULL CHECK (unit_price_eur >= 0),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE inventory (
    warehouse_id TEXT NOT NULL,
    product_id UUID NOT NULL REFERENCES products(product_id),
    quantity_on_hand INTEGER NOT NULL CHECK (quantity_on_hand >= 0),
    updated_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (warehouse_id, product_id)
);

CREATE TABLE orders (
    order_id UUID PRIMARY KEY,
    customer_id UUID REFERENCES customers(customer_id),
    order_status TEXT NOT NULL,
    currency CHAR(3) NOT NULL DEFAULT 'EUR',
    order_value_eur NUMERIC(12,2) NOT NULL CHECK (order_value_eur >= 0),
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE order_items (
    order_id UUID NOT NULL REFERENCES orders(order_id),
    product_id UUID NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price_eur NUMERIC(12,2) NOT NULL CHECK (unit_price_eur >= 0),
    PRIMARY KEY (order_id, product_id)
);

CREATE TABLE payments (
    payment_id UUID PRIMARY KEY,
    order_id UUID NOT NULL REFERENCES orders(order_id),
    amount_eur NUMERIC(12,2) NOT NULL CHECK (amount_eur >= 0),
    payment_method TEXT NOT NULL,
    payment_status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE refunds (
    refund_id UUID PRIMARY KEY,
    order_id UUID NOT NULL REFERENCES orders(order_id),
    payment_id UUID NOT NULL REFERENCES payments(payment_id),
    amount_eur NUMERIC(12,2) NOT NULL CHECK (amount_eur >= 0),
    reason TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL
);
