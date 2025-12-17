# broadcastio

**broadcastio** is a provider-agnostic Python library for **outbound message broadcasting with fallback orchestration**.

It is designed for sending notifications, alerts, or reports reliably across one or more delivery providers, with clear failure semantics.

---

## Features

* 🚦 Ordered provider fallback
* 📦 Attachment support
* 🧩 Provider abstraction (WhatsApp, Email, etc.)
* ⚠️ Clear error classification (exceptions vs delivery failures)
* 🧪 Tested core logic

---

## What it is / is not

### ✅ It is

* A Python **orchestration layer** for outbound messages
* A way to retry delivery across providers
* A library that separates configuration errors from runtime failures

### ❌ It is not

* A chatbot framework
* An inbound message handler
* A WhatsApp automation tool by itself

---

## Installation

```bash
pip install broadcastio
```

Python ≥ 3.10 required.

---

## Quick Start

```python
from broadcastio.core.orchestrator import Orchestrator
from broadcastio.providers.whatsapp import WhatsAppProvider
from broadcastio.core.message import Message

wa = WhatsAppProvider("http://localhost:3000")
orch = Orchestrator([wa])

result = orch.send(
    Message(
        recipient="6281234567890",
        content="Hello from broadcastio"
    )
)

print(result)
```

---

## Attachments

```python
from broadcastio.core.attachment import Attachment

msg = Message(
    recipient="6281234567890",
    content="Daily report",
    attachment=Attachment(
        host_path="shared_files/report.xlsx",
        provider_path="/app/shared_files/report.xlsx",
        filename="report.xlsx"
    )
)
```

`host_path` refers to the Python host filesystem, while `provider_path` refers to the provider runtime (e.g. Docker container).

---

## Error Handling

`broadcastio` distinguishes **exceptions** from **delivery results**.

### Exceptions

Raised for misconfiguration or invalid input:

```python
from broadcastio.core.exceptions import BroadcastioError

try:
    orch.send(msg)
except BroadcastioError as exc:
    print(exc.code, str(exc))
```

### DeliveryResult

Returned when delivery was attempted:

```python
if not result.success:
    print(result.error.code, result.error.message)
```

This makes fallback behavior explicit and predictable.

---

## Providers

### WhatsApp Provider

The WhatsApp provider relies on an **external Node.js sender service** (e.g. using `whatsapp-web.js`).

```python
from broadcastio.providers.whatsapp import WhatsAppProvider

wa = WhatsAppProvider("http://localhost:3000")
```

If the service is unavailable, `broadcastio` returns:

```
DeliveryError(code="PROVIDER_UNAVAILABLE")
```

---

## Project Status

* **Version:** 0.2.0
* **Status:** Alpha
* APIs may evolve until 1.0.0

See the full documentation on GitHub for architecture details and Docker examples.

---

## Links

* GitHub: [https://github.com/naufalhilmiaji/broadcastio](https://github.com/naufalhilmiaji/broadcastio)
* Issues: [https://github.com/naufalhilmiaji/broadcastio/issues](https://github.com/naufalhilmiaji/broadcastio/issues)

---

## License

MIT License.
