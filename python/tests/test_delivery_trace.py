from broadcastio.core.exceptions import ErrorCode
from broadcastio.core.health import ProviderHealth
from broadcastio.core.message import Message
from broadcastio.core.orchestrator import Orchestrator
from broadcastio.core.result import DeliveryError, DeliveryResult
from broadcastio.core.trace import DeliveryTrace
from broadcastio.providers.base import MessageProvider
from broadcastio.providers.dummy import DummyProvider


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

    result = orch.send(
        Message(recipient="test", content="hello"),
        trace=True,
    )

    assert result.success is True
    assert result.trace is not None

    trace = result.trace
    assert trace.success is True
    assert len(trace.attempts) == 1


def test_delivery_trace_records_fallback_attempts():
    orch = Orchestrator(
        [
            AlwaysFailProvider(),
            DummyProvider(),
        ]
    )

    result = orch.send(
        Message(recipient="test", content="hello"),
        trace=True,
    )
    trace = result.trace

    assert trace.success is True
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

    result = orch.send(
        Message(recipient="test", content="hello"),
        trace=True,
    )
    trace = result.trace

    assert trace.success is False
    assert len(trace.attempts) == 1
    assert trace.attempts[0].success is False


def test_delivery_trace_serialization():
    orch = Orchestrator([DummyProvider()])

    result = orch.send(
        Message(recipient="test", content="hello"),
        trace=True,
    )

    data = result.trace.to_dict()

    assert "trace_id" in data
    assert "attempts" in data
    assert "started_at" in data
    assert "finished_at" in data
    assert isinstance(data["attempts"], list)
