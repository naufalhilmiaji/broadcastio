from dataclasses import dataclass
from typing import Optional


@dataclass
class DeliveryError:
    code: str
    message: str
    details: Optional[dict] = None

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }
