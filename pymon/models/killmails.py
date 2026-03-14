"""Killmail domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class KillmailAttacker:
    """An attacker in a killmail."""

    character_id: int | None = None
    character_name: str = ""
    corporation_id: int | None = None
    corporation_name: str = ""
    alliance_id: int | None = None
    ship_type_id: int | None = None
    ship_type_name: str = ""
    weapon_type_id: int | None = None
    weapon_type_name: str = ""
    damage_done: int = 0
    final_blow: bool = False
    security_status: float = 0.0


@dataclass
class KillmailItem:
    """An item fitted/carried on the victim ship."""

    type_id: int
    type_name: str = ""
    flag: int = 0  # EVE item flag (slot)
    quantity_dropped: int = 0
    quantity_destroyed: int = 0
    singleton: int = 0

    @property
    def total_quantity(self) -> int:
        return self.quantity_dropped + self.quantity_destroyed

    @property
    def slot_name(self) -> str:
        """Human-readable slot from EVE flag ID."""
        if 11 <= self.flag <= 18:
            return f"Low Slot {self.flag - 10}"
        elif 19 <= self.flag <= 26:
            return f"Med Slot {self.flag - 18}"
        elif 27 <= self.flag <= 34:
            return f"Hi Slot {self.flag - 26}"
        elif 92 <= self.flag <= 99:
            return f"Rig Slot {self.flag - 91}"
        elif 125 <= self.flag <= 132:
            return f"Subsystem {self.flag - 124}"
        elif self.flag == 87:
            return "Drone Bay"
        elif self.flag == 5:
            return "Cargo"
        elif self.flag == 62:
            return "Implant"
        elif self.flag == 89:
            return "Fleet Hangar"
        elif self.flag == 155:
            return "Fighter Bay"
        return f"Flag {self.flag}"


@dataclass
class KillmailVictim:
    """The victim in a killmail."""

    character_id: int | None = None
    character_name: str = ""
    corporation_id: int | None = None
    corporation_name: str = ""
    alliance_id: int | None = None
    ship_type_id: int = 0
    ship_type_name: str = ""
    damage_taken: int = 0
    items: list[KillmailItem] = field(default_factory=list)
    position: dict = field(default_factory=dict)


@dataclass
class Killmail:
    """A detailed killmail."""

    killmail_id: int
    killmail_hash: str = ""
    killmail_time: datetime | None = None
    solar_system_id: int = 0
    solar_system_name: str = ""
    victim: KillmailVictim | None = None
    attackers: list[KillmailAttacker] = field(default_factory=list)
    total_value: float = 0.0  # estimated from zKillboard or items

    @property
    def is_loss(self) -> bool:
        """Check if this was a loss (our character was the victim)."""
        return self.victim is not None


@dataclass
class KillmailSummary:
    """A summary entry from the killmails endpoint."""

    killmail_id: int
    killmail_hash: str = ""
