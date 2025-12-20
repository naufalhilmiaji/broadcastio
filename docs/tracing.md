# Delivery Tracing

`broadcastio` provides **delivery tracing** to help users understand
how a message was delivered, retried, or failed.

Tracing is **optional** and **disabled by default**.

---

## What is DeliveryTrace?

A `DeliveryTrace` records:

- Every provider attempt
- Retry attempts
- Timing information
- Final success or failure

It is useful for:
- debugging failures
- audit logs
- observability pipelines

---

## Enabling tracing

Tracing is enabled per call:

```python
result = orch.send(message, trace=True)
````

When enabled:

* `DeliveryResult.trace` is populated
* All attempts are recorded

---

## DeliveryAttempt

Each attempt (including retries) is recorded as a `DeliveryAttempt`.

Captured fields include:

| Field         | Description                   |
| ------------- | ----------------------------- |
| `provider`    | Provider name                 |
| `attempt`     | Attempt number (1-based)      |
| `started_at`  | UTC timestamp                 |
| `finished_at` | UTC timestamp                 |
| `success`     | Whether the attempt succeeded |
| `error`       | Optional `DeliveryError`      |

---

## Example trace structure

```json
{
  "trace_id": "a9c9e6e3-...",
  "started_at": "2025-01-10T10:12:00Z",
  "finished_at": "2025-01-10T10:12:05Z",
  "success": false,
  "attempts": [
    {
      "provider": "whatsapp",
      "attempt": 1,
      "success": false,
      "duration_ms": 500,
      "error": {
        "code": "PROVIDER_UNAVAILABLE",
        "message": "service unavailable"
      }
    }
  ]
}
```

---

## Serialization

`DeliveryTrace` can be serialized safely:

```python
trace_data = result.trace.to_dict()
```

All timestamps are ISO-8601 UTC strings.

---

## Tracing vs Observability Hooks

| Feature | Purpose                  |
| ------- | ------------------------ |
| Tracing | Post-delivery inspection |
| Hooks   | Real-time observation    |

Hooks are better for:

* logging
* metrics
* alerts

Tracing is better for:

* debugging
* audit logs
* diagnostics

---

## Performance considerations

* Tracing adds minimal overhead
* No external dependencies
* Disabled by default
