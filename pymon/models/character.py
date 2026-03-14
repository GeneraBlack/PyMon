"""Character domain model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Character:
    """Represents an EVE Online character."""

    character_id: int
    character_name: str
    corporation_id: int = 0
    corporation_name: str = ""
    alliance_id: int | None = None
    alliance_name: str = ""
    birthday: str = ""
    security_status: float = 0.0
    portrait_url: str = ""

    # Attributes
    intelligence: int = 0
    memory: int = 0
    perception: int = 0
    willpower: int = 0
    charisma: int = 0

    # Location
    solar_system_id: int = 0
    solar_system_name: str = ""
    station_id: int | None = None
    station_name: str = ""
    ship_type_id: int = 0
    ship_name: str = ""
    is_online: bool = False

    # Skills summary
    total_sp: int = 0
    unallocated_sp: int = 0

    # Wallet
    wallet_balance: float = 0.0

    # Last update
    last_updated: datetime | None = None


@dataclass
class SkillInfo:
    """A trained skill."""

    skill_id: int
    skill_name: str = ""
    group_name: str = ""
    active_skill_level: int = 0
    trained_skill_level: int = 0
    skillpoints_in_skill: int = 0


@dataclass
class SkillQueueEntry:
    """An entry in the skill training queue."""

    skill_id: int
    skill_name: str = ""
    finished_level: int = 0
    queue_position: int = 0
    start_date: datetime | None = None
    finish_date: datetime | None = None
    training_start_sp: int = 0
    level_start_sp: int = 0
    level_end_sp: int = 0

    @property
    def is_training(self) -> bool:
        """Check if this skill is currently being trained."""
        if self.start_date and self.finish_date:
            now = datetime.now(timezone.utc)
            return self.start_date <= now <= self.finish_date
        return False

    @property
    def time_remaining(self) -> float | None:
        """Seconds remaining until training completes."""
        if self.finish_date:
            remaining = (self.finish_date - datetime.now(timezone.utc)).total_seconds()
            return max(0.0, remaining)
        return None


@dataclass
class Clone:
    """A jump clone."""

    jump_clone_id: int
    location_id: int
    location_type: str = ""
    location_name: str = ""
    implants: list[int] = field(default_factory=list)
