# Architecture Overview

This document describes the high-level architecture of `broadcastio`
and the design principles behind it.

---

## High-level flow

```

User application
↓
Orchestrator
↓
Provider (Python)
↓
External Service
↓
Delivery Channel

```

Example (WhatsApp):

```

Python app
↓
broadcastio Orchestrator
↓
WhatsAppProvider
↓
HTTP request
↓
Node.js WhatsApp service
↓
WhatsApp Web

```

## Core components

### Orchestrator

The Orchestrator is the **brain** of the system.

It is responsible for:

- Message validation
- Health-aware provider selection
- Retry orchestration
- Provider fallback
- Delivery tracing
- Observability hooks

All control flow lives here.

---

### Providers

Providers are **adapters** between `broadcastio` and delivery channels.

They:
- attempt delivery once
- return structured results
- expose health status
- remain stateless

Providers never:
- retry
- fallback
- coordinate other providers

---

### RetryPolicy

Retries are configured using `RetryPolicy`:

- Explicit
- Opt-in
- Per-provider
- Observable

Retry logic lives entirely in the Orchestrator.

---

### DeliveryTrace

Delivery tracing records:

- each provider attempt
- retries
- timing information
- final outcome

Tracing is optional and disabled by default.

---

### Observability hooks

Hooks allow users to observe delivery behavior in real time.

Hooks:
- are synchronous
- are optional
- never affect orchestration flow

---

## Error model

`broadcastio` separates errors into two categories:

### Exceptions
- Configuration errors
- Invalid input
- Misuse of the API

Exceptions stop orchestration immediately.

### Delivery errors
- Provider failures
- Network issues
- Logical delivery failures

Delivery errors are returned as `DeliveryResult`.

---

## Design principles

`broadcastio` is built around these principles:

- Explicit behavior
- No hidden retries
- Clear ownership of responsibilities
- Observable execution
- Safe defaults

---

## Why external services?

Some providers (e.g. WhatsApp) require non-Python runtimes.

`broadcastio` integrates with these services over HTTP to:
- keep the Python core clean
- isolate unstable dependencies
- allow independent scaling and deployment

