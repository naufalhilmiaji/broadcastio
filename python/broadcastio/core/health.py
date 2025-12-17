from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class ProviderHealth:
    provider: str
    ready: bool

    checked_at: datetime = datetime.now()
    details: Optional[str] = None
