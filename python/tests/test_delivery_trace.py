from broadcastio.core.exceptions import ErrorCode
from broadcastio.core.health import ProviderHealth
from broadcastio.core.message import Message
from broadcastio.core.orchestrator import Orchestrator
from broadcastio.core.result import DeliveryResult, DeliveryError
from broadcastio.core.trace import DeliveryTrace
from broadcastio.providers.dummy import DummyProvider
from broadcastio.providers.base import MessageProvider


class AlwaysFailProvider(MessageProvider):
    name = "failer"

    def health(self) -> ProviderHealth:
        return ProviderHealth(
            provider=self.name,
            ready=True,
            details="Always healthy (test provider)",
        )

    def send(self, message):
        return DeliveryResult(
            success=False,
            provider=self.name,
            error=DeliveryError(
                code=ErrorCode.ALL_PROVIDERS_FAILED,
                message="forced failure",
            ),
        )


def test_send_without_trace_returns_delivery_result():
    orch = Orchestrator([DummyProvider()])

    result = orch.send(Message(recipient="test", content="hello"))

    assert isinstance(result, DeliveryResult)
    assert result.success is True


def test_delivery_trace_single_success():
    orch = Orchestrator([DummyProvider()])

    trace = orch.send(
        Message(recipient="test", content="hello"),
        trace=True,
    )

    assert isinstance(trace, DeliveryTrace)
    assert trace.final.success is True
    assert len(trace.attempts) == 1

    attempt = trace.attempts[0]
    assert attempt.provider == "dummy"
    assert attempt.success is True
    assert attempt.duration_ms >= 0


def test_delivery_trace_records_fallback_attempts():
    orch = Orchestrator(
        [
            AlwaysFailProvider(),
            DummyProvider(),
        ]
    )

    trace = orch.send(
        Message(recipient="test", content="hello"),
        trace=True,
    )

    assert trace.final.success is True
    assert len(trace.attempts) == 2

    first, second = trace.attempts

    assert first.provider == "failer"
    assert first.success is False

    assert second.provider == "dummy"
    assert second.success is True


def test_delivery_trace_all_providers_failed():
    orch = Orchestrator(
        [
            AlwaysFailProvider(),
        ]
    )

    trace = orch.send(
        Message(recipient="test", content="hello"),
        trace=True,
    )

    assert trace.final.success is False
    assert len(trace.attempts) == 1
    assert trace.attempts[0].success is False


def test_delivery_trace_serialization():
    orch = Orchestrator([DummyProvider()])

    trace = orch.send(
        Message(recipient="test", content="hello"),
        trace=True,
    )

    data = trace.to_dict()

    assert "id" in data
    assert "attempts" in data
    assert isinstance(data["attempts"], list)
    assert "final" in data
