"""Character service – orchestrates character data fetching and storage."""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any

from pymon.api.assets import AssetsAPI
from pymon.api.blueprints import BlueprintsAPI
from pymon.api.bookmarks import BookmarksAPI
from pymon.api.calendar import CalendarAPI
from pymon.api.character import CharacterAPI
from pymon.api.clones import ClonesAPI
from pymon.api.contacts import ContactsAPI
from pymon.api.contracts import ContractsAPI
from pymon.api.esi_client import ESIClient
from pymon.api.fatigue import FatigueAPI
from pymon.api.fittings import FittingsAPI
from pymon.api.fw import FactionWarfareAPI
from pymon.api.industry import IndustryAPI
from pymon.api.killmails import KillmailsAPI
from pymon.api.location import LocationAPI
from pymon.api.loyalty import LoyaltyAPI
from pymon.api.mail import MailAPI
from pymon.api.market import MarketAPI
from pymon.api.mining import MiningAPI
from pymon.api.notifications import NotificationsAPI
from pymon.api.planets import PlanetsAPI
from pymon.api.research import ResearchAPI
from pymon.api.skills import SkillsAPI
from pymon.api.universe import UniverseAPI
from pymon.api.wallet import WalletAPI
from pymon.auth.token_manager import TokenManager
from pymon.core.database import Database
from pymon.models.blueprints import Blueprint
from pymon.models.character import Character, Clone, SkillInfo, SkillQueueEntry
from pymon.models.contacts import Contact, Standing
from pymon.models.contracts import Contract
from pymon.models.fittings import Fitting, FittingItem
from pymon.models.industry import IndustryJob, MiningEntry
from pymon.models.killmails import Killmail, KillmailAttacker, KillmailItem, KillmailSummary, KillmailVictim
from pymon.models.mail import MailHeader, MailLabel
from pymon.models.market import LoyaltyPoints, MarketOrder, WalletJournalEntry, WalletTransaction
from pymon.models.misc import AgentResearch, AssetItem, Bookmark, CalendarEvent, JumpFatigue, Medal
from pymon.models.notifications import Notification
from pymon.models.planets import PlanetaryColony
from pymon.sde.database import SDEDatabase

logger = logging.getLogger(__name__)


