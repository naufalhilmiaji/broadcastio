# Changelog

All notable changes to this project will be documented in this file.

This project follows [Semantic Versioning](https://semver.org/).

---
## [0.3.0a2] – 2025-12-21

### Changed
- Stabilized `RetryPolicy` behavior and retry execution flow
- Finalized `DeliveryTrace` structure, timestamps, and serialization
- Improved health-aware orchestration consistency
- Normalized provider-unavailable error handling
- Aligned tests, documentation, and runtime behavior

### Fixed
- CI failures related to timezone handling and logging
- Edge cases in orchestration fallback and health checks
- Minor internal correctness and cleanup issues

### Notes
- This is an **alpha release**
- APIs may continue to evolve before `1.0.0`
- No new features introduced compared to `0.3.0a1`


## [0.3.0a1] – 2025-12-18

### Added
- Health-aware orchestration with provider skipping
- DeliveryTrace for detailed delivery inspection
- Observability hooks (`on_attempt`, `on_success`, `on_failure`)
- Strict health mode (`require_healthy`)
- Health caching with configurable TTL

### Changed
- Orchestrator now supports optional tracing and hooks
- Provider unavailability is normalized consistently
- (Minor) Changed QR path to `./node/qr/wa_authentication.png`

### Notes
- This is an **alpha release**
- APIs may evolve before 1.0.0

---
## [0.2.1] - 2025-12-17

### Fixed
- Expose package version via `broadcastio.__version__`
- Remove misplaced root-level `__init__.py`

---

## [0.2.0] – 2025-12-16

### Added
- Structured exception hierarchy (`BroadcastioError` and subclasses)
- Canonical error codes for delivery and orchestration failures
- Provider unavailability normalization (`PROVIDER_UNAVAILABLE`)
- Message metadata normalization to enforce internal consistency
- Unit tests for message normalization and orchestrator behavior
- Public-ready packaging metadata (`pyproject.toml`)

### Changed
- Centralized message and attachment validation in the orchestrator
- Refined provider contract: providers no longer validate message correctness
- Improved fallback logic and error classification
- Updated WhatsApp provider to clearly separate logical failures from runtime failures

### Fixed
- Prevented invalid message metadata from causing runtime attribute errors
- Ensured runtime provider failures no longer surface as misconfiguration errors

---

## [0.1.0] – 2025-12-16

### Added
- Initial release of `broadcastio`
- Core message model with attachment support
- Provider abstraction and fallback orchestrator
- WhatsApp provider (via external Node service)
- Dummy provider for testing and development
- Basic delivery result and error model
