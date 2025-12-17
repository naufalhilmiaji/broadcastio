import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from broadcastio.core.attachment import Attachment


@dataclass
class MessageMetadata:
    # Higher = more important (1–10)
    priority: int = 5

    # For tracing logs across systems
    reference_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Free-form labels: ["alert", "prod"]
    tags: List[str] = field(default_factory=list)

    # Anything else you might need later
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Message:
    recipient: str
    content: str
    metadata: MessageMetadata | dict | None = field(default_factory=MessageMetadata)
    attachment: Optional[Attachment] = None

    def __post_init__(self):
        # Normalize metadata
        if self.metadata is None:
            self.metadata = MessageMetadata()

        elif isinstance(self.metadata, MessageMetadata):
            pass  # already correct

        elif isinstance(self.metadata, dict):
            self.metadata = MessageMetadata(
                priority=self.metadata.get("priority", 5),
                reference_id=self.metadata.get("reference_id", str(uuid.uuid4())),
                tags=self.metadata.get("tags", []),
                extra={
                    k: v
                    for k, v in self.metadata.items()
                    if k not in {"priority", "reference_id", "tags"}
                },
            )
        else:
            raise TypeError("metadata must be MessageMetadata, dict, or None")
