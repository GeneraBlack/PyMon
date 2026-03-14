"""Planetary Interaction (PI) domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class PlanetaryPin:
    """A pin (building) on a planetary colony."""

    pin_id: int
    type_id: int
    type_name: str = ""
    schematic_id: int | None = None
    latitude: float = 0.0
    longitude: float = 0.0
    install_time: datetime | None = None
    expiry_time: datetime | None = None
    last_cycle_start: datetime | None = None


@dataclass
class PlanetaryRoute:
    """A route between pins on a colony."""

    route_id: int
    source_pin_id: int = 0
    destination_pin_id: int = 0
    content_type_id: int = 0
    content_type_name: str = ""
    quantity: int = 0


@dataclass
class PlanetaryColony:
    """A planetary colony summary."""

    planet_id: int
    solar_system_id: int = 0
    solar_system_name: str = ""
    planet_type: str = ""
    planet_name: str = ""
    owner_id: int = 0
    upgrade_level: int = 0
    num_pins: int = 0
    last_update: datetime | None = None
    pins: list[PlanetaryPin] = field(default_factory=list)
    routes: list[PlanetaryRoute] = field(default_factory=list)
