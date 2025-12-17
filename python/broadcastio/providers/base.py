from abc import ABC, abstractmethod
from typing import Any

from broadcastio.core.message import Message
from broadcastio.core.result import DeliveryResult
from broadcastio.core.health import ProviderHealth


class MessageProvider(ABC):
    """
    Base class for all message providers (WhatsApp, Telegram, Email, etc.)
    """

    name: str  # provider identifier, e.g. "whatsapp"

    @abstractmethod
    def send(self, message: Message) -> DeliveryResult:
        """
        Send a message through this provider.

        Must return a DeliveryResult.
        Must NOT raise exceptions for normal failures.
        """
        raise NotImplementedError

    @abstractmethod
    def health(self) -> ProviderHealth:
        """
        Return current provider health status.
        Used by the orchestrator to decide whether to use this provider.
        """
        raise NotImplementedError
