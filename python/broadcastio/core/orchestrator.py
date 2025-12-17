import os
from typing import List

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
from broadcastio.providers.base import MessageProvider


class Orchestrator:
    """
    Coordinates message delivery across multiple providers.
    """

    def __init__(self, providers: List[MessageProvider]):
        if not providers:
            raise OrchestrationError("Orchestrator requires at least one provider")

        self.providers = providers

    def _validate_message(self, message):
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
                # Best-effort sanity check: directory must exist on host mapping
                provider_dir = os.path.dirname(message.attachment.provider_path)
                if not provider_dir:
                    raise AttachmentError(
                        f"Invalid provider_path: {message.attachment.provider_path}"
                    )

    def send(self, message: Message) -> DeliveryResult:
        self._validate_message(message)

        last_error = None

        for provider in self.providers:
            try:
                result = provider.send(message)

            except BroadcastioError:
                # Misuse / config error → never fallback
                raise

            except requests.RequestException as exc:
                # Provider runtime unavailable (Node down, timeout, etc.)
                last_error = DeliveryError(
                    code=ErrorCode.PROVIDER_UNAVAILABLE,
                    message=f"{provider.name} service unavailable",
                    details={"exception": str(exc)},
                )
                continue

            except Exception as exc:
                # Unexpected crash inside provider
                last_error = DeliveryError(
                    code=ErrorCode.ALL_PROVIDERS_FAILED,
                    message=str(exc),
                )
                continue

            # Provider returned a result
            if result.success:
                return result

            # Logical provider failure → try next provider
            last_error = result.error

        return DeliveryResult(
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
