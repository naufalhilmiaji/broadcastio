"""
run_test.py

This script simulates real-world usage of broadcastio from a user's perspective.
It is NOT a unit test. It is a sanity-check / demo script.

Scenarios covered:
1. Health-aware delivery with fallback + trace
2. Attachment validation failure
3. Strict health mode (require_healthy)
4. Logical provider failure
"""

import logging

from broadcastio.core.attachment import Attachment
from broadcastio.core.exceptions import BroadcastioError
from broadcastio.core.message import Message, MessageMetadata
from broadcastio.core.orchestrator import Orchestrator
from broadcastio.providers.whatsapp import WhatsAppProvider
from broadcastio.providers.dummy import DummyProvider


# ---------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("broadcastio-demo")


# ---------------------------------------------------------------------
# Providers
# ---------------------------------------------------------------------

wa = WhatsAppProvider(
    "http://localhost:3000"
)  # assumes Node service may/may not be running
dummy = DummyProvider()
orch = Orchestrator(
    [wa, dummy],
    require_healthy=False,
)

# ---------------------------------------------------------------------
# Scenario 1: Health-aware delivery with fallback + trace
# ---------------------------------------------------------------------

# print("\n=== Scenario 1: Health-aware delivery with fallback + trace ===")


# msg = Message(
#     recipient="628123456789",
#     content="Hello from broadcastio (health-aware)",
# )

# try:
#     trace = orch.send(msg, trace=True)
#     print("Final result:", trace.final)
#     print("Delivery trace:")
#     for attempt in trace.attempts:
#         print(
#             f"  - provider={attempt.provider}, "
#             f"success={attempt.success}, "
#             f"duration_ms={attempt.duration_ms}, "
#             f"error={attempt.error.code if attempt.error else None}"
#         )
# except BroadcastioError as exc:
#     logger.error(
#         "Broadcastio configuration error",
#         extra={"code": exc.code, "err_message": str(exc)},
#     )


# ---------------------------------------------------------------------
# Scenario 2: Attachment validation failure (host-side)
# ---------------------------------------------------------------------

# print("\n=== Scenario 2: Attachment validation failure ===")

# bad_attachment = Attachment(
#     host_path="shared_files/does-not-exist.xlsx",  # intentionally wrong
#     provider_path="/app/shared_files/does-not-exist.xlsx",
#     filename="does-not-exist.xlsx",
# )

# msg_with_bad_attachment = Message(
#     recipient="628123456789",
#     content="This should fail before sending",
#     attachment=bad_attachment,
# )

# try:
#     orch.send(msg_with_bad_attachment)
# except BroadcastioError as exc:
#     logger.error(
#         "Expected attachment validation error",
#         extra={"code": exc.code, "err_message": str(exc)},
#     )


# ---------------------------------------------------------------------
# Scenario 3: Strict health mode (require_healthy=True)
# ---------------------------------------------------------------------

print("\n=== Scenario 3: Strict health mode ===")

orch_strict = Orchestrator(
    [wa],
    require_healthy=True,
)

msg_strict = Message(
    recipient="628123456789",
    content="Strict health check test",
)

try:
    orch_strict.send(msg_strict)
except BroadcastioError as exc:
    logger.error(
        "Strict health orchestration error",
        extra={"code": exc.code, "err_message": str(exc)},
    )


# ---------------------------------------------------------------------
# Scenario 4: Logical provider failure (no exception, but delivery fails)
# ---------------------------------------------------------------------

print("\n=== Scenario 4: Logical provider failure ===")

msg_logical_fail = Message(
    recipient="628123456789",
    content="Trigger logical failure",
    metadata=MessageMetadata(reference_id="FORCE_LOGICAL_FAIL"),
)

try:
    result = orch.send(msg_logical_fail)
    if not result.success:
        logger.warning(
            "Logical delivery failure",
            extra={"code": result.error.code, "message": result.error.message},
        )
    else:
        print("Unexpected success:", result)
except BroadcastioError as exc:
    logger.error(
        "Unexpected broadcastio error",
        extra={"code": exc.code, "err_message": str(exc)},
    )


print("\n=== run_test.py completed ===")
