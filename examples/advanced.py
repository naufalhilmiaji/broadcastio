"""
advanced.py

Advanced broadcastio usage demonstrating:
- retries
- fallback
- observability hooks
- attachments
- failure scenarios

SECURITY NOTE:
Recipients are loaded from environment variables.
Never hardcode real phone numbers in source code.
"""

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

import logging
import os
from pprint import pprint

from broadcastio.core.attachment import Attachment
from broadcastio.core.exceptions import BroadcastioError
from broadcastio.core.message import Message
from broadcastio.core.orchestrator import Orchestrator
from broadcastio.core.retry import RetryPolicy
from broadcastio.providers.dummy import DummyProvider
from broadcastio.providers.whatsapp import WhatsAppProvider

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("broadcastio")


# ---------------------------------------------------------------------------
# Recipient (loaded from environment)
# ---------------------------------------------------------------------------

RECIPIENT = os.getenv("BROADCASTIO_TEST_RECIPIENT")

if not RECIPIENT:
    raise RuntimeError(
        "Environment variable BROADCASTIO_TEST_RECIPIENT is not set.\n"
        "Example:\n"
        "  export BROADCASTIO_TEST_RECIPIENT='+628XXXXXXXXX'\n"
        '  setx BROADCASTIO_TEST_RECIPIENT "+628XXXXXXXXX"  (Windows)'
    )


# ---------------------------------------------------------------------------
# Providers
# ---------------------------------------------------------------------------

whatsapp = WhatsAppProvider("http://localhost:3000")
dummy = DummyProvider()


# ---------------------------------------------------------------------------
# Retry policy
# ---------------------------------------------------------------------------

retry_policy = RetryPolicy(
    max_attempts=3,
    backoff="exponential",
    base_delay=0.5,
    max_delay=2.0,
)


# ---------------------------------------------------------------------------
# Orchestrator with observability hooks
# ---------------------------------------------------------------------------

orch = Orchestrator(
    providers=[whatsapp, dummy],
    retry_policy=retry_policy,
    require_healthy=False,
    on_attempt=lambda a: logger.info(
        f"Attempt {a.attempt} via {a.provider} (success={a.success})"
    ),
    on_success=lambda r: logger.info(f"Delivery succeeded via {r.provider}"),
    on_failure=lambda r: logger.error(
        f"Delivery failed: {r.error.code} - {r.error.message}"
    ),
)


# ---------------------------------------------------------------------------
# Scenario 1: Message with attachment
# ---------------------------------------------------------------------------

print("\n=== Scenario 1: Attachment ===")

msg_attachment = Message(
    recipient=RECIPIENT,
    content="Testing attachment delivery",
    attachment=Attachment(
        # IMPORTANT:
        # host_path = path on Python machine
        # provider_path = path inside provider runtime (Docker container)
        host_path="shared_files/testing.txt",
        provider_path="/app/shared_files/testing.txt",
        filename="testing.txt",
    ),
)

try:
    result = orch.send(msg_attachment, trace=True)
except BroadcastioError as exc:
    logger.error(f"Configuration error: {exc}")
    raise

pprint(result.to_dict())


# ---------------------------------------------------------------------------
# Scenario 2: Forced logical failure (fallback)
# ---------------------------------------------------------------------------

print("\n=== Scenario 2: Forced logical failure ===")
print("This message intentionally fails to test fallback behavior")

msg_force_fail = Message(
    recipient=RECIPIENT,
    content="FORCE_LOGICAL_FAIL",
)

result = orch.send(msg_force_fail, trace=True)
pprint(result.to_dict())


# ---------------------------------------------------------------------------
# Scenario 3: Provider unavailable
# ---------------------------------------------------------------------------

print("\n=== Scenario 3: Provider unavailable ===")
print("ACTION REQUIRED:")
print("  Stop the WhatsApp Node service, then press Enter")
input()

msg_unavailable = Message(
    recipient=RECIPIENT,
    content="Test provider unavailable",
)

result = orch.send(msg_unavailable, trace=True)
pprint(result.to_dict())


# ---------------------------------------------------------------------------
# Scenario 4: Validation error
# ---------------------------------------------------------------------------

print("\n=== Scenario 4: Validation error ===")

msg_invalid = Message(
    recipient="",  # invalid on purpose
    content="This should fail",
)

try:
    orch.send(msg_invalid)
except BroadcastioError as exc:
    logger.error(f"Expected validation error: {exc.code} - {exc}")
