"""Contract domain models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Contract:
    """An EVE contract."""

    contract_id: int
    issuer_id: int = 0
    issuer_name: str = ""
    issuer_corporation_id: int = 0
    assignee_id: int = 0
    assignee_name: str = ""
    acceptor_id: int = 0
    acceptor_name: str = ""
    contract_type: str = ""  # unknown, item_exchange, auction, courier, loan
    status: str = ""  # outstanding, in_progress, finished, etc.
    title: str = ""
    start_location_id: int | None = None
    end_location_id: int | None = None
    price: float = 0.0
    reward: float = 0.0
    collateral: float = 0.0
    buyout: float = 0.0
    volume: float = 0.0
    days_to_complete: int = 0
    date_issued: datetime | None = None
    date_expired: datetime | None = None
    date_accepted: datetime | None = None
    date_completed: datetime | None = None
    for_corporation: bool = False
    availability: str = ""  # public, personal, corporation, alliance


@dataclass
class ContractItem:
    """An item within a contract."""

    record_id: int
    type_id: int
    type_name: str = ""
    quantity: int = 0
    is_included: bool = True
    is_singleton: bool = False
    raw_quantity: int | None = None
