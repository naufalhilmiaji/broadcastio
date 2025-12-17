import pytest

from broadcastio.core.message import Message, MessageMetadata


def test_metadata_default_created():
    msg = Message(
        recipient="123",
        content="hello",
    )

    assert isinstance(msg.metadata, MessageMetadata)
    assert msg.metadata.priority == 5
    assert msg.metadata.tags == []
    assert msg.metadata.extra == {}


def test_metadata_none_normalized():
    msg = Message(
        recipient="123",
        content="hello",
        metadata=None,
    )

    assert isinstance(msg.metadata, MessageMetadata)


def test_metadata_object_preserved():
    meta = MessageMetadata(
        priority=9,
        reference_id="abc",
        tags=["alert"],
        extra={"foo": "bar"},
    )

    msg = Message(
        recipient="123",
        content="hello",
        metadata=meta,
    )

    assert msg.metadata is meta
    assert msg.metadata.priority == 9
    assert msg.metadata.reference_id == "abc"
    assert msg.metadata.tags == ["alert"]
    assert msg.metadata.extra == {"foo": "bar"}


def test_metadata_dict_partial():
    msg = Message(
        recipient="123",
        content="hello",
        metadata={
            "reference_id": "FORCE_LOGICAL_FAIL",
        },
    )

    assert isinstance(msg.metadata, MessageMetadata)
    assert msg.metadata.reference_id == "FORCE_LOGICAL_FAIL"
    assert msg.metadata.priority == 5
    assert msg.metadata.tags == []
    assert msg.metadata.extra == {}


def test_metadata_dict_with_extra_fields():
    msg = Message(
        recipient="123",
        content="hello",
        metadata={
            "priority": 1,
            "reference_id": "xyz",
            "tags": ["prod"],
            "region": "apac",
            "retry": True,
        },
    )

    assert msg.metadata.priority == 1
    assert msg.metadata.reference_id == "xyz"
    assert msg.metadata.tags == ["prod"]
    assert msg.metadata.extra == {
        "region": "apac",
        "retry": True,
    }


def test_metadata_invalid_type_raises():
    with pytest.raises(TypeError):
        Message(
            recipient="123",
            content="hello",
            metadata=42,  # invalid
        )
