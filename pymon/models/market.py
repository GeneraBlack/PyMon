"""Market, Wallet and Financial domain models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class MarketOrder:
    """A character market order."""

    order_id: int
    type_id: int
    type_name: str = ""
    location_id: int = 0
    location_name: str = ""
    region_id: int = 0
    is_buy_order: bool = False
    price: float = 0.0
    volume_remain: int = 0
    volume_total: int = 0
    min_volume: int = 1
    duration: int = 0
    issued: datetime | None = None
    state: str = ""  # active (current orders only via ESI), or from history
    escrow: float = 0.0
    range: str = ""


@dataclass
class WalletTransaction:
    """A wallet transaction."""

    transaction_id: int
    date: datetime | None = None
    type_id: int = 0
    type_name: str = ""
    quantity: int = 0
    unit_price: float = 0.0
    client_id: int = 0
    client_name: str = ""
    location_id: int = 0
    is_buy: bool = False
    is_personal: bool = True
    journal_ref_id: int = 0


@dataclass
class WalletJournalEntry:
    """A wallet journal entry."""

    entry_id: int
    date: datetime | None = None
    ref_type: str = ""
    amount: float = 0.0
    balance: float = 0.0
    description: str = ""
    first_party_id: int = 0
    first_party_name: str = ""
    second_party_id: int = 0
    second_party_name: str = ""
    reason: str = ""
    context_id: int | None = None
    context_id_type: str = ""


@dataclass
class LoyaltyPoints:
    """LP balance for a corporation."""

    corporation_id: int
    corporation_name: str = ""
    loyalty_points: int = 0
