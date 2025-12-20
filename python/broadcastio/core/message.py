import uuid
import warnings
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from broadcastio.core.attachment import Attachment
from broadcastio.core.exceptions import ValidationError


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
        elif not isinstance(self.recipient, str) or not self.recipient.strip():
            raise ValidationError("recipient must be a non-empty string")
        elif self.recipient.isdigit() and len(self.recipient) > 10:
            warnings.warn(
                "Recipient looks like a phone number. "
                "Avoid hardcoding real phone numbers in source code.",
                UserWarning,
            )
        else:
            raise TypeError("metadata must be MessageMetadata, dict, or None")
