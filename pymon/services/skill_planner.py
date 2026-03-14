"""Skill training time calculator and planner.

Uses SDE data (dogma attributes) and character attributes to compute
exact EVE skill training times.  Supports creating, editing and
persisting skill plans.
"""

from __future__ import annotations

import math
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from pymon.sde.database import SDEDatabase

logger = logging.getLogger(__name__)

# ── EVE Skill Training constants ──────────────────────────────────

# Dogma attribute IDs
_PRIMARY_ATTR = 180      # primaryAttribute
_SECONDARY_ATTR = 181    # secondaryAttribute
_TIME_CONSTANT = 275     # skillTimeConstant (rank)

# requiredSkill 1-6
_REQ_SKILL_IDS = [182, 183, 184, 1285, 1289, 1290]
_REQ_LEVEL_IDS = [277, 278, 279, 1286, 1287, 1288]

# Attribute ID → name mapping
_ATTR_NAMES = {
    164: "charisma",
    165: "intelligence",
    166: "memory",
    167: "perception",
    168: "willpower",
}

# SP required to reach each level (cumulative)
_SP_FOR_LEVEL = [0, 250, 1415, 8000, 45255, 256000]

# Category ID for skills
_SKILL_CATEGORY_ID = 16


@dataclass
class SkillInfo:
    """SDE-based skill information."""
    type_id: int
    name: str
    group_name: str
    rank: float  # skillTimeConstant
    primary_attr: str  # e.g. "perception"
    secondary_attr: str  # e.g. "willpower"
    prerequisites: list[tuple[int, int]]  # [(type_id, level), ...]
    description: str = ""


@dataclass
class PlanEntry:
    """A single entry in a skill plan."""
    type_id: int
    skill_name: str
    target_level: int
    current_level: int = 0
    current_sp: int = 0
    training_time_seconds: float = 0.0
    notes: str = ""

    @property
    def target_sp(self) -> int:
        """Total SP needed for target level (with rank applied elsewhere)."""
        return _SP_FOR_LEVEL[self.target_level] if self.target_level <= 5 else 0


@dataclass
class SkillPlan:
    """A named skill plan."""
    name: str
    entries: list[PlanEntry] = field(default_factory=list)
    created: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def total_time_seconds(self) -> float:
        return sum(e.training_time_seconds for e in self.entries)

    @property
    def total_time_display(self) -> str:
        return _format_duration(self.total_time_seconds)


