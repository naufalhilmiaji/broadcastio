from dataclasses import dataclass
from typing import Optional


@dataclass
class Attachment:
    # Path as seen by PYTHON (host)
    host_path: str

    # Path as seen by PROVIDER (container)
    provider_path: str

    filename: Optional[str] = None
    mime_type: Optional[str] = None
