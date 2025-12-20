"""
minimal.py

Minimal broadcastio usage.
Goal: send a single message successfully.

SECURITY NOTE:
Do NOT hardcode real phone numbers.
Use environment variables instead.
"""

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

import os

from broadcastio.core.message import Message
from broadcastio.core.orchestrator import Orchestrator
from broadcastio.providers.dummy import DummyProvider
from broadcastio.providers.whatsapp import WhatsAppProvider

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
# Orchestrator
# ---------------------------------------------------------------------------

orch = Orchestrator(
    providers=[whatsapp, dummy],
)


# ---------------------------------------------------------------------------
# Send message
# ---------------------------------------------------------------------------

msg = Message(
    recipient=RECIPIENT,
    content="Hello from broadcastio 👋",
)

result = orch.send(msg)

print("Success:", result.success)
print("Provider:", result.provider)
print("Message ID:", result.message_id)
