# broadcastio

[![PyPI](https://img.shields.io/pypi/v/broadcastio)](https://pypi.org/project/broadcastio/)
![Python Versions](https://img.shields.io/pypi/pyversions/broadcastio)
![CI](https://github.com/naufalhilmiaji/broadcastio/actions/workflows/ci.yml/badge.svg)

**broadcastio** is a provider-agnostic Python library for
**outbound message broadcasting with fallback orchestration**.

It is designed for reliable notifications, alerts, and reports
across one or more delivery providers.

---

## Features

- 🚦 Ordered provider fallback with configurable retries
- 📦 Attachment support
- 🧩 Provider abstraction (WhatsApp, Email, etc.)
- ⚠️ Clear error classification
- 🔍 Observability hooks and delivery tracing
- 🧪 Tested core logic

---

## What it is / is not

### ✅ It is
- A Python **orchestration layer** for outbound messages
- A way to attempt delivery across multiple providers
- A library with explicit failure semantics

### ❌ It is not
- A chatbot framework
- An inbound message handler
- A WhatsApp automation tool by itself

---

## Installation

```bash
pip install broadcastio
````

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

Message(
    recipient="6281234567890",
    content="Daily report",
    attachment=Attachment(
        host_path="shared_files/report.xlsx",
        provider_path="/app/shared_files/report.xlsx",
        filename="report.xlsx"
    )
)
```

---

## Error Handling

* **Exceptions** → misconfiguration or invalid input
* **DeliveryResult** → delivery was attempted

```python
if not result.success:
    print(result.error.code, result.error.message)
```

---

## Observability Hooks

Hooks allow real-time observation without affecting delivery flow.

```python
def log_attempt(attempt):
    print(attempt.provider, attempt.success)

orch = Orchestrator([wa], on_attempt=log_attempt)
```

---

## Advanced Topics

* 📘 [Retries & Backoff](docs/retries.md)
* 📘 [Delivery Tracing](docs/tracing.md)

---

## Providers

### WhatsApp Provider

WhatsApp delivery is supported via an **external Node.js service**
based on WhatsApp Web.

This service is **not included** in the Python package.

📘 See full setup instructions in:

* [`docs/providers.md`] (planned)

---

## Project Status

* **Version:** 0.3.0a1
* **Status:** Alpha
* APIs may evolve before 1.0.0

---

## Links

* GitHub: [https://github.com/naufalhilmiaji/broadcastio](https://github.com/naufalhilmiaji/broadcastio)
* Issues: [https://github.com/naufalhilmiaji/broadcastio/issues](https://github.com/naufalhilmiaji/broadcastio/issues)

---

## License

MIT License