def _format_duration(seconds: float) -> str:
    """Human-readable duration string."""
    if seconds <= 0:
        return "fertig"
    d = int(seconds // 86400)
    h = int((seconds % 86400) // 3600)
    m = int((seconds % 3600) // 60)
    parts = []
    if d:
        parts.append(f"{d}d")
    if h:
        parts.append(f"{h}h")
    if m or not parts:
        parts.append(f"{m}m")
    return " ".join(parts)


class SkillPlanner:
    """Skill training time calculator.

    EVE training time formula:
        SP/min = primary_attr + secondary_attr / 2
        training_time = (target_sp - current_sp) / (SP/min)
    where SP per level = base_sp * rank
    """

    def __init__(self, sde: SDEDatabase) -> None:
        self.sde = sde
        self._skill_cache: dict[int, SkillInfo] = {}

    def get_all_skills(self) -> list[SkillInfo]:
        """Get all trainable skills from SDE, grouped by category."""
        if self._skill_cache:
            return list(self._skill_cache.values())

        rows = self.sde._get_rows(
            """SELECT t.type_id, t.name_en, g.name_en as group_name, t.description_en
               FROM types t
               JOIN groups g ON g.group_id = t.group_id
               WHERE g.category_id = ?
               AND t.published = 1
               ORDER BY g.name_en, t.name_en""",
            (_SKILL_CATEGORY_ID,),
        )
        for row in rows:
            info = self._build_skill_info(row)
            if info:
                self._skill_cache[info.type_id] = info

        return list(self._skill_cache.values())

    def get_skill_info(self, type_id: int) -> SkillInfo | None:
        """Get skill info for a specific type."""
        if type_id in self._skill_cache:
            return self._skill_cache[type_id]

        row = self.sde._get_row(
            """SELECT t.type_id, t.name_en, g.name_en as group_name, t.description_en
               FROM types t
               JOIN groups g ON g.group_id = t.group_id
               WHERE t.type_id = ? AND g.category_id = ?""",
            (type_id, _SKILL_CATEGORY_ID),
        )
        if not row:
            return None
        info = self._build_skill_info(row)
        if info:
            self._skill_cache[type_id] = info
        return info

    def get_skill_groups(self) -> dict[str, list[SkillInfo]]:
        """Get all skills grouped by group name."""
        skills = self.get_all_skills()
        groups: dict[str, list[SkillInfo]] = {}
        for s in skills:
            groups.setdefault(s.group_name, []).append(s)
        return groups

    def calculate_training_time(
        self,
        type_id: int,
        from_level: int,
        to_level: int,
        attributes: dict[str, int],
    ) -> float:
        """Calculate training time in seconds.

        Args:
            type_id: Skill type ID
            from_level: Current skill level (0-4)
            to_level: Target skill level (1-5)
            attributes: Character attributes dict
                {"intelligence": N, "memory": N, "perception": N,
                 "willpower": N, "charisma": N}

        Returns:
            Training time in seconds.
        """
        info = self.get_skill_info(type_id)
        if not info or to_level <= from_level:
            return 0.0

        primary_val = attributes.get(info.primary_attr, 17)
        secondary_val = attributes.get(info.secondary_attr, 17)

        # SP per minute
        sp_per_min = primary_val + secondary_val / 2.0

        total_seconds = 0.0
        for level in range(from_level + 1, to_level + 1):
            sp_needed = _SP_FOR_LEVEL[level] * info.rank
            sp_have = _SP_FOR_LEVEL[level - 1] * info.rank if level > 1 else 0
            # If from_level == level-1, we might have partial SP, but for planning
            # we assume starting from level completion
            delta_sp = sp_needed - sp_have
            minutes = delta_sp / sp_per_min if sp_per_min > 0 else 999999
            total_seconds += minutes * 60

        return total_seconds

    def calculate_plan_times(
        self,
        plan: SkillPlan,
        attributes: dict[str, int],
        trained_skills: dict[int, int] | None = None,
    ) -> None:
        """Calculate training times for all entries in a plan.

        Args:
            plan: The skill plan to update
            attributes: Character attributes
            trained_skills: Dict of {type_id: current_level} for already trained skills
        """
        trained = trained_skills or {}

        for entry in plan.entries:
            current = trained.get(entry.type_id, 0)
            entry.current_level = current
            if current >= entry.target_level:
                entry.training_time_seconds = 0.0
            else:
                entry.training_time_seconds = self.calculate_training_time(
                    entry.type_id, current, entry.target_level, attributes
                )

    def get_prerequisites_tree(
        self, type_id: int, target_level: int = 1
    ) -> list[tuple[int, str, int]]:
        """Get all prerequisites recursively.

        Returns:
            List of (type_id, name, required_level) in dependency order.
        """
        result: list[tuple[int, str, int]] = []
        visited: set[tuple[int, int]] = set()
        self._collect_prereqs(type_id, target_level, result, visited)
        return result

    def _collect_prereqs(
        self,
        type_id: int,
        level: int,
        result: list[tuple[int, str, int]],
        visited: set[tuple[int, int]],
    ) -> None:
        """Recursively collect prerequisites."""
        info = self.get_skill_info(type_id)
        if not info:
            return

        for req_id, req_level in info.prerequisites:
            if (req_id, req_level) in visited:
                continue
            visited.add((req_id, req_level))
            # First add sub-prerequisites
            self._collect_prereqs(req_id, req_level, result, visited)
            req_info = self.get_skill_info(req_id)
            if req_info:
                result.append((req_id, req_info.name, req_level))

    def _build_skill_info(self, row: Any) -> SkillInfo | None:
        """Build SkillInfo from a DB row + dogma attributes."""
        type_id = row["type_id"]
        attrs = self.sde.get_type_dogma_attributes(type_id)

        # Build lookup
        attr_map: dict[int, float] = {}
        for a in attrs:
            attr_map[a["attribute_id"]] = a["value"]

        rank = attr_map.get(_TIME_CONSTANT, 1.0)
        primary_id = int(attr_map.get(_PRIMARY_ATTR, 165))
        secondary_id = int(attr_map.get(_SECONDARY_ATTR, 166))

        primary_name = _ATTR_NAMES.get(primary_id, "intelligence")
        secondary_name = _ATTR_NAMES.get(secondary_id, "memory")

        # Prerequisites
        prereqs: list[tuple[int, int]] = []
        for sid, lid in zip(_REQ_SKILL_IDS, _REQ_LEVEL_IDS):
            req_type = attr_map.get(sid)
            req_level = attr_map.get(lid)
            if req_type and req_level:
                prereqs.append((int(req_type), int(req_level)))

        return SkillInfo(
            type_id=type_id,
            name=row["name_en"] or f"Skill #{type_id}",
            group_name=row["group_name"] or "Unknown",
            rank=rank,
            primary_attr=primary_name,
            secondary_attr=secondary_name,
            prerequisites=prereqs,
            description=row["description_en"] or "",
        )


def format_training_time(seconds: float) -> str:
    """Format training time for display."""
    return _format_duration(seconds)
