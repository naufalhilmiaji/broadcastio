# broadcastio

[![PyPI](https://img.shields.io/pypi/v/broadcastio)](https://pypi.org/project/broadcastio/)
![Python Versions](https://img.shields.io/pypi/pyversions/broadcastio)
![CI](https://github.com/naufalhilmiaji/broadcastio/actions/workflows/ci.yml/badge.svg)

**broadcastio** is a provider-agnostic Python library for **outbound message broadcasting with fallback orchestration**.

It is designed for sending notifications, alerts, or reports reliably across one or more delivery providers, with clear failure semantics.

---

## Features

- 🚦 Ordered provider fallback
- 📦 Attachment support
- 🧩 Provider abstraction (WhatsApp, Email, etc.)
- ⚠️ Clear error classification (exceptions vs delivery failures)
- 🧪 Tested core logic

---

## What it is / is not

### ✅ It is

- A Python **orchestration layer** for outbound messages
- A way to retry delivery across providers
- A library that separates configuration errors from runtime failures

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

> **Note:** Some providers (such as WhatsApp) require external services to be running.
> The Quick Start example below assumes the WhatsApp Node.js service is already available.
> See the *Providers* section for setup details.

---

## Quick Start

```python
from broadcastio.core.orchestrator import Orchestrator
from broadcastio.providers.whatsapp import WhatsAppProvider
from broadcastio.core.message import Message

# Example using WhatsAppProvider (requires Node.js service)
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
from broadcastio.core.message import Message

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

`host_path` refers to the Python host filesystem, while `provider_path` refers to the provider runtime (for example, a Docker container).

Attachment paths are intentionally explicit to support containerized providers.

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

`broadcastio` supports WhatsApp delivery via an **external Node.js service** based on WhatsApp Web.

This service is **not included** in the Python package and must be run separately.
The Python library communicates with it over HTTP.

---

#### Requirements

* Node.js **18+**
* Chrome / Chromium (used by Puppeteer)
* A WhatsApp account for QR-based authentication

---

#### Running the WhatsApp service (Docker Compose – recommended)

From the repository root:

```bash
git clone https://github.com/naufalhilmiaji/broadcastio.git
cd broadcastio

docker compose up
```

This will start the WhatsApp service on:

```
http://localhost:3000
```

Authentication state is persisted under `node/.wwebjs_auth/`.

---

#### Running the WhatsApp service (manual Docker build)

This section describes a manual Docker build as an alternative to Docker Compose.

```bash
git clone https://github.com/naufalhilmiaji/broadcastio.git
cd broadcastio/node

docker build -t broadcastio-whatsapp .
docker run -p 3000:3000 \
  -v $(pwd)/.wwebjs_auth:/app/.wwebjs_auth \
  broadcastio-whatsapp
```

The service will be available at:

```
http://localhost:3000
```

---

#### WhatsApp authentication

On first startup, the service will generate a QR code for authentication.
Depending on configuration, this may be written to a file or printed in logs.

* Scan the QR code using the WhatsApp mobile app
* Authentication state is stored in `.wwebjs_auth/`
* Subsequent restarts reuse the existing session

If `.wwebjs_auth/` is removed, re-authentication will be required.

---

#### Service health check

You can verify that the service is ready by calling:

```bash
curl http://localhost:3000/health
```

Expected response:

```json
{
  "provider": "whatsapp",
  "ready": true,
  "timestamp": "2025-12-17T06:34:44.198Z"
}
```

---

#### Using WhatsAppProvider in Python

```python
from broadcastio.core.orchestrator import Orchestrator
from broadcastio.providers.whatsapp import WhatsAppProvider
from broadcastio.providers.dummy import DummyProvider
from broadcastio.core.message import Message

wa = WhatsAppProvider("http://localhost:3000")
fallback = DummyProvider()

orch = Orchestrator([wa, fallback])

orch.send(
    Message(
        recipient="6281234567890",
        content="Hello from broadcastio"
    )
)
```

---

#### Notes and limitations

* The WhatsApp provider supports **outbound messaging only**
* Inbound messages and chatbot behavior are intentionally out of scope
* WhatsApp delivery relies on `whatsapp-web.js`, which is unofficial
* This provider is best suited for automation, alerts, and internal tooling

---

#### Architecture overview

```
Python application
        ↓
    broadcastio
        ↓
   HTTP request
        ↓
Node WhatsApp service
        ↓
   WhatsApp Web
```

---

## Project Status

* **Version:** 0.2.0
* **Status:** Alpha
* Public APIs may evolve until version 1.0.0

---

## Links

* GitHub: [https://github.com/naufalhilmiaji/broadcastio](https://github.com/naufalhilmiaji/broadcastio)
* Issues: [https://github.com/naufalhilmiaji/broadcastio/issues](https://github.com/naufalhilmiaji/broadcastio/issues)

---

## License

MIT License.
