import requests

from broadcastio.core.exceptions import ProviderError
from broadcastio.providers.base import MessageProvider
from broadcastio.core.message import Message
from broadcastio.core.result import DeliveryResult, DeliveryError
from broadcastio.core.health import ProviderHealth


class WhatsAppProvider(MessageProvider):
    name = "whatsapp"

    def __init__(self, base_url: str, timeout: int = 5):
        if not base_url:
            raise ProviderError("WhatsAppProvider base_url is not configured")

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def health(self) -> ProviderHealth:
        try:
            resp = requests.get(f"{self.base_url}/health", timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()

            return ProviderHealth(
                provider=self.name, ready=bool(data.get("ready", False)), details=None
            )

        except Exception as exc:
            return ProviderHealth(provider=self.name, ready=False, details=str(exc))

    def send(self, message: Message) -> DeliveryResult:
        payload = {
            "recipient": message.recipient,
            "content": message.content,
            "metadata": {
                "priority": message.metadata.priority,
                "reference_id": message.metadata.reference_id,
                "tags": message.metadata.tags,
                **message.metadata.extra,
            },
        }

        if message.attachment:
            payload["attachment"] = {
                "path": message.attachment.provider_path,
                "filename": message.attachment.filename,
                "mime_type": message.attachment.mime_type,
            }

        resp = requests.post(
            f"{self.base_url}/send", json=payload, timeout=self.timeout
        )
        resp.raise_for_status()
        data = resp.json()

        if data.get("success"):
            return DeliveryResult(
                success=True,
                provider=self.name,
                message_id=data.get("message_id"),
            )

        error = data.get("error", {})
        return DeliveryResult(
            success=False,
            provider=self.name,
            error=DeliveryError(
                code=error.get("code", "UNKNOWN_ERROR"),
                message=error.get("message", "Unknown error"),
            ),
        )
