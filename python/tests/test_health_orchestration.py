import pytest

from broadcastio.core.exceptions import ErrorCode, OrchestrationError
from broadcastio.core.health import ProviderHealth
from broadcastio.core.message import Message
from broadcastio.core.orchestrator import Orchestrator
from broadcastio.core.result import DeliveryResult, DeliveryError
from broadcastio.core.trace import DeliveryTrace
from broadcastio.providers.base import MessageProvider


class HealthyFailingProvider(MessageProvider):
    name = "healthy_fail"

    def health(self) -> ProviderHealth:
        return ProviderHealth(
            provider=self.name,
            ready=True,
            details="healthy but fails",
        )

    def send(self, message):
        return DeliveryResult(
            success=False,
            provider=self.name,
            error=DeliveryError(
                code=ErrorCode.ALL_PROVIDERS_FAILED,
                message="intentional failure",
            ),
        )


class UnhealthyProvider(MessageProvider):
    name = "unhealthy"

    def health(self) -> ProviderHealth:
        return ProviderHealth(
            provider=self.name,
            ready=False,
            details="service down",
        )

    def send(self, message):
        raise AssertionError("send() must not be called for unhealthy providers")


class HealthySuccessProvider(MessageProvider):
    name = "healthy_ok"

    def health(self) -> ProviderHealth:
        return ProviderHealth(
            provider=self.name,
            ready=True,
            details="healthy",
        )

    def send(self, message):
        return DeliveryResult(
            success=True,
            provider=self.name,
            message_id="ok-123",
        )


def test_unhealthy_provider_is_skipped():
    orch = Orchestrator(
        providers=[UnhealthyProvider(), HealthySuccessProvider()],
        require_healthy=False,
    )

    trace = orch.send(
        Message(recipient="test", content="hello"),
        trace=True,
    )

    assert isinstance(trace, DeliveryTrace)
    assert trace.final.success is True
    assert trace.final.provider == "healthy_ok"

    assert len(trace.attempts) == 2

    skipped, success = trace.attempts

    assert skipped.provider == "unhealthy"
    assert skipped.success is False
    assert skipped.error.code == ErrorCode.PROVIDER_UNAVAILABLE

    assert success.provider == "healthy_ok"
    assert success.success is True


def test_unhealthy_does_not_block_fallback():
    orch = Orchestrator(
        providers=[
            UnhealthyProvider(),
            HealthyFailingProvider(),
            HealthySuccessProvider(),
        ],
        require_healthy=False,
    )

    trace = orch.send(
        Message(recipient="test", content="hello"),
        trace=True,
    )

    assert trace.final.success is True
    assert trace.final.provider == "healthy_ok"

    providers_tried = [a.provider for a in trace.attempts]
    assert providers_tried == ["unhealthy", "healthy_fail", "healthy_ok"]


def test_require_healthy_raises_if_none_healthy():
    orch = Orchestrator(
        providers=[UnhealthyProvider()],
        require_healthy=True,
    )

    with pytest.raises(OrchestrationError):
        orch.send(
            Message(recipient="test", content="hello"),
        )


def test_require_healthy_allows_healthy_provider():
    orch = Orchestrator(
        providers=[UnhealthyProvider(), HealthySuccessProvider()],
        require_healthy=True,
    )

    result = orch.send(
        Message(recipient="test", content="hello"),
    )

    assert result.success is True
    assert result.provider == "healthy_ok"


def test_health_cache_is_used(monkeypatch):
    calls = {"count": 0}

    class CountingHealthProvider(HealthySuccessProvider):
        name = "counting"

        def health(self):
            calls["count"] += 1
            return super().health()

    provider = CountingHealthProvider()
    orch = Orchestrator(
        providers=[provider],
        health_ttl=60,
    )

    msg = Message(recipient="test", content="hello")

    orch.send(msg)
    orch.send(msg)
    orch.send(msg)

    assert calls["count"] == 1


def test_health_cache_disabled_when_ttl_none():
    calls = {"count": 0}

    class CountingHealthProvider(HealthySuccessProvider):
        name = "counting_nocache"

        def health(self):
            calls["count"] += 1
            return super().health()

    provider = CountingHealthProvider()
    orch = Orchestrator(
        providers=[provider],
        health_ttl=None,
    )

    msg = Message(recipient="test", content="hello")

    orch.send(msg)
    orch.send(msg)

    assert calls["count"] == 2
