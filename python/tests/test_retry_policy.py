from tests.helpers import FlakyProvider

from broadcastio.core.errors import DeliveryError
from broadcastio.core.exceptions import ErrorCode
from broadcastio.core.message import Message
from broadcastio.core.orchestrator import Orchestrator
from broadcastio.core.result import DeliveryResult
from broadcastio.core.retry import RetryPolicy


def test_retry_until_success():
    provider = FlakyProvider(fail_times=2)

    orch = Orchestrator(
        [provider],
        retry_policy=RetryPolicy(max_attempts=3),
    )

    result = orch.send(Message(recipient="123", content="hello"), trace=True)

    assert result.success
    assert provider.calls == 3
    assert len(result.trace.attempts) == 3


def test_retry_exhausted():
    provider = FlakyProvider(fail_times=5)

    orch = Orchestrator(
        [provider],
        retry_policy=RetryPolicy(max_attempts=2),
    )

    result = orch.send(Message(recipient="123", content="hello"), trace=True)

    assert not result.success
    assert provider.calls == 2
    assert result.error.code == "PROVIDER_UNAVAILABLE"


class LogicalFailProvider(FlakyProvider):
    def send(self, message):
        self.calls += 1
        return DeliveryResult(
            success=False,
            provider=self.name,
            error=DeliveryError(
                code=ErrorCode.VALIDATION_ERROR,
                message="bad input",
            ),
        )


def test_no_retry_on_logical_error():
    provider = LogicalFailProvider(fail_times=1)

    orch = Orchestrator(
        [provider],
        retry_policy=RetryPolicy(max_attempts=3),
    )

    result = orch.send(Message(recipient="123", content="hello"))

    assert provider.calls == 1
    assert not result.success


class AlwaysFailProvider(FlakyProvider):
    def send(self, message):
        self.calls += 1
        return DeliveryResult(
            success=False,
            provider=self.name,
            error=DeliveryError(
                code=ErrorCode.PROVIDER_UNAVAILABLE,
                message="down",
            ),
        )


def test_retry_then_fallback():
    primary = AlwaysFailProvider(fail_times=10)
    fallback = FlakyProvider(fail_times=0)

    orch = Orchestrator(
        [primary, fallback],
        retry_policy=RetryPolicy(max_attempts=2),
    )

    result = orch.send(Message(recipient="123", content="hello"))

    assert result.success
    assert primary.calls == 2
    assert fallback.calls == 1
