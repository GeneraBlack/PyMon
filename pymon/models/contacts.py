"""Contacts and Standings domain models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Contact:
    """A contact entry."""

    contact_id: int
    contact_type: str = ""  # character, corporation, alliance, faction
    contact_name: str = ""
    standing: float = 0.0
    label_ids: list[int] = field(default_factory=list)
    is_watched: bool = False
    is_blocked: bool = False


@dataclass
class ContactLabel:
    """A contact label."""

    label_id: int
    label_name: str = ""


@dataclass
class Standing:
    """A standing towards an NPC entity."""

    from_id: int
    from_type: str = ""  # agent, npc_corp, faction
    from_name: str = ""
    standing: float = 0.0
