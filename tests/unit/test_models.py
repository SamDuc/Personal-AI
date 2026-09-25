from datetime import UTC, datetime

from personal_ai.core.models import AccessPolicy, DataItem


def test_access_policy_defaults_to_deny():
    policy = AccessPolicy()

    assert policy.read is False
    assert policy.write is False


def test_data_item_defaults():
    item = DataItem(
        id="local-001",
        source="local_filesystem",
        source_id="C:/example/test.pdf",
        uri="file:///C:/example/test.pdf",
        item_type="file",
    )

    assert item.id == "local-001"
    assert item.source == "local_filesystem"
    assert item.item_type == "file"

    assert item.content_available is False
    assert item.searchable is False
    assert item.sync_status == "new"
    assert item.sensitivity == "normal"

    assert item.topics == []
    assert item.tags == []

    assert item.access_policy.read is False
    assert item.access_policy.write is False


def test_data_item_with_metadata():
    modified = datetime(2026, 9, 25, 10, 30, tzinfo=UTC)

    item = DataItem(
        id="local-002",
        source="local_filesystem",
        source_id="C:/Projects/paper.pdf",
        uri="file:///C:/Projects/paper.pdf",
        item_type="file",
        mime_type="application/pdf",
        extension=".pdf",
        name="paper.pdf",
        size=123456,
        modified_at=modified,
        content_available=True,
        project="computer_vision",
        topics=["crack_detection"],
        tags=["research"],
        searchable=True,
    )

    assert item.name == "paper.pdf"
    assert item.mime_type == "application/pdf"
    assert item.extension == ".pdf"
    assert item.size == 123456
    assert item.modified_at == modified

    assert item.content_available is True
    assert item.project == "computer_vision"
    assert item.topics == ["crack_detection"]
    assert item.tags == ["research"]
    assert item.searchable is True


def test_data_items_do_not_share_mutable_lists():
    item_a = DataItem(
        id="a",
        source="local_filesystem",
        source_id="a",
        uri="file:///a",
        item_type="file",
    )

    item_b = DataItem(
        id="b",
        source="local_filesystem",
        source_id="b",
        uri="file:///b",
        item_type="file",
    )

    item_a.tags.append("research")

    assert item_a.tags == ["research"]
    assert item_b.tags == []