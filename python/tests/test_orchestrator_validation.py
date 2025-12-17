import pytest
import os
import tempfile

from broadcastio.core.orchestrator import Orchestrator
from broadcastio.core.message import Message
from broadcastio.core.attachment import Attachment
from broadcastio.core.exceptions import (
    OrchestrationError,
    ValidationError,
    AttachmentError,
)
from broadcastio.providers.dummy import DummyProvider


def test_orchestrator_requires_providers():
    with pytest.raises(OrchestrationError):
        Orchestrator([])


def test_validation_missing_recipient():
    orch = Orchestrator([DummyProvider()])

    msg = Message(
        recipient="",
        content="hello",
    )

    with pytest.raises(ValidationError):
        orch.send(msg)


def test_validation_missing_content_and_attachment():
    orch = Orchestrator([DummyProvider()])

    msg = Message(
        recipient="123",
        content="",
    )

    with pytest.raises(ValidationError):
        orch.send(msg)


def test_attachment_host_path_not_found():
    orch = Orchestrator([DummyProvider()])

    attachment = Attachment(
        host_path="does/not/exist.txt",
        provider_path="/app/shared/does/not/exist.txt",
        filename="exist.txt",
    )

    msg = Message(
        recipient="123",
        content="hello",
        attachment=attachment,
    )

    with pytest.raises(AttachmentError):
        orch.send(msg)


def test_attachment_host_path_exists():
    orch = Orchestrator([DummyProvider()])

    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"test")
        host_path = f.name

    attachment = Attachment(
        host_path=host_path,
        provider_path="/app/shared/test.txt",
        filename="test.txt",
    )

    msg = Message(
        recipient="123",
        content="hello",
        attachment=attachment,
    )

    # DummyProvider always succeeds
    result = orch.send(msg)

    assert result.success is True

    os.unlink(host_path)
