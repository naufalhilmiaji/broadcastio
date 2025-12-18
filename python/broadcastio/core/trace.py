import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from broadcastio.core.result import DeliveryError, DeliveryResult


@dataclass
class DeliveryAttempt:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    provider: str = ""
    success: bool = False
    started_at: datetime = field(default_factory=datetime.utcnow)
    finished_at: datetime = field(default_factory=datetime.utcnow)
    error: Optional[DeliveryError] = None

    @property
    def duration_ms(self) -> int:
        return int((self.finished_at - self.started_at).total_seconds() * 1000)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "provider": self.provider,
            "success": self.success,
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat(),
            "duration_ms": self.duration_ms,
            "error": self.error.to_dict() if self.error else None,
        }


@dataclass
class DeliveryTrace:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    attempts: List[DeliveryAttempt] = field(default_factory=list)
    final: DeliveryResult = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "attempts": [a.to_dict() for a in self.attempts],
            "final": self.final.to_dict(),
        }
