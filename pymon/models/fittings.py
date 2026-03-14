"""Fitting domain models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FittingItem:
    """A module/item in a fitting."""

    type_id: int
    type_name: str = ""
    flag: str = ""   # e.g. HiSlot0, LoSlot0, MedSlot0, RigSlot0, SubSystemSlot0, Cargo, DroneBay
    quantity: int = 1


@dataclass
class Fitting:
    """A saved ship fitting."""

    fitting_id: int
    name: str = ""
    description: str = ""
    ship_type_id: int = 0
    ship_type_name: str = ""
    items: list[FittingItem] = field(default_factory=list)
