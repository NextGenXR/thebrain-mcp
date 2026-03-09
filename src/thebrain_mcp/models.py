"""
Typed data models for TheBrain API responses and sync state.
"""

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any


class ThoughtKind(IntEnum):
    """Thought kind enumeration from TheBrain API."""

    NORMAL = 1
    TYPE = 2
    EVENT = 3
    TAG = 4
    SYSTEM = 5


class EntityType(IntEnum):
    """Entity type in modification logs."""

    UNKNOWN = -1
    BRAIN = 1
    THOUGHT = 2
    LINK = 3
    ATTACHMENT = 4
    BRAIN_SETTING = 5
    BRAIN_ACCESS_ENTRY = 6
    CALENDAR_EVENT = 7
    FIELD_INSTANCE = 8
    FIELD_DEFINITION = 9


class ModificationType(IntEnum):
    """Modification type in modification logs (subset)."""

    CREATED = 101
    DELETED = 102
    CHANGED_NAME = 103


@dataclass
class ThoughtDto:
    """Thought entity from TheBrain API."""

    id: str
    brain_id: str
    name: str
    kind: ThoughtKind | int = ThoughtKind.NORMAL
    ac_type: int = 0
    label: str | None = None
    type_id: str | None = None
    foreground_color: str | None = None
    background_color: str | None = None
    creation_datetime: str | None = None
    modification_datetime: str | None = None
    forgotten_datetime: str | None = None
    links_modification_datetime: str | None = None
    raw_json: str | None = None

    @classmethod
    def from_api_dict(cls, d: dict[str, Any]) -> "ThoughtDto":
        """Build from API response dict."""
        return cls(
            id=str(d["id"]),
            brain_id=str(d.get("brainId", "")),
            name=str(d.get("name", "")),
            kind=d.get("kind", ThoughtKind.NORMAL),
            ac_type=d.get("acType", 0),
            label=d.get("label"),
            type_id=str(d["typeId"]) if d.get("typeId") else None,
            foreground_color=d.get("foregroundColor"),
            background_color=d.get("backgroundColor"),
            creation_datetime=d.get("creationDateTime"),
            modification_datetime=d.get("modificationDateTime"),
            forgotten_datetime=d.get("forgottenDateTime"),
            links_modification_datetime=d.get("linksModificationDateTime"),
        )


@dataclass
class LinkDto:
    """Link entity between two thoughts."""

    id: str
    brain_id: str
    thought_id_a: str
    thought_id_b: str
    relation: int  # 1=Child, 2=Parent, 3=Jump, 4=Sibling
    direction: int = 0
    meaning: int = 1
    name: str | None = None
    type_id: str | None = None
    kind: int = 1
    color: str | None = None
    thickness: int | None = None
    creation_datetime: str | None = None
    modification_datetime: str | None = None
    raw_json: str | None = None

    @classmethod
    def from_api_dict(cls, d: dict[str, Any]) -> "LinkDto":
        """Build from API response dict."""
        return cls(
            id=str(d["id"]),
            brain_id=str(d.get("brainId", "")),
            thought_id_a=str(d.get("thoughtIdA", "")),
            thought_id_b=str(d.get("thoughtIdB", "")),
            relation=int(d.get("relation", 1)),
            direction=int(d.get("direction", 0)),
            meaning=int(d.get("meaning", 1)),
            name=d.get("name"),
            type_id=str(d["typeId"]) if d.get("typeId") else None,
            kind=int(d.get("kind", 1)),
            color=d.get("color"),
            thickness=d.get("thickness"),
            creation_datetime=d.get("creationDateTime"),
            modification_datetime=d.get("modificationDateTime"),
        )


@dataclass
class ModificationLogDto:
    """Single entry from the modifications API."""

    source_id: str
    source_type: EntityType | int
    mod_type: ModificationType | int
    old_value: str | None = None
    new_value: str | None = None
    creation_datetime: str | None = None
    modification_datetime: str | None = None
    extra_a_id: str | None = None
    extra_b_id: str | None = None

    @classmethod
    def from_api_dict(cls, d: dict[str, Any]) -> "ModificationLogDto":
        """Build from API response dict."""
        return cls(
            source_id=str(d.get("sourceId", "")),
            source_type=int(d.get("sourceType", -1)),
            mod_type=int(d.get("modType", 0)),
            old_value=d.get("oldValue"),
            new_value=d.get("newValue"),
            creation_datetime=d.get("creationDateTime"),
            modification_datetime=d.get("modificationDateTime"),
            extra_a_id=str(d["extraAId"]) if d.get("extraAId") else None,
            extra_b_id=str(d["extraBId"]) if d.get("extraBId") else None,
        )


@dataclass
class SyncStateDto:
    """Per-brain sync state stored in cache."""

    brain_id: str
    last_sync_at: str
    full_sync_completed: bool = False
    total_thoughts: int = 0
    total_links: int = 0
    last_full_sync_duration_ms: int | None = None
