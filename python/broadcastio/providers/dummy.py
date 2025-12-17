from broadcastio.providers.base import MessageProvider
from broadcastio.core.result import DeliveryResult
from broadcastio.core.health import ProviderHealth
from broadcastio.core.message import Message


class DummyProvider(MessageProvider):
    name = "dummy"

    def health(self) -> ProviderHealth:
        return ProviderHealth(
            provider=self.name,
            ready=True,
            details="Always healthy (dummy)"
        )

    def send(self, message: Message) -> DeliveryResult:
        print("[DUMMY] Fallback provider used")
        return DeliveryResult(
            success=True,
            provider=self.name,
            message_id="dummy-123"
        )
