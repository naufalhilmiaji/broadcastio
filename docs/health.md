# Health-Aware Orchestration

`broadcastio` supports **health-aware routing** to prevent sending messages
through unavailable or degraded providers.

Health checks are **provider-defined** and **orchestrator-enforced**.

---

## ProviderHealth

Providers report health using `ProviderHealth`:

```python
ProviderHealth(
    provider="whatsapp",
    ready=True,
    details=None,
)
````

### Fields

| Field      | Description                          |
| ---------- | ------------------------------------ |
| `provider` | Provider name                        |
| `ready`    | Whether provider can accept requests |
| `details`  | Optional diagnostic information      |

---

## Health caching (TTL)

Health checks may be expensive.

The Orchestrator caches provider health using a configurable TTL:

```python
Orchestrator(
    providers=[wa],
    health_ttl=30,  # seconds
)
```

* `health_ttl=None` disables caching
* Cached health is reused until TTL expires

---

## Health-aware routing

When sending a message:

1. Provider health is checked
2. Unhealthy providers are skipped
3. Healthy providers are tried in order

If **all providers are unhealthy**:

* and `require_healthy=False` → all providers are tried anyway
* and `require_healthy=True` → orchestration fails immediately

---

## Strict health mode

Enable strict mode:

```python
Orchestrator(
    providers=[wa, email],
    require_healthy=True,
)
```

Behavior:

* If no providers are healthy → `OrchestrationError`
* No retries or fallback attempted

This is useful for:

* critical systems
* strict SLO enforcement
* avoiding degraded services

---

## Health and retries

Retries only occur if a provider is considered **healthy**.

An unhealthy provider:

* is skipped entirely
* is not retried
* may still appear in delivery traces (if enabled)

---

## Health vs availability

Health represents **provider readiness**, not message validity.

A provider may be:

* healthy but fail logically
* unhealthy but still reachable
* temporarily unavailable

Health is a signal — not a guarantee.
