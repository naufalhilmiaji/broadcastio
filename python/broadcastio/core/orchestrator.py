import os
import time
import requests
from datetime import datetime, timedelta, timezone
from typing import Callable, Dict, List, Optional, Tuple

from broadcastio.core.exceptions import (
    AttachmentError,
    BroadcastioError,
    ErrorCode,
    OrchestrationError,
    ValidationError,
)
from broadcastio.core.health import ProviderHealth
from broadcastio.core.message import Message
from broadcastio.core.result import DeliveryError, DeliveryResult
from broadcastio.core.retry import RetryPolicy
from broadcastio.core.trace import DeliveryAttempt, DeliveryTrace
from broadcastio.providers.base import MessageProvider


class Orchestrator:
    """
    Coordinates outbound message delivery across providers.

    Responsibilities:
    - Message validation
    - Health-aware provider selection
    - Retry orchestration (per provider)
    - Fallback routing
    - Delivery tracing
    - Observability hooks
    """

    def __init__(
        self,
        providers: List[MessageProvider],
        *,
        retry_policy: Optional[RetryPolicy] = None,
        health_ttl: Optional[int] = 30,
        require_healthy: bool = False,
        on_attempt: Optional[Callable[[DeliveryAttempt], None]] = None,
        on_success: Optional[Callable[[DeliveryResult], None]] = None,
        on_failure: Optional[Callable[[DeliveryResult], None]] = None,
    ):
        if not providers:
            raise OrchestrationError("Orchestrator requires at least one provider")

        self.providers = providers
        self.retry_policy = retry_policy or RetryPolicy()
        self.health_ttl = health_ttl
        self.require_healthy = require_healthy

        self.on_attempt = on_attempt
        self.on_success = on_success
        self.on_failure = on_failure

        # provider_name -> (checked_at, ProviderHealth)
        self._health_cache: Dict[str, Tuple[datetime, ProviderHealth]] = {}

    def _validate_message(self, message: Message) -> None:
        if not message.recipient:
            raise ValidationError("Message recipient is required")

        if not message.content and not message.attachment:
            raise ValidationError("Message must have content or an attachment")

        if message.attachment:
            if not os.path.isfile(message.attachment.host_path):
                raise AttachmentError(
                    f"Attachment not found: {message.attachment.host_path}"
                )

            if not message.attachment.provider_path:
                raise AttachmentError("Attachment provider_path is required")

    def _get_provider_health(self, provider: MessageProvider) -> ProviderHealth:
        now = datetime.now(timezone.utc)

        if self.health_ttl is not None:
            cached = self._health_cache.get(provider.name)
            if cached:
                checked_at, health = cached
                if now - checked_at < timedelta(seconds=self.health_ttl):
                    return health

        health = provider.health()
        self._health_cache[provider.name] = (now, health)
        return health

    def _iter_providers(self) -> List[MessageProvider]:
        healthy = []
        unhealthy = []

        for provider in self.providers:
            health = self._get_provider_health(provider)
            if health.ready:
                healthy.append(provider)
            else:
                unhealthy.append(provider)

        if self.require_healthy and not healthy:
            raise OrchestrationError("No healthy providers available")

        return healthy or self.providers

    def _safe_call_hook(self, hook, payload) -> None:
        if not hook:
            return
        try:
            hook(payload)
        except Exception:
            # Hooks must NEVER affect orchestration
            pass

    def _sleep_before_retry(self, policy: RetryPolicy, attempt_index: int) -> None:
        if policy.backoff == "none":
            return

        delay = policy.base_delay
        if policy.backoff == "exponential":
            delay = delay * (2**attempt_index)

        if policy.max_delay is not None:
            delay = min(delay, policy.max_delay)

        if delay > 0:
            time.sleep(delay)

    def send(self, message: Message, *, trace: bool = False):
        self._validate_message(message)

        delivery_trace = DeliveryTrace() if trace else None
        last_error: Optional[DeliveryError] = None

        for provider in self._iter_providers():
            policy = getattr(provider, "retry_policy", None) or self.retry_policy

            for attempt_index in range(policy.max_attempts):
                started_at = datetime.now(timezone.utc)

                try:
                    result = provider.send(message)

                except BroadcastioError:
                    # Configuration / misuse → stop immediately
                    raise

                except requests.RequestException as exc:
                    result = DeliveryResult(
                        success=False,
                        provider=provider.name,
                        error=DeliveryError(
                            code=ErrorCode.PROVIDER_UNAVAILABLE,
                            message=f"{provider.name} service unavailable",
                            details={"exception": str(exc)},
                        ),
                    )

                except Exception as exc:
                    result = DeliveryResult(
                        success=False,
                        provider=provider.name,
                        error=DeliveryError(
                            code=ErrorCode.ALL_PROVIDERS_FAILED,
                            message=str(exc),
                        ),
                    )

                finished_at = datetime.now(timezone.utc)

                attempt = DeliveryAttempt(
                    provider=provider.name,
                    attempt=attempt_index + 1,
                    started_at=started_at,
                    finished_at=finished_at,
                    success=result.success,
                    error=result.error,
                )

                if delivery_trace:
                    delivery_trace.add_attempt(attempt)

                self._safe_call_hook(self.on_attempt, attempt)

                if result.success:
                    if delivery_trace:
                        delivery_trace.mark_finished(success=True)
                        result.trace = delivery_trace

                    self._safe_call_hook(self.on_success, result)
                    return result

                last_error = result.error

                if (
                    attempt_index + 1 < policy.max_attempts
                    and last_error
                    and policy.should_retry(last_error.code)
                ):
                    self._sleep_before_retry(policy, attempt_index)
                    continue

                break  # stop retrying this provider

        final_error = last_error or DeliveryError(
            code=ErrorCode.ALL_PROVIDERS_FAILED,
            message="All providers failed",
        )

        final_result = DeliveryResult(
            success=False,
            provider="none",
            error=final_error,
        )

        if delivery_trace:
            delivery_trace.mark_finished(success=False)
            final_result.trace = delivery_trace

        self._safe_call_hook(self.on_failure, final_result)

        return final_result
