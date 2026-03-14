"""Configuration management for PyMon."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

import appdirs

logger = logging.getLogger(__name__)

APP_NAME = "PyMon"
APP_AUTHOR = "PyMon"

# ESI API settings
ESI_BASE_URL = "https://esi.evetech.net/latest"
ESI_AUTH_URL = "https://login.eveonline.com/v2/oauth/authorize"
ESI_TOKEN_URL = "https://login.eveonline.com/v2/oauth/token"
ESI_JWKS_URL = "https://login.eveonline.com/oauth/jwks"
SSO_CALLBACK_PORT = 8182
SSO_CALLBACK_URL = f"http://localhost:{SSO_CALLBACK_PORT}/callback"

# Default ESI scopes for character monitoring
DEFAULT_SCOPES = [
    # -- Skills --
    "esi-skills.read_skills.v1",
    "esi-skills.read_skillqueue.v1",
    # -- Clones --
    "esi-clones.read_clones.v1",
    "esi-clones.read_implants.v1",
    # -- Assets --
    "esi-assets.read_assets.v1",
    # -- Wallet --
    "esi-wallet.read_character_wallet.v1",
    # -- Mail --
    "esi-mail.read_mail.v1",
    "esi-mail.organize_mail.v1",
    "esi-mail.send_mail.v1",
    # -- Calendar --
    "esi-calendar.read_calendar_events.v1",
    "esi-calendar.respond_calendar_events.v1",
    # -- Location --
    "esi-location.read_location.v1",
    "esi-location.read_ship_type.v1",
    "esi-location.read_online.v1",
    # -- Fittings --
    "esi-fittings.read_fittings.v1",
    "esi-fittings.write_fittings.v1",
    # -- Markets --
    "esi-markets.read_character_orders.v1",
    "esi-markets.structure_markets.v1",
    # -- Industry --
    "esi-industry.read_character_jobs.v1",
    "esi-industry.read_character_mining.v1",
    "esi-industry.read_corporation_mining.v1",
    # -- Contracts --
    "esi-contracts.read_character_contracts.v1",
    "esi-contracts.read_corporation_contracts.v1",
    # -- Killmails --
    "esi-killmails.read_killmails.v1",
    "esi-killmails.read_corporation_killmails.v1",
    # -- Characters --
    "esi-characters.read_contacts.v1",
    "esi-characters.write_contacts.v1",
    "esi-characters.read_standings.v1",
    "esi-characters.read_blueprints.v1",
    "esi-characters.read_notifications.v1",
    "esi-characters.read_loyalty.v1",
    "esi-characters.read_medals.v1",
    "esi-characters.read_titles.v1",
    "esi-characters.read_fatigue.v1",
    "esi-characters.read_fw_stats.v1",
    "esi-characters.read_agents_research.v1",
    # -- Planets (PI) --
    "esi-planets.manage_planets.v1",
    "esi-planets.read_customs_offices.v1",
    # -- Corporations --
    "esi-corporations.read_contacts.v1",
    "esi-corporations.read_blueprints.v1",
    "esi-corporations.read_standings.v1",
    "esi-corporations.read_starbases.v1",
    "esi-corporations.read_structures.v1",
    "esi-corporations.read_titles.v1",
    "esi-corporations.read_medals.v1",
    "esi-corporations.read_facilities.v1",
    "esi-corporations.read_fw_stats.v1",
    "esi-corporations.read_container_logs.v1",
    "esi-corporations.read_divisions.v1",
    "esi-corporations.track_members.v1",
    # -- Fleets --
    "esi-fleets.read_fleet.v1",
    "esi-fleets.write_fleet.v1",
    # -- Search --
    "esi-search.search_structures.v1",
    # -- Universe / Structures --
    "esi-universe.read_structures.v1",
    # -- UI --
    "esi-ui.open_window.v1",
    "esi-ui.write_waypoint.v1",
    # -- Alliances --
    "esi-alliances.read_contacts.v1",
]


@dataclass
class Config:
    """Application configuration."""

    # EVE SSO
    client_id: str = ""
    scopes: list[str] = field(default_factory=lambda: DEFAULT_SCOPES.copy())

    # Paths
    data_dir: Path = field(default_factory=lambda: Path(appdirs.user_data_dir(APP_NAME, APP_AUTHOR)))
    config_file: Path = field(default=Path(""))
    db_path: Path = field(default=Path(""))
    sde_db_path: Path = field(default=Path(""))

    # UI
    language: str = "en"
    debug: bool = False
    refresh_interval_minutes: int = 5

    # Tray Notifications
    tray_notify_skill_complete: bool = True
    tray_notify_queue_empty: bool = True
    tray_show_popup_duration: int = 5  # seconds

    # Email Notifications
    email_enabled: bool = False
    email_smtp_server: str = ""
    email_smtp_port: int = 587
    email_smtp_user: str = ""
    email_smtp_password: str = ""
    email_to: str = ""
    email_use_tls: bool = True

    # Cloud Sync
    cloud_sync_path: str = ""

    # Auto-Update
    auto_update_check: bool = True

    def __post_init__(self) -> None:
        """Set derived paths and load from file if exists."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.data_dir / "config.json"
        self.db_path = self.data_dir / "pymon.db"
        self.sde_db_path = self.data_dir / "sde.db"

        if self.config_file.exists():
            self._load()

    def _load(self) -> None:
        """Load configuration from JSON file."""
        try:
            data = json.loads(self.config_file.read_text(encoding="utf-8"))
            self.client_id = data.get("client_id", self.client_id)
            saved_scopes = data.get("scopes", [])
            # Merge: keep any user-custom scopes AND add new defaults
            merged = list(dict.fromkeys(DEFAULT_SCOPES + saved_scopes))
            self.scopes = merged
            self.language = data.get("language", self.language)
            self.debug = data.get("debug", self.debug)
            self.refresh_interval_minutes = data.get("refresh_interval_minutes", self.refresh_interval_minutes)
            self.tray_notify_skill_complete = data.get("tray_notify_skill_complete", self.tray_notify_skill_complete)
            self.tray_notify_queue_empty = data.get("tray_notify_queue_empty", self.tray_notify_queue_empty)
            self.tray_show_popup_duration = data.get("tray_show_popup_duration", self.tray_show_popup_duration)
            # Email
            self.email_enabled = data.get("email_enabled", self.email_enabled)
            self.email_smtp_server = data.get("email_smtp_server", self.email_smtp_server)
            self.email_smtp_port = data.get("email_smtp_port", self.email_smtp_port)
            self.email_smtp_user = data.get("email_smtp_user", self.email_smtp_user)
            self.email_smtp_password = data.get("email_smtp_password", self.email_smtp_password)
            self.email_to = data.get("email_to", self.email_to)
            self.email_use_tls = data.get("email_use_tls", self.email_use_tls)
            # Cloud Sync
            self.cloud_sync_path = data.get("cloud_sync_path", self.cloud_sync_path)
            # Auto-Update
            self.auto_update_check = data.get("auto_update_check", self.auto_update_check)
            logger.info("Configuration loaded from %s", self.config_file)
        except Exception:
            logger.warning("Failed to load config from %s", self.config_file, exc_info=True)

    def save(self) -> None:
        """Save configuration to JSON file."""
        data = {
            "client_id": self.client_id,
            "scopes": self.scopes,
            "language": self.language,
            "debug": self.debug,
            "refresh_interval_minutes": self.refresh_interval_minutes,
            "tray_notify_skill_complete": self.tray_notify_skill_complete,
            "tray_notify_queue_empty": self.tray_notify_queue_empty,
            "tray_show_popup_duration": self.tray_show_popup_duration,
            "email_enabled": self.email_enabled,
            "email_smtp_server": self.email_smtp_server,
            "email_smtp_port": self.email_smtp_port,
            "email_smtp_user": self.email_smtp_user,
            "email_smtp_password": self.email_smtp_password,
            "email_to": self.email_to,
            "email_use_tls": self.email_use_tls,
            "cloud_sync_path": self.cloud_sync_path,
            "auto_update_check": self.auto_update_check,
        }
        self.config_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        logger.info("Configuration saved to %s", self.config_file)
