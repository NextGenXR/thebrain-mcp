"""Tests for thebrain_mcp models."""

import pytest

from thebrain_mcp.models import (
    EntityType,
    LinkDto,
    ModificationLogDto,
    ThoughtDto,
    ThoughtKind,
)


def test_thought_dto_from_api(sample_thought_dict: dict) -> None:
    thought = ThoughtDto.from_api_dict(sample_thought_dict)
    assert thought.id == sample_thought_dict["id"]
    assert thought.name == "Test Thought"
    assert thought.kind == ThoughtKind.NORMAL
    assert thought.brain_id == "brain-uuid-here"


def test_link_dto_from_api(sample_link_dict: dict) -> None:
    link = LinkDto.from_api_dict(sample_link_dict)
    assert link.id == "link-uuid-1"
    assert link.thought_id_a == "thought-a"
    assert link.thought_id_b == "thought-b"
    assert link.relation == 1


def test_modification_log_dto_from_api() -> None:
    log = ModificationLogDto.from_api_dict(
        {
            "sourceId": "thought-123",
            "sourceType": 2,
            "modType": 101,
            "creationDateTime": "2024-01-20T00:00:00Z",
        }
    )
    assert log.source_id == "thought-123"
    assert log.source_type == EntityType.THOUGHT
    assert log.mod_type == 101
