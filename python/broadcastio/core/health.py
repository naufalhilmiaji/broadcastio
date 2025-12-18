from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timezone


@dataclass
class ProviderHealth:
    provider: str
    ready: bool

    checked_at: datetime = datetime.now(timezone.utc)
    details: Optional[str] = None
