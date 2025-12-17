from dataclasses import dataclass
from typing import Optional


@dataclass
class DeliveryError:
    code: str
    message: str
    details: Optional[dict] = None


@dataclass
class DeliveryResult:
    success: bool
    provider: str

    message_id: Optional[str] = None
    error: Optional[DeliveryError] = None
