from dataclasses import dataclass
from typing import Optional

from broadcastio.core.errors import DeliveryError
from broadcastio.core.trace import DeliveryTrace


@dataclass
class DeliveryResult:
    success: bool
    provider: str
    message_id: Optional[str] = None
    error: Optional[DeliveryError] = None
    trace: Optional[DeliveryTrace] = None

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "provider": self.provider,
            "message_id": self.message_id,
            "error": self.error.to_dict() if self.error else None,
            "trace": self.trace.to_dict() if self.trace else None,
        }
