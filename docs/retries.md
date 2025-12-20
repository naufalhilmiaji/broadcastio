# Retries in broadcastio

`broadcastio` supports **explicit, per-provider retries** designed to be
predictable, observable, and safe by default.

Retries are **disabled by default**.

---

## Design principles

Retries in `broadcastio` follow these rules:

- Retries are **explicit**, never implicit
- Retries are **per provider**, not global
- Retries happen **before fallback**
- Retries are **observable** via tracing and hooks
- Providers themselves never retry internally

This ensures retries never hide failures or surprise users.

---

## RetryPolicy

Retries are configured using `RetryPolicy`.

```python
from broadcastio.core.retry import RetryPolicy
````

### Fields

| Field          | Description                                   |
| -------------- | --------------------------------------------- |
| `max_attempts` | Total attempts per provider (including first) |
| `backoff`      | `"none"`, `"fixed"`, or `"exponential"`       |
| `base_delay`   | Base delay in seconds                         |
| `max_delay`    | Optional delay cap                            |
| `retry_on`     | Set of retryable `ErrorCode` values           |

---

### Default behavior

```python
RetryPolicy()
```

Equivalent to:

* `max_attempts = 1`
* no retries
* no delay

This preserves backwards compatibility.

---

## Example: basic retries

```python
policy = RetryPolicy(
    max_attempts=3,
    backoff="fixed",
    base_delay=1.0,
)
```

Behavior:

* Try provider once
* Retry up to 2 more times
* Wait 1 second between retries
* Fallback only after retries are exhausted

---

## Retryable errors

Retries only occur when the error code matches `retry_on`.

If `retry_on` is not provided, retries happen **only** for:

```python
ErrorCode.PROVIDER_UNAVAILABLE
```

This prevents retrying:

* validation errors
* authentication failures
* logical provider failures

Example:

```python
policy = RetryPolicy(
    max_attempts=3,
    retry_on={
        ErrorCode.PROVIDER_UNAVAILABLE,
        ErrorCode.TIMEOUT,
    },
)
```

---

## Where retries happen

Retries are handled **exclusively by the Orchestrator**.

Providers must:

* attempt delivery once
* return a `DeliveryResult`
* never retry internally

This keeps retry behavior transparent and traceable.

---

## Retries and fallback

Retry flow:

```
Provider A
  ├── attempt 1
  ├── retry 2
  └── retry 3
Provider B
  └── attempt 1
```

Fallback occurs **only after retries for a provider are exhausted**.

---

## Retries and tracing

Each retry is recorded as a separate `DeliveryAttempt` when tracing is enabled.

See: [`docs/tracing.md`](tracing.md)

---

## Retries and health checks

Retries only occur if a provider is considered **healthy**.

If `require_healthy=True` and no providers are healthy,
orchestration stops immediately.
