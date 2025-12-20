# Providers

Providers are responsible for **sending messages via a specific delivery channel**
(e.g. WhatsApp, Email, SMS).

In `broadcastio`, providers are intentionally **thin and stateless**.

---

## Provider responsibilities

A provider must:

- Attempt delivery **once**
- Return a `DeliveryResult`
- Expose a `health()` method
- Never retry internally
- Never perform orchestration or fallback

All orchestration logic (retries, fallback, tracing) is handled by the **Orchestrator**.

---

## Provider interface

All providers inherit from `MessageProvider`:

```python
class MessageProvider:
    name: str

    def send(self, message: Message) -> DeliveryResult:
        ...

    def health(self) -> ProviderHealth:
        ...
````

---

## Provider health

Providers must expose a `health()` method that returns `ProviderHealth`:

```python
ProviderHealth(
    provider="whatsapp",
    ready=True,
    details=None,
)
```

Health checks are used by the Orchestrator to:

* skip unhealthy providers
* enforce strict health mode
* cache health state (TTL-based)

---

## WhatsApp Provider

`broadcastio` includes a WhatsApp provider backed by an **external Node.js service**
based on WhatsApp Web.

### Characteristics

* Outbound messaging only
* HTTP-based integration
* QR-code authentication
* Uses `whatsapp-web.js` (unofficial)

### Requirements

* Node.js 18+
* Chrome / Chromium
* WhatsApp mobile app for authentication

See the README for setup instructions.

---

## Dummy Provider

A `DummyProvider` is included for:

* testing
* fallback examples
* local development

It always reports healthy and simulates successful delivery.

---

## Provider-specific retries

Providers may optionally define their own retry policy:

```python
class WhatsAppProvider(MessageProvider):
    retry_policy = RetryPolicy(max_attempts=3)
```

If not provided, the Orchestrator’s default `RetryPolicy` is used.

---

## Writing a custom provider

To implement a custom provider:

1. Subclass `MessageProvider`
2. Implement `send()`
3. Implement `health()`
4. Return `DeliveryResult` consistently

Providers should **never raise exceptions** for delivery failures.
Exceptions are reserved for configuration or misuse.
