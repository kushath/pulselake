# Event Contracts v1

All events share a common envelope.

```json
{
  "event_id": "uuid",
  "event_type": "page_view",
  "event_version": 1,
  "event_time": "2026-09-05T10:00:00Z",
  "producer": "pulsemart-web",
  "session_id": "uuid",
  "customer_id": "optional uuid",
  "country": "FR",
  "channel": "web",
  "payload": {}
}
```

## Supported countries

`FR`, `DE`, `ES`, `IT`, `NL`, `BE`

## Supported channels

`web`, `mobile`

## page_view payload

```json
{
  "product_id": "uuid",
  "page_type": "product",
  "referrer": "search"
}
```

## search payload

```json
{
  "query": "wireless headphones",
  "result_count": 42
}
```

## add_to_cart payload

```json
{
  "product_id": "uuid",
  "quantity": 1,
  "unit_price_eur": 79.99
}
```

## checkout_started payload

```json
{
  "cart_id": "uuid",
  "item_count": 3,
  "cart_value_eur": 154.50
}
```

## order_created payload

```json
{
  "order_id": "uuid",
  "item_count": 3,
  "order_value_eur": 154.50
}
```

## payment_attempted payload

```json
{
  "payment_id": "uuid",
  "order_id": "uuid",
  "amount_eur": 154.50,
  "payment_method": "card",
  "status": "authorized"
}
```

## inventory_changed payload

```json
{
  "product_id": "uuid",
  "warehouse_id": "paris-01",
  "delta_quantity": -1,
  "reason": "sale"
}
```

## Versioning policy

Breaking schema changes increment `event_version`.
Consumers must reject unsupported versions into quarantine rather than silently coercing them.
