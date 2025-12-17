import logging

from broadcastio.core.attachment import Attachment
from broadcastio.core.exceptions import BroadcastioError
from broadcastio.core.orchestrator import Orchestrator
from broadcastio.providers.whatsapp import WhatsAppProvider
from broadcastio.providers.dummy import DummyProvider
from broadcastio.core.message import Message

# Basic configuration (optional, but good practice)
logging.basicConfig(level=logging.INFO)  # Default is WARNING level

# Get a logger instance
logger = logging.getLogger(__name__)

wa = WhatsAppProvider("http://localhost:3000")  # correct URL
dummy = DummyProvider()

orch = Orchestrator([wa])
host_path = "shared_files/DailyReport-15-December-2025.xlsx"  # this is wrong path
provider_path = (
    "/app/shared_files/DailyReport-15-December-2025.xlsx"  # this is wrong path
)

filename = host_path.split("/")[-1]

msg_attachment = Message(
    recipient="6281285244060",
    content="Testing Chat (With Excel)",
    attachment=Attachment(
        host_path=host_path,
        provider_path=provider_path,
        filename="DailyReport-15-December-2025.xlsx",
    ),
)

msg_text = Message(
    recipient="6281285244060",
    content="Testing Chat",
)

msg_error = Message(
    recipient="6281285244060",
    content="Test logical failure",
    metadata={"reference_id": "FORCE_LOGICAL_FAIL"},
)
try:
    result = orch.send(msg_error)
except BroadcastioError as exc:
    logger.error("broadcastio error", extra={"code": exc.code, "err_message": str(exc)})
    raise

if not result.success:
    logger.warning("Delivery failed", extra={"code": result.error.code})

print(result)
