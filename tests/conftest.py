"""
Shared pytest fixtures for thebrain_mcp tests.
"""

import pytest


@pytest.fixture
def sample_thought_dict() -> dict:
    """Sample thought as returned by TheBrain API."""
    return {
        "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "brainId": "brain-uuid-here",
        "name": "Test Thought",
        "kind": 1,
        "acType": 0,
        "label": None,
        "typeId": None,
        "foregroundColor": "#000000",
        "backgroundColor": None,
        "creationDateTime": "2024-01-15T10:00:00Z",
        "modificationDateTime": "2024-01-16T12:00:00Z",
    }


@pytest.fixture
def sample_link_dict() -> dict:
    """Sample link as returned by TheBrain API."""
    return {
        "id": "link-uuid-1",
        "brainId": "brain-uuid-here",
        "thoughtIdA": "thought-a",
        "thoughtIdB": "thought-b",
        "relation": 1,
        "direction": 0,
        "meaning": 1,
        "name": None,
    }
