import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from broadcastio.core.errors import DeliveryError


@dataclass
class DeliveryAttempt:
    provider: str
    attempt: int
    started_at: datetime
    finished_at: datetime
    success: bool
    error: Optional[DeliveryError] = None

    @property
    def duration_ms(self) -> int:
        delta = self.finished_at - self.started_at
        return int(delta.total_seconds() * 1000)

    def to_dict(self) -> dict:
        return {
            "provider": self.provider,
            "attempt": self.attempt,
            "success": self.success,
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat(),
            "duration_ms": self.duration_ms,
            "error": self.error.to_dict() if self.error else None,
        }


@dataclass
class DeliveryTrace:
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: Optional[datetime] = None
    success: Optional[bool] = None
    attempts: List[DeliveryAttempt] = field(default_factory=list)

    def add_attempt(self, attempt: DeliveryAttempt) -> None:
        self.attempts.append(attempt)

    def mark_finished(self, *, success: bool) -> None:
        self.success = success
        self.finished_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "trace_id": self.trace_id,
            "started_at": self.started_at.isoformat(),
            "finished_at": (self.finished_at.isoformat() if self.finished_at else None),
            "success": self.success,
            "attempts": [a.to_dict() for a in self.attempts],
        }
