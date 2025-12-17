# Changelog

All notable changes to this project will be documented in this file.

This project follows [Semantic Versioning](https://semver.org/).

---
## [0.2.1] - 2025-01-xx

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
