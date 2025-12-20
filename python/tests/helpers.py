from broadcastio.core.exceptions import ErrorCode
from broadcastio.core.health import ProviderHealth
from broadcastio.core.result import DeliveryError, DeliveryResult
from broadcastio.providers.base import MessageProvider


class FlakyProvider(MessageProvider):
    name = "flaky"

    def __init__(self, fail_times: int):
        self.fail_times = fail_times
        self.calls = 0

    def health(self):
        return ProviderHealth(
            provider=self.name,
            ready=True,
            details="healthy (test)",
        )

    def send(self, message):
        self.calls += 1
        if self.calls <= self.fail_times:
            return DeliveryResult(
                success=False,
                provider=self.name,
                error=DeliveryError(
                    code=ErrorCode.PROVIDER_UNAVAILABLE,
                    message="temporary failure",
                ),
            )
        return DeliveryResult(
            success=True,
            provider=self.name,
            message_id="ok",
        )
