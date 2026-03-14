"""Notification domain models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Notification:
    """An in-game notification."""

    notification_id: int
    type: str = ""
    sender_id: int = 0
    sender_type: str = ""  # character, corporation, alliance, faction, other
    sender_name: str = ""
    timestamp: datetime | None = None
    text: str = ""
    is_read: bool = False
