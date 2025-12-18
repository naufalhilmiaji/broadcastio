from dataclasses import dataclass
from typing import Optional
from datetime import datetime, UTC


@dataclass
class ProviderHealth:
    provider: str
    ready: bool

    checked_at: datetime = datetime.now(UTC)
    details: Optional[str] = None
