from dataclasses import dataclass
from typing import Optional


@dataclass
class DeliveryError:
    code: str
    message: str
    details: dict | None = None

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


@dataclass
class DeliveryResult:
    success: bool
    provider: str
    message_id: str | None = None
    error: DeliveryError | None = None

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "provider": self.provider,
            "message_id": self.message_id,
            "error": self.error.to_dict() if self.error else None,
        }
