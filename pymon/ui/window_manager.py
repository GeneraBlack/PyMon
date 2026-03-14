"""Window Manager – persists multi-window layout across sessions.

Stores which tabs are detached, their position/size per monitor, and
restores the layout on application startup.  Data is saved in the
PyMon config directory as ``window_layout.json``.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from PySide6.QtCore import QRect
from PySide6.QtWidgets import QApplication

logger = logging.getLogger(__name__)


class WindowLayout:
    """Serialisable snapshot of the window arrangement."""

    def __init__(self) -> None:
        # Main window geometry
        self.main_geometry: dict[str, int] = {}
        self.main_maximized: bool = False

        # Detached tabs: title → {x, y, w, h}
        self.detached_tabs: dict[str, dict[str, int]] = {}

        # Current tab index in main window
        self.active_tab: int = 0

        # Active tab name (for sidebar sync)
        self.active_tab_name: str = ""

        # Splitter sizes (left panel vs tabs)
        self.splitter_sizes: list[int] = []

        # Collapsed sidebar groups (list of group keys)
        self.collapsed_groups: list[str] = []

        # Detached groups: group_key → {x, y, w, h}
        self.detached_groups: dict[str, dict[str, int]] = {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "main_geometry": self.main_geometry,
            "main_maximized": self.main_maximized,
            "detached_tabs": self.detached_tabs,
            "active_tab": self.active_tab,
            "active_tab_name": self.active_tab_name,
            "splitter_sizes": self.splitter_sizes,
            "collapsed_groups": self.collapsed_groups,
            "detached_groups": self.detached_groups,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WindowLayout":
        layout = cls()
        layout.main_geometry = data.get("main_geometry", {})
        layout.main_maximized = data.get("main_maximized", False)
        layout.detached_tabs = data.get("detached_tabs", {})
        layout.active_tab = data.get("active_tab", 0)
        layout.active_tab_name = data.get("active_tab_name", "")
        layout.splitter_sizes = data.get("splitter_sizes", [])
        layout.collapsed_groups = data.get("collapsed_groups", [])
        layout.detached_groups = data.get("detached_groups", {})
        return layout


class WindowManager:
    """Manages window layout persistence.

    Usage:
        wm = WindowManager(config.data_dir)
        layout = wm.load()           # on startup
        # … apply layout …
        wm.save(layout)              # on shutdown
    """

    FILENAME = "window_layout.json"

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self._file = data_dir / self.FILENAME

    def load(self) -> WindowLayout:
        """Load saved layout or return defaults."""
        if not self._file.exists():
            return WindowLayout()
        try:
            data = json.loads(self._file.read_text(encoding="utf-8"))
            layout = WindowLayout.from_dict(data)
            # Validate geometries against current screens
            layout.detached_tabs = self._validate_geometries(layout.detached_tabs)
            if layout.main_geometry:
                validated = self._validate_single_geometry(layout.main_geometry)
                layout.main_geometry = validated if validated else {}
            logger.info("Window layout loaded from %s", self._file)
            return layout
        except Exception as e:
            logger.warning("Failed to load window layout: %s", e)
            return WindowLayout()

    def save(self, layout: WindowLayout) -> None:
        """Save layout to disk."""
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            self._file.write_text(
                json.dumps(layout.to_dict(), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            logger.debug("Window layout saved to %s", self._file)
        except Exception as e:
            logger.warning("Failed to save window layout: %s", e)

    @staticmethod
    def _validate_geometries(
        geoms: dict[str, dict[str, int]],
    ) -> dict[str, dict[str, int]]:
        """Remove geometries that are completely off-screen."""
        app = QApplication.instance()
        if not app:
            return geoms

        screens = app.screens()
        if not screens:
            return geoms

        # Build union of all screen geometries
        valid: dict[str, dict[str, int]] = {}
        for title, g in geoms.items():
            rect = QRect(g.get("x", 0), g.get("y", 0), g.get("w", 900), g.get("h", 650))
            if WindowManager._is_visible_on_any_screen(rect, screens):
                valid[title] = g
            else:
                logger.info(
                    "Discarding off-screen geometry for '%s': %s", title, g
                )
        return valid

    @staticmethod
    def _validate_single_geometry(g: dict[str, int]) -> dict[str, int] | None:
        """Validate a single geometry dict."""
        app = QApplication.instance()
        if not app:
            return g
        screens = app.screens()
        if not screens:
            return g
        rect = QRect(g.get("x", 0), g.get("y", 0), g.get("w", 1400), g.get("h", 900))
        if WindowManager._is_visible_on_any_screen(rect, screens):
            return g
        return None

    @staticmethod
    def _is_visible_on_any_screen(rect: QRect, screens: list) -> bool:
        """Check if at least 100px of the rect is visible on any screen."""
        for screen in screens:
            avail = screen.availableGeometry()
            intersection = rect.intersected(avail)
            if intersection.width() >= 100 and intersection.height() >= 100:
                return True
        return False

    @staticmethod
    def get_screen_info() -> list[dict[str, Any]]:
        """Return info about all connected screens (useful for debugging)."""
        app = QApplication.instance()
        if not app:
            return []
        result = []
        for screen in app.screens():
            g = screen.availableGeometry()
            result.append({
                "name": screen.name(),
                "x": g.x(), "y": g.y(),
                "w": g.width(), "h": g.height(),
                "dpi": screen.logicalDotsPerInch(),
            })
        return result