class CharacterService:
    """High-level service for character data management.

    Coordinates between ESI API calls, token management,
    SDE lookups, and local database storage.
    """

    def __init__(
        self,
        esi: ESIClient,
        token_manager: TokenManager,
        db: Database,
        sde: SDEDatabase,
    ) -> None:
        self.token_manager = token_manager
        self.db = db
        self.sde = sde

        # API sub-clients
        self.character_api = CharacterAPI(esi)
        self.skills_api = SkillsAPI(esi)
        self.location_api = LocationAPI(esi)
        self.wallet_api = WalletAPI(esi)
        self.clones_api = ClonesAPI(esi)
        self.mail_api = MailAPI(esi)
        self.contracts_api = ContractsAPI(esi)
        self.fittings_api = FittingsAPI(esi)
        self.industry_api = IndustryAPI(esi)
        self.killmails_api = KillmailsAPI(esi)
        self.assets_api = AssetsAPI(esi)
        self.market_api = MarketAPI(esi)
        self.blueprints_api = BlueprintsAPI(esi)
        self.contacts_api = ContactsAPI(esi)
        self.notifications_api = NotificationsAPI(esi)
        self.calendar_api = CalendarAPI(esi)
        self.planets_api = PlanetsAPI(esi)
        self.loyalty_api = LoyaltyAPI(esi)
        self.mining_api = MiningAPI(esi)
        self.bookmarks_api = BookmarksAPI(esi)
        self.fatigue_api = FatigueAPI(esi)
        self.fw_api = FactionWarfareAPI(esi)
        self.research_api = ResearchAPI(esi)
        self.universe_api = UniverseAPI(esi)

    async def fetch_character_overview(self, character_id: int) -> Character | None:
        """Fetch full character overview from ESI.

        Combines data from multiple endpoints into a single Character model.
        """
        token = await self.token_manager.get_valid_token(character_id)
        if not token:
            logger.warning("No valid token for character %d", character_id)
            return None

        logger.info("Fetching overview for character %d", character_id)

        # Fetch data in parallel – each coroutine uses its own httpx client,
        # so asyncio.gather is safe here.
        import asyncio

        try:
            (
                char_info,
                skills_data,
                location_data,
                ship_data,
                wallet_balance,
                online_data,
            ) = await asyncio.gather(
                self.character_api.get_character(character_id),
                self.skills_api.get_skills(character_id, token),
                self.location_api.get_location(character_id, token),
                self.location_api.get_ship(character_id, token),
                self.wallet_api.get_balance(character_id, token),
                self.location_api.get_online(character_id, token),
            )
        except Exception:
            logger.error("Failed to fetch data for character %d", character_id, exc_info=True)
            return None

        logger.info("Got char_info: %s", char_info)

        # Resolve names from SDE
        system_id = location_data.get("solar_system_id", 0)
        system_name = self.sde.get_system_name(system_id) if system_id else ""
        ship_type_name = self.sde.get_type_name(ship_data.get("ship_type_id", 0))

        # Get character name from stored data
        stored = self.db.conn.execute(
            "SELECT character_name FROM characters WHERE character_id = ?",
            (character_id,),
        ).fetchone()

        character = Character(
            character_id=character_id,
            character_name=stored["character_name"] if stored else char_info.get("name", "Unknown"),
            corporation_id=char_info.get("corporation_id", 0),
            alliance_id=char_info.get("alliance_id"),
            birthday=char_info.get("birthday", ""),
            security_status=char_info.get("security_status", 0.0),
            solar_system_id=system_id,
            solar_system_name=system_name,
            station_id=location_data.get("station_id") or location_data.get("structure_id"),
            ship_type_id=ship_data.get("ship_type_id", 0),
            ship_name=ship_data.get("ship_name", ship_type_name),
            is_online=online_data.get("online", False),
            total_sp=skills_data.get("total_sp", 0),
            unallocated_sp=skills_data.get("unallocated_sp", 0),
            wallet_balance=wallet_balance if isinstance(wallet_balance, (int, float)) else 0.0,
            last_updated=datetime.now(timezone.utc),
        )

        return character

    async def fetch_skill_queue(self, character_id: int) -> list[SkillQueueEntry]:
        """Fetch the skill training queue."""
        token = await self.token_manager.get_valid_token(character_id)
        if not token:
            return []

        try:
            queue_data = await self.skills_api.get_skill_queue(character_id, token)
        except Exception:
            logger.error("Failed to fetch skill queue", exc_info=True)
            return []

        entries: list[SkillQueueEntry] = []
        for item in queue_data:
            skill_name = self.sde.get_type_name(item.get("skill_id", 0))
            entry = SkillQueueEntry(
                skill_id=item.get("skill_id", 0),
                skill_name=skill_name,
                finished_level=item.get("finished_level", 0),
                queue_position=item.get("queue_position", 0),
                start_date=_parse_date(item.get("start_date")),
                finish_date=_parse_date(item.get("finish_date")),
                training_start_sp=item.get("training_start_sp", 0),
                level_start_sp=item.get("level_start_sp", 0),
                level_end_sp=item.get("level_end_sp", 0),
            )
            entries.append(entry)

        return entries

    async def fetch_skills(self, character_id: int) -> list[SkillInfo]:
        """Fetch all trained skills."""
        token = await self.token_manager.get_valid_token(character_id)
        if not token:
            return []

        try:
            skills_data = await self.skills_api.get_skills(character_id, token)
        except Exception:
            logger.error("Failed to fetch skills", exc_info=True)
            return []

        skills: list[SkillInfo] = []
        for item in skills_data.get("skills", []):
            skill_id = item.get("skill_id", 0)
            skill_name = self.sde.get_type_name(skill_id)

            # Get group name from SDE
            type_info = self.sde.get_type(skill_id)
            group_name = ""
            if type_info and type_info.get("group_id"):
                group = self.sde.get_group(type_info["group_id"])
                group_name = group.get("name_en", "") if group else ""

            skill = SkillInfo(
                skill_id=skill_id,
                skill_name=skill_name,
                group_name=group_name,
                active_skill_level=item.get("active_skill_level", 0),
                trained_skill_level=item.get("trained_skill_level", 0),
                skillpoints_in_skill=item.get("skillpoints_in_skill", 0),
            )
            skills.append(skill)

        return skills


    # ──────────────────────────────────────────────────────────────────
    #  Mail
    # ──────────────────────────────────────────────────────────────────

    async def fetch_mail(self, character_id: int) -> list[MailHeader]:
        """Fetch mail headers."""
        token = await self.token_manager.get_valid_token(character_id)
        if not token:
            return []
        try:
            data = await self.mail_api.get_mail_headers(character_id, token)
        except Exception:
            logger.error("Failed to fetch mail", exc_info=True)
            return []
        headers: list[MailHeader] = []
        for item in data:
            headers.append(MailHeader(
                mail_id=item.get("mail_id", 0),
                subject=item.get("subject", ""),
                from_id=item.get("from", 0),
                timestamp=_parse_date(item.get("timestamp")),
                is_read=item.get("is_read", False),
                labels=item.get("labels", []),
            ))
        return headers

    async def fetch_mail_labels(self, character_id: int) -> list[MailLabel]:
        """Fetch mail labels."""
        token = await self.token_manager.get_valid_token(character_id)
        if not token:
            return []
        try:
            data = await self.mail_api.get_mail_labels(character_id, token)
        except Exception:
            logger.error("Failed to fetch mail labels", exc_info=True)
            return []
        labels: list[MailLabel] = []
        for item in data.get("labels", []):
            labels.append(MailLabel(
                label_id=item.get("label_id", 0),
                name=item.get("name", ""),
                color=item.get("color", ""),
                unread_count=item.get("unread_count", 0),
            ))
        return labels

    # ──────────────────────────────────────────────────────────────────
    #  Contracts
    # ──────────────────────────────────────────────────────────────────

    async def fetch_contracts(self, character_id: int) -> list[Contract]:
        """Fetch character contracts."""
        token = await self.token_manager.get_valid_token(character_id)
        if not token:
            return []
        try:
            data = await self.contracts_api.get_contracts(character_id, token)
        except Exception:
            logger.error("Failed to fetch contracts", exc_info=True)
            return []
        contracts: list[Contract] = []
        for item in data:
            contracts.append(Contract(
                contract_id=item.get("contract_id", 0),
                issuer_id=item.get("issuer_id", 0),
                issuer_corporation_id=item.get("issuer_corporation_id", 0),
                assignee_id=item.get("assignee_id", 0),
                acceptor_id=item.get("acceptor_id", 0),
                contract_type=item.get("type", ""),
                status=item.get("status", ""),
                title=item.get("title", ""),
                price=item.get("price", 0.0),
                reward=item.get("reward", 0.0),
                collateral=item.get("collateral", 0.0),
                buyout=item.get("buyout", 0.0),
                volume=item.get("volume", 0.0),
                days_to_complete=item.get("days_to_complete", 0),
                date_issued=_parse_date(item.get("date_issued")),
                date_expired=_parse_date(item.get("date_expired")),
                date_accepted=_parse_date(item.get("date_accepted")),
                date_completed=_parse_date(item.get("date_completed")),
                for_corporation=item.get("for_corporation", False),
                availability=item.get("availability", ""),
            ))
        return contracts

    # ──────────────────────────────────────────────────────────────────
    #  Industry Jobs
    # ──────────────────────────────────────────────────────────────────

    async def fetch_industry_jobs(self, character_id: int) -> list[IndustryJob]:
        """Fetch character industry jobs."""
        token = await self.token_manager.get_valid_token(character_id)
        if not token:
            return []
        try:
            data = await self.industry_api.get_character_jobs(character_id, token)
        except Exception:
            logger.error("Failed to fetch industry jobs", exc_info=True)
            return []
        jobs: list[IndustryJob] = []
        for item in data:
            bp_type_id = item.get("blueprint_type_id", 0)
            product_type_id = item.get("product_type_id", 0)
            jobs.append(IndustryJob(
                job_id=item.get("job_id", 0),
                installer_id=item.get("installer_id", 0),
                facility_id=item.get("facility_id", 0),
                station_id=item.get("station_id", 0),
                activity_id=item.get("activity_id", 0),
                blueprint_id=item.get("blueprint_id", 0),
                blueprint_type_id=bp_type_id,
                blueprint_type_name=self.sde.get_type_name(bp_type_id),
                product_type_id=product_type_id,
                product_type_name=self.sde.get_type_name(product_type_id) if product_type_id else "",
                status=item.get("status", ""),
                runs=item.get("runs", 0),
                licensed_runs=item.get("licensed_runs", 0),
                cost=item.get("cost", 0.0),
                start_date=_parse_date(item.get("start_date")),
                end_date=_parse_date(item.get("end_date")),
                completed_date=_parse_date(item.get("completed_date")),
                probability=item.get("probability", 0.0),
                successful_runs=item.get("successful_runs"),
            ))
        return jobs

    # ──────────────────────────────────────────────────────────────────
    #  Fittings
    # ──────────────────────────────────────────────────────────────────

    async def fetch_fittings(self, character_id: int) -> list[Fitting]:
        """Fetch saved fittings."""
        token = await self.token_manager.get_valid_token(character_id)
        if not token:
            return []
        try:
            data = await self.fittings_api.get_fittings(character_id, token)
        except Exception:
            logger.error("Failed to fetch fittings", exc_info=True)
            return []
        fittings: list[Fitting] = []
        for item in data:
            ship_type_id = item.get("ship_type_id", 0)
            items = [
                FittingItem(
                    type_id=fi.get("type_id", 0),
                    type_name=self.sde.get_type_name(fi.get("type_id", 0)),
                    flag=fi.get("flag", ""),
                    quantity=fi.get("quantity", 1),
                )
                for fi in item.get("items", [])
            ]
            fittings.append(Fitting(
                fitting_id=item.get("fitting_id", 0),
                name=item.get("name", ""),
                description=item.get("description", ""),
                ship_type_id=ship_type_id,
                ship_type_name=self.sde.get_type_name(ship_type_id),
                items=items,
            ))
        return fittings

    # ──────────────────────────────────────────────────────────────────
    #  Market Orders
    # ──────────────────────────────────────────────────────────────────

    async def fetch_market_orders(self, character_id: int) -> list[MarketOrder]:
        """Fetch active character market orders."""
        token = await self.token_manager.get_valid_token(character_id)
        if not token:
            return []
        try:
            data = await self.market_api.get_character_orders(character_id, token)
        except Exception:
            logger.error("Failed to fetch market orders", exc_info=True)
            return []
        orders: list[MarketOrder] = []
        for item in data:
            type_id = item.get("type_id", 0)
            orders.append(MarketOrder(
                order_id=item.get("order_id", 0),
                type_id=type_id,
                type_name=self.sde.get_type_name(type_id),
                location_id=item.get("location_id", 0),
                region_id=item.get("region_id", 0),
                is_buy_order=item.get("is_buy_order", False),
                price=item.get("price", 0.0),
                volume_remain=item.get("volume_remain", 0),
                volume_total=item.get("volume_total", 0),
                min_volume=item.get("min_volume", 1),
                duration=item.get("duration", 0),
                issued=_parse_date(item.get("issued")),
                escrow=item.get("escrow", 0.0),
                range=item.get("range", ""),
            ))
        return orders

    # ──────────────────────────────────────────────────────────────────
    #  Killmails
    # ──────────────────────────────────────────────────────────────────

    async def fetch_killmail_summaries(self, character_id: int) -> list[KillmailSummary]:
        """Fetch killmail summary list (ID + hash)."""
        token = await self.token_manager.get_valid_token(character_id)
        if not token:
            return []
        try:
            data = await self.killmails_api.get_character_killmails(character_id, token)
        except Exception:
            logger.error("Failed to fetch killmails", exc_info=True)
            return []
        return [
            KillmailSummary(
                killmail_id=item.get("killmail_id", 0),
                killmail_hash=item.get("killmail_hash", ""),
            )
            for item in data
        ]

    # ──────────────────────────────────────────────────────────────────
    #  Assets
    # ──────────────────────────────────────────────────────────────────

    async def fetch_assets(self, character_id: int) -> list[AssetItem]:
        """Fetch character assets (first page)."""
        token = await self.token_manager.get_valid_token(character_id)
        if not token:
            return []
        try:
            data = await self.assets_api.get_assets(character_id, token)
        except Exception:
            logger.error("Failed to fetch assets", exc_info=True)
            return []
        assets: list[AssetItem] = []
        for item in data:
            type_id = item.get("type_id", 0)
            assets.append(AssetItem(
                item_id=item.get("item_id", 0),
                type_id=type_id,
                type_name=self.sde.get_type_name(type_id),
                location_id=item.get("location_id", 0),
                location_type=item.get("location_type", ""),
                location_flag=item.get("location_flag", ""),
                quantity=item.get("quantity", 1),
                is_singleton=item.get("is_singleton", False),
                is_blueprint_copy=item.get("is_blueprint_copy"),
            ))
        return assets

    # ──────────────────────────────────────────────────────────────────
    #  Blueprints
    # ──────────────────────────────────────────────────────────────────

    async def fetch_blueprints(self, character_id: int) -> list[Blueprint]:
        """Fetch character blueprints."""
        token = await self.token_manager.get_valid_token(character_id)
        if not token:
            return []
        try:
            data = await self.blueprints_api.get_character_blueprints(character_id, token)
        except Exception:
            logger.error("Failed to fetch blueprints", exc_info=True)
            return []
        bps: list[Blueprint] = []
        for item in data:
            type_id = item.get("type_id", 0)
            bps.append(Blueprint(
                item_id=item.get("item_id", 0),
                type_id=type_id,
                type_name=self.sde.get_type_name(type_id),
                location_id=item.get("location_id", 0),
                location_flag=item.get("location_flag", ""),
                quantity=item.get("quantity", 0),
                material_efficiency=item.get("material_efficiency", 0),
                time_efficiency=item.get("time_efficiency", 0),
                runs=item.get("runs", 0),
            ))
        return bps

    # ──────────────────────────────────────────────────────────────────
    #  Contacts & Standings
    # ──────────────────────────────────────────────────────────────────

    async def fetch_contacts(self, character_id: int) -> list[Contact]:
        """Fetch character contacts."""
        token = await self.token_manager.get_valid_token(character_id)
        if not token:
            return []
        try:
            data = await self.contacts_api.get_contacts(character_id, token)
        except Exception:
            logger.error("Failed to fetch contacts", exc_info=True)
            return []
        return [
            Contact(
                contact_id=item.get("contact_id", 0),
                contact_type=item.get("contact_type", ""),
                standing=item.get("standing", 0.0),
                label_ids=item.get("label_ids", []),
                is_watched=item.get("is_watched", False),
                is_blocked=item.get("is_blocked", False),
            )
            for item in data
        ]

    async def fetch_standings(self, character_id: int) -> list[Standing]:
        """Fetch NPC standings."""
        token = await self.token_manager.get_valid_token(character_id)
        if not token:
            return []
        try:
            data = await self.contacts_api.get_standings(character_id, token)
        except Exception:
            logger.error("Failed to fetch standings", exc_info=True)
            return []
        return [
            Standing(
                from_id=item.get("from_id", 0),
                from_type=item.get("from_type", ""),
                standing=item.get("standing", 0.0),
            )
            for item in data
        ]

    # ──────────────────────────────────────────────────────────────────
    #  Notifications
    # ──────────────────────────────────────────────────────────────────

    async def fetch_notifications(self, character_id: int) -> list[Notification]:
        """Fetch notifications."""
        token = await self.token_manager.get_valid_token(character_id)
        if not token:
            return []
        try:
            data = await self.notifications_api.get_notifications(character_id, token)
        except Exception:
            logger.error("Failed to fetch notifications", exc_info=True)
            return []
        return [
            Notification(
                notification_id=item.get("notification_id", 0),
                type=item.get("type", ""),
                sender_id=item.get("sender_id", 0),
                sender_type=item.get("sender_type", ""),
                timestamp=_parse_date(item.get("timestamp")),
                text=item.get("text", ""),
                is_read=item.get("is_read", False),
            )
            for item in data
        ]

    # ──────────────────────────────────────────────────────────────────
    #  Calendar
    # ──────────────────────────────────────────────────────────────────

    async def fetch_calendar_events(self, character_id: int) -> list[CalendarEvent]:
        """Fetch upcoming calendar events."""
        token = await self.token_manager.get_valid_token(character_id)
        if not token:
            return []
        try:
            data = await self.calendar_api.get_events(character_id, token)
        except Exception:
            logger.error("Failed to fetch calendar", exc_info=True)
            return []
        return [
            CalendarEvent(
                event_id=item.get("event_id", 0),
                title=item.get("title", ""),
                event_date=_parse_date(item.get("event_date")),
                event_response=item.get("event_response", ""),
                importance=item.get("importance", 0),
            )
            for item in data
        ]

    # ──────────────────────────────────────────────────────────────────
    #  Planetary Interaction
    # ──────────────────────────────────────────────────────────────────

    async def fetch_planetary_colonies(self, character_id: int) -> list[PlanetaryColony]:
        """Fetch PI colonies."""
        token = await self.token_manager.get_valid_token(character_id)
        if not token:
            return []
        try:
            data = await self.planets_api.get_colonies(character_id, token)
        except Exception:
            logger.error("Failed to fetch PI colonies", exc_info=True)
            return []
        colonies: list[PlanetaryColony] = []
        for item in data:
            sys_id = item.get("solar_system_id", 0)
            colonies.append(PlanetaryColony(
                planet_id=item.get("planet_id", 0),
                solar_system_id=sys_id,
                solar_system_name=self.sde.get_system_name(sys_id) if sys_id else "",
                planet_type=item.get("planet_type", ""),
                owner_id=item.get("owner_id", 0),
                upgrade_level=item.get("upgrade_level", 0),
                num_pins=item.get("num_pins", 0),
                last_update=_parse_date(item.get("last_update")),
            ))
        return colonies

    # ──────────────────────────────────────────────────────────────────
    #  Clones & Implants
    # ──────────────────────────────────────────────────────────────────

    async def fetch_clones(self, character_id: int) -> list[Clone]:
        """Fetch jump clones."""
        token = await self.token_manager.get_valid_token(character_id)
        if not token:
            return []
        try:
            data = await self.clones_api.get_clones(character_id, token)
        except Exception:
            logger.error("Failed to fetch clones", exc_info=True)
            return []
        clones: list[Clone] = []
        for item in data.get("jump_clones", []):
            clones.append(Clone(
                jump_clone_id=item.get("jump_clone_id", 0),
                location_id=item.get("location_id", 0),
                location_type=item.get("location_type", ""),
                implants=item.get("implants", []),
            ))
        return clones

    async def fetch_implant_ids(self, character_id: int) -> list[int]:
        """Fetch active implant type IDs."""
        token = await self.token_manager.get_valid_token(character_id)
        if not token:
            return []
        try:
            return await self.clones_api.get_implants(character_id, token)
        except Exception:
            logger.error("Failed to fetch implant IDs", exc_info=True)
            return []

    async def fetch_implants(self, character_id: int) -> list[str]:
        """Fetch active implant names."""
        implant_ids = await self.fetch_implant_ids(character_id)
        return [self.sde.get_type_name(imp_id) for imp_id in implant_ids]

    # ──────────────────────────────────────────────────────────────────
    #  Loyalty Points
    # ──────────────────────────────────────────────────────────────────

    async def fetch_loyalty_points(self, character_id: int) -> list[LoyaltyPoints]:
        """Fetch LP balances."""
        token = await self.token_manager.get_valid_token(character_id)
        if not token:
            return []
        try:
            data = await self.loyalty_api.get_loyalty_points(character_id, token)
        except Exception:
            logger.error("Failed to fetch LP", exc_info=True)
            return []
        return [
            LoyaltyPoints(
                corporation_id=item.get("corporation_id", 0),
                loyalty_points=item.get("loyalty_points", 0),
            )
            for item in data
        ]

    # ──────────────────────────────────────────────────────────────────
    #  Wallet Journal & Transactions
    # ──────────────────────────────────────────────────────────────────

    async def fetch_wallet_journal(self, character_id: int) -> list[WalletJournalEntry]:
        """Fetch wallet journal."""
        token = await self.token_manager.get_valid_token(character_id)
        if not token:
            return []
        try:
            data = await self.wallet_api.get_journal(character_id, token)
        except Exception:
            logger.error("Failed to fetch wallet journal", exc_info=True)
            return []
        return [
            WalletJournalEntry(
                entry_id=item.get("id", 0),
                date=_parse_date(item.get("date")),
                ref_type=item.get("ref_type", ""),
                amount=item.get("amount", 0.0),
                balance=item.get("balance", 0.0),
                description=item.get("description", ""),
                first_party_id=item.get("first_party_id", 0),
                second_party_id=item.get("second_party_id", 0),
                reason=item.get("reason", ""),
                context_id=item.get("context_id"),
                context_id_type=item.get("context_id_type", ""),
            )
            for item in data
        ]

    # ──────────────────────────────────────────────────────────────────
    #  Mining Ledger
    # ──────────────────────────────────────────────────────────────────

    async def fetch_mining_ledger(self, character_id: int) -> list[MiningEntry]:
        """Fetch mining ledger (last 30 days)."""
        token = await self.token_manager.get_valid_token(character_id)
        if not token:
            return []
        try:
            data = await self.mining_api.get_character_mining(character_id, token)
        except Exception:
            logger.error("Failed to fetch mining ledger", exc_info=True)
            return []
        entries: list[MiningEntry] = []
        for item in data:
            type_id = item.get("type_id", 0)
            sys_id = item.get("solar_system_id", 0)
            entries.append(MiningEntry(
                date=item.get("date", ""),
                solar_system_id=sys_id,
                solar_system_name=self.sde.get_system_name(sys_id) if sys_id else "",
                type_id=type_id,
                type_name=self.sde.get_type_name(type_id),
                quantity=item.get("quantity", 0),
            ))
        return entries

    # ──────────────────────────────────────────────────────────────────
    #  Bookmarks
    # ──────────────────────────────────────────────────────────────────

    async def fetch_bookmarks(self, character_id: int) -> list[Bookmark]:
        """Fetch character bookmarks."""
        token = await self.token_manager.get_valid_token(character_id)
        if not token:
            return []
        try:
            data = await self.bookmarks_api.get_character_bookmarks(character_id, token)
        except Exception:
            logger.error("Failed to fetch bookmarks", exc_info=True)
            return []
        return [
            Bookmark(
                bookmark_id=item.get("bookmark_id", 0),
                folder_id=item.get("folder_id"),
                label=item.get("label", ""),
                notes=item.get("notes", ""),
                location_id=item.get("location_id", 0),
                creator_id=item.get("creator_id", 0),
                created=_parse_date(item.get("created")),
            )
            for item in data
        ]

    # ──────────────────────────────────────────────────────────────────
    #  Jump Fatigue
    # ──────────────────────────────────────────────────────────────────

    async def fetch_jump_fatigue(self, character_id: int) -> JumpFatigue | None:
        """Fetch jump fatigue info."""
        token = await self.token_manager.get_valid_token(character_id)
        if not token:
            return None
        try:
            data = await self.fatigue_api.get_jump_fatigue(character_id, token)
        except Exception:
            logger.error("Failed to fetch jump fatigue", exc_info=True)
            return None
        return JumpFatigue(
            jump_fatigue_expire_date=_parse_date(data.get("jump_fatigue_expire_date")),
            last_jump_date=_parse_date(data.get("last_jump_date")),
            last_update_date=_parse_date(data.get("last_update_date")),
        )

    # ──────────────────────────────────────────────────────────────────
    #  Killmail Details
    # ──────────────────────────────────────────────────────────────────

    async def fetch_killmail_detail(self, killmail_id: int, killmail_hash: str) -> Killmail | None:
        """Fetch full killmail details (victim, attackers, system)."""
        try:
            data = await self.killmails_api.get_killmail(killmail_id, killmail_hash)
        except Exception:
            logger.error("Failed to fetch killmail %d", killmail_id, exc_info=True)
            return None

        victim_data = data.get("victim", {})
        
        # Parse victim items (dropped/destroyed)
        victim_items: list[KillmailItem] = []
        for item_data in victim_data.get("items", []):
            victim_items.append(KillmailItem(
                type_id=item_data.get("item_type_id", 0),
                type_name=self.sde.get_type_name(item_data.get("item_type_id", 0)),
                flag=item_data.get("flag", 0),
                quantity_dropped=item_data.get("quantity_dropped", 0),
                quantity_destroyed=item_data.get("quantity_destroyed", 0),
                singleton=item_data.get("singleton", 0),
            ))

        victim = KillmailVictim(
            character_id=victim_data.get("character_id"),
            corporation_id=victim_data.get("corporation_id"),
            ship_type_id=victim_data.get("ship_type_id", 0),
            ship_type_name=self.sde.get_type_name(victim_data.get("ship_type_id", 0)),
            damage_taken=victim_data.get("damage_taken", 0),
            items=victim_items,
            position=victim_data.get("position", {}),
        )

        attackers: list[KillmailAttacker] = []
        for a in data.get("attackers", []):
            attackers.append(KillmailAttacker(
                character_id=a.get("character_id"),
                corporation_id=a.get("corporation_id"),
                alliance_id=a.get("alliance_id"),
                ship_type_id=a.get("ship_type_id"),
                ship_type_name=self.sde.get_type_name(a.get("ship_type_id", 0)) if a.get("ship_type_id") else "",
                weapon_type_id=a.get("weapon_type_id"),
                weapon_type_name=self.sde.get_type_name(a.get("weapon_type_id", 0)) if a.get("weapon_type_id") else "",
                damage_done=a.get("damage_done", 0),
                final_blow=a.get("final_blow", False),
                security_status=a.get("security_status", 0.0),
            ))

        sys_id = data.get("solar_system_id", 0)
        return Killmail(
            killmail_id=killmail_id,
            killmail_hash=killmail_hash,
            killmail_time=_parse_date(data.get("killmail_time")),
            solar_system_id=sys_id,
            solar_system_name=self.sde.get_system_name(sys_id) if sys_id else "",
            victim=victim,
            attackers=attackers,
        )

    # ──────────────────────────────────────────────────────────────────
    #  Mail Body
    # ──────────────────────────────────────────────────────────────────

    async def fetch_mail_body(self, character_id: int, mail_id: int) -> str:
        """Fetch the body text of a specific mail."""
        token = await self.token_manager.get_valid_token(character_id)
        if not token:
            return ""
        try:
            data = await self.mail_api.get_mail(character_id, token, mail_id)
            return data.get("body", "")
        except Exception:
            logger.error("Failed to fetch mail body %d", mail_id, exc_info=True)
            return ""

    # ──────────────────────────────────────────────────────────────────
    #  Wallet Transactions
    # ──────────────────────────────────────────────────────────────────

    async def fetch_wallet_transactions(self, character_id: int) -> list[WalletTransaction]:
        """Fetch wallet transactions."""
        token = await self.token_manager.get_valid_token(character_id)
        if not token:
            return []
        try:
            data = await self.wallet_api.get_transactions(character_id, token)
        except Exception:
            logger.error("Failed to fetch wallet transactions", exc_info=True)
            return []
        return [
            WalletTransaction(
                transaction_id=item.get("transaction_id", 0),
                date=_parse_date(item.get("date")),
                type_id=item.get("type_id", 0),
                type_name=self.sde.get_type_name(item.get("type_id", 0)),
                quantity=item.get("quantity", 0),
                unit_price=item.get("unit_price", 0.0),
                client_id=item.get("client_id", 0),
                location_id=item.get("location_id", 0),
                is_buy=item.get("is_buy", False),
                is_personal=item.get("is_personal", True),
                journal_ref_id=item.get("journal_ref_id", 0),
            )
            for item in data
        ]

    # ──────────────────────────────────────────────────────────────────
    #  Contract Items
    # ──────────────────────────────────────────────────────────────────

    async def fetch_contract_items(self, character_id: int, contract_id: int) -> list[dict]:
        """Fetch items inside a contract."""
        token = await self.token_manager.get_valid_token(character_id)
        if not token:
            return []
        try:
            data = await self.contracts_api.get_contract_items(character_id, token, contract_id)
            for item in data:
                item["type_name"] = self.sde.get_type_name(item.get("type_id", 0))
            return data
        except Exception:
            logger.error("Failed to fetch contract items %d", contract_id, exc_info=True)
            return []

    # ──────────────────────────────────────────────────────────────────
    #  Character Attributes
    # ──────────────────────────────────────────────────────────────────

    async def fetch_attributes(self, character_id: int) -> dict:
        """Fetch character attributes (INT, MEM, PER, WIL, CHA) + bonus remaps."""
        token = await self.token_manager.get_valid_token(character_id)
        if not token:
            return {}
        try:
            return await self.character_api.get_attributes(character_id, token)
        except Exception:
            logger.error("Failed to fetch attributes", exc_info=True)
            return {}

    # ──────────────────────────────────────────────────────────────────
    #  Employment History (public – no auth needed)
    # ──────────────────────────────────────────────────────────────────

    async def fetch_employment_history(self, character_id: int) -> list[dict]:
        """Fetch corporation history."""
        try:
            return await self.character_api.get_corporation_history(character_id)
        except Exception:
            logger.error("Failed to fetch employment history", exc_info=True)
            return []

    # ──────────────────────────────────────────────────────────────────
    #  Research Agents
    # ──────────────────────────────────────────────────────────────────

    async def fetch_research_agents(self, character_id: int) -> list[AgentResearch]:
        """Fetch research agent information."""
        token = await self.token_manager.get_valid_token(character_id)
        if not token:
            return []
        try:
            data = await self.research_api.get_agents_research(character_id, token)
        except Exception:
            logger.error("Failed to fetch research agents", exc_info=True)
            return []
        results: list[AgentResearch] = []
        for item in data:
            agent_id = item.get("agent_id", 0)
            skill_id = item.get("skill_type_id", 0)
            results.append(AgentResearch(
                agent_id=agent_id,
                skill_type_id=skill_id,
                skill_type_name=self.sde.get_type_name(skill_id),
                started_at=_parse_date(item.get("started_at")),
                points_per_day=item.get("points_per_day", 0.0),
                remainder_points=item.get("remainder_points", 0.0),
            ))
        return results

    # ──────────────────────────────────────────────────────────────────
    #  Faction Warfare Stats
    # ──────────────────────────────────────────────────────────────────

    async def fetch_fw_stats(self, character_id: int) -> dict:
        """Fetch faction warfare stats."""
        token = await self.token_manager.get_valid_token(character_id)
        if not token:
            return {}
        try:
            return await self.fw_api.get_character_fw_stats(character_id, token)
        except Exception:
            logger.error("Failed to fetch FW stats", exc_info=True)
            return {}

    # ──────────────────────────────────────────────────────────────────
    #  Medals
    # ──────────────────────────────────────────────────────────────────

    async def fetch_medals(self, character_id: int) -> list[Medal]:
        """Fetch character medals."""
        token = await self.token_manager.get_valid_token(character_id)
        if not token:
            return []
        try:
            data = await self.character_api.get_medals(character_id, token)
        except Exception:
            logger.error("Failed to fetch medals", exc_info=True)
            return []
        return [
            Medal(
                medal_id=item.get("medal_id", 0),
                title=item.get("title", ""),
                description=item.get("description", ""),
                corporation_id=item.get("corporation_id", 0),
                issuer_id=item.get("issuer_id", 0),
                date=_parse_date(item.get("date")),
                reason=item.get("reason", ""),
                status=item.get("status", ""),
            )
            for item in data
        ]

    # ──────────────────────────────────────────────────────────────────
    #  Titles
    # ──────────────────────────────────────────────────────────────────

    async def fetch_titles(self, character_id: int) -> list[dict]:
        """Fetch character corporation titles."""
        token = await self.token_manager.get_valid_token(character_id)
        if not token:
            return []
        try:
            return await self.character_api.get_titles(character_id, token)
        except Exception:
            logger.error("Failed to fetch titles", exc_info=True)
            return []

    # ──────────────────────────────────────────────────────────────────
    #  Mailing Lists
    # ──────────────────────────────────────────────────────────────────

    async def fetch_mailing_lists(self, character_id: int) -> list[dict]:
        """Fetch mailing list subscriptions."""
        token = await self.token_manager.get_valid_token(character_id)
        if not token:
            return []
        try:
            return await self.mail_api.get_mailing_lists(character_id, token)
        except Exception:
            logger.error("Failed to fetch mailing lists", exc_info=True)
            return []

    # ──────────────────────────────────────────────────────────────────
    #  Portrait URLs
    # ──────────────────────────────────────────────────────────────────

    async def fetch_portrait_url(self, character_id: int) -> str:
        """Get character portrait URL (128px)."""
        try:
            data = await self.character_api.get_portrait(character_id)
            return data.get("px128x128", "")
        except Exception:
            logger.error("Failed to fetch portrait", exc_info=True)
            return ""

    # ──────────────────────────────────────────────────────────────────
    #  Corporation & Alliance Info (public)
    # ──────────────────────────────────────────────────────────────────

    async def fetch_corporation_info(self, corporation_id: int) -> dict:
        """Fetch public corporation info."""
        try:
            return await self.character_api.get_corporation(corporation_id)
        except Exception:
            logger.error("Failed to fetch corporation info", exc_info=True)
            return {}

    async def fetch_alliance_info(self, alliance_id: int) -> dict:
        """Fetch public alliance info."""
        try:
            return await self.character_api.get_alliance(alliance_id)
        except Exception:
            logger.error("Failed to fetch alliance info", exc_info=True)
            return {}


def _parse_date(date_str: str | None) -> datetime | None:
    """Parse an ISO 8601 date string."""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None
