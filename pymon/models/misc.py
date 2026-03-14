"""Calendar and Miscellaneous domain models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class CalendarEvent:
    """A calendar event."""

    event_id: int
    title: str = ""
    event_date: datetime | None = None
    event_response: str = ""  # accepted, declined, tentative, not_responded
    importance: int = 0
    owner_id: int = 0
    owner_name: str = ""
    owner_type: str = ""  # eve_server, corporation, faction, character, alliance
    text: str = ""  # event description (from detail endpoint)
    duration: int = 0  # minutes


@dataclass
class JumpFatigue:
    """Jump fatigue information."""

    jump_fatigue_expire_date: datetime | None = None
    last_jump_date: datetime | None = None
    last_update_date: datetime | None = None


@dataclass
class AgentResearch:
    """An agent research entry."""

    agent_id: int
    agent_name: str = ""
    skill_type_id: int = 0
    skill_type_name: str = ""
    started_at: datetime | None = None
    points_per_day: float = 0.0
    remainder_points: float = 0.0


@dataclass
class Bookmark:
    """A bookmark."""

    bookmark_id: int
    folder_id: int | None = None
    label: str = ""
    notes: str = ""
    location_id: int = 0
    creator_id: int = 0
    created: datetime | None = None
    # Coordinates (optional – for space bookmarks)
    x: float | None = None
    y: float | None = None
    z: float | None = None
    # Item bookmark
    item_id: int | None = None
    type_id: int | None = None


@dataclass
class BookmarkFolder:
    """A bookmark folder."""

    folder_id: int
    name: str = ""


@dataclass
class Medal:
    """A character medal."""

    medal_id: int
    title: str = ""
    description: str = ""
    corporation_id: int = 0
    corporation_name: str = ""
    issuer_id: int = 0
    date: datetime | None = None
    reason: str = ""
    status: str = ""  # private, public


@dataclass
class AssetItem:
    """An asset item."""

    item_id: int
    type_id: int
    type_name: str = ""
    location_id: int = 0
    location_type: str = ""  # station, solar_system, item, other
    location_flag: str = ""
    location_name: str = ""
    quantity: int = 1
    is_singleton: bool = False
    is_blueprint_copy: bool | None = None
