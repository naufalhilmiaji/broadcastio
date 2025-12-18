import os
from datetime import datetime, timedelta, UTC
from typing import Callable, List, Optional, Union, Dict, Tuple

import requests

from broadcastio.core.exceptions import (
    AttachmentError,
    BroadcastioError,
    OrchestrationError,
    ErrorCode,
    ValidationError,
)
from broadcastio.core.message import Message
from broadcastio.core.result import DeliveryResult, DeliveryError
from broadcastio.core.trace import DeliveryAttempt, DeliveryTrace
from broadcastio.core.health import ProviderHealth
from broadcastio.providers.base import MessageProvider


class Orchestrator:
    """
    Coordinates message delivery across multiple providers,
    with optional health-aware routing and delivery tracing.
    """

    def __init__(
        self,
        providers: List[MessageProvider],
        *,
        health_ttl: Optional[int] = 30,
        require_healthy: bool = False,
        on_attempt: Optional[Callable] = None,
        on_success: Optional[Callable] = None,
        on_failure: Optional[Callable] = None,
    ):

        if not providers:
            raise OrchestrationError("Orchestrator requires at least one provider")

        self.providers = providers
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
            # Host-side validation
            if not os.path.isfile(message.attachment.host_path):
                raise AttachmentError(
                    f"Attachment not found: {message.attachment.host_path}"
                )

            # Provider-path sanity check
            if message.attachment.provider_path.startswith("/"):
                provider_dir = os.path.dirname(message.attachment.provider_path)
                if not provider_dir:
                    raise AttachmentError(
                        f"Invalid provider_path: {message.attachment.provider_path}"
                    )

    def _get_provider_health(self, provider: MessageProvider) -> ProviderHealth:
        now = datetime.now(UTC)

        if self.health_ttl is not None:
            cached = self._health_cache.get(provider.name)
            if cached:
                checked_at, health = cached
                if now - checked_at < timedelta(seconds=self.health_ttl):
                    return health

        health = provider.health()
        self._health_cache[provider.name] = (now, health)
        return health

    def _safe_call_hook(self, hook, arg) -> None:
        if not hook:
            return
        try:
            hook(arg)
        except Exception:
            # Hooks must NEVER affect orchestration
            pass

    def send(
        self,
        message: Message,
        *,
        trace: bool = False,
    ) -> Union[DeliveryResult, DeliveryTrace]:
        """
        Send a message using the configured providers.

        Args:
            message: Message to deliver
            trace: If True, return DeliveryTrace instead of DeliveryResult

        Returns:
            DeliveryResult or DeliveryTrace
        """
        self._validate_message(message)

        attempts: List[DeliveryAttempt] = []
        last_error: Optional[DeliveryError] = None

        healthy_providers: List[MessageProvider] = []

        for provider in self.providers:
            health = self._get_provider_health(provider)

            if health.ready:
                healthy_providers.append(provider)
            else:
                # Record skipped provider in trace
                if trace:
                    now = datetime.now(UTC)
                    attempts.append(
                        DeliveryAttempt(
                            provider=provider.name,
                            success=False,
                            started_at=now,
                            finished_at=now,
                            error=DeliveryError(
                                code=ErrorCode.PROVIDER_UNAVAILABLE,
                                message="Provider reported unhealthy",
                                details={"health": health.details},
                            ),
                        )
                    )

        if self.require_healthy and not healthy_providers:
            raise OrchestrationError("No healthy providers available")

        providers_to_try = healthy_providers or self.providers

        for provider in providers_to_try:
            started_at = datetime.now(UTC)

            try:
                result = provider.send(message)

            except BroadcastioError:
                # Misuse / configuration error → never fallback
                raise

            except requests.RequestException as exc:
                # Provider runtime unavailable (Node down, timeout, etc.)
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
                # Unexpected crash inside provider
                result = DeliveryResult(
                    success=False,
                    provider=provider.name,
                    error=DeliveryError(
                        code=ErrorCode.ALL_PROVIDERS_FAILED,
                        message=str(exc),
                    ),
                )

            finished_at = datetime.now(UTC)

            # Record attempt
            attempt = DeliveryAttempt(
                provider=provider.name,
                success=result.success,
                started_at=started_at,
                finished_at=finished_at,
                error=result.error,
            )

            attempts.append(attempt)

            self._safe_call_hook(self.on_attempt, attempt)

            if result.success:
                if trace:
                    return DeliveryTrace(attempts=attempts, final=result)
                return result

            last_error = result.error

        final_result = DeliveryResult(
            success=False,
            provider="none",
            error=(
                last_error
                if isinstance(last_error, DeliveryError)
                else DeliveryError(
                    code=ErrorCode.ALL_PROVIDERS_FAILED,
                    message=str(last_error) if last_error else "All providers failed",
                )
            ),
        )

        if trace:
            return DeliveryTrace(attempts=attempts, final=final_result)

        return final_result
