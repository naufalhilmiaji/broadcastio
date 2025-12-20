import broadcastio
import inspect

from broadcastio.core.orchestrator import Orchestrator


def test_package_has_version():
    assert hasattr(broadcastio, "__version__")
    assert isinstance(broadcastio.__version__, str)
    assert broadcastio.__version__ != "unknown"


def test_public_api_imports():
    from broadcastio.core.message import Message
    from broadcastio.core.orchestrator import Orchestrator
    from broadcastio.core.retry import RetryPolicy
    from broadcastio.core.result import DeliveryResult
    from broadcastio.core.trace import DeliveryTrace


def test_orchestrator_signature():
    sig = inspect.signature(Orchestrator.__init__)
    params = sorted(list(sig.parameters.keys()))

    assert params == sorted(
        [
            "self",
            "providers",
            "health_ttl",
            "require_healthy",
            "retry_policy",
            "on_attempt",
            "on_success",
            "on_failure",
        ]
    )
