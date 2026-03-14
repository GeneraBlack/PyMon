"""Blueprint domain models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Blueprint:
    """A character-owned blueprint."""

    item_id: int
    type_id: int
    type_name: str = ""
    location_id: int = 0
    location_flag: str = ""
    quantity: int = 0  # -1 = original, -2 = copy
    material_efficiency: int = 0
    time_efficiency: int = 0
    runs: int = 0  # -1 = BPO (infinite), >0 = BPC remaining runs

    @property
    def is_original(self) -> bool:
        """True if this is a BPO (original)."""
        return self.quantity == -1

    @property
    def is_copy(self) -> bool:
        """True if this is a BPC (copy)."""
        return self.quantity == -2

    @property
    def bpo_bpc_label(self) -> str:
        """Human-readable BPO/BPC label."""
        if self.is_original:
            return "BPO"
        elif self.is_copy:
            return f"BPC ({self.runs} Runs)"
        return str(self.quantity)
