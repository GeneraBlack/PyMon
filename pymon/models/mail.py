"""Mail domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MailRecipient:
    """A mail recipient."""

    recipient_id: int = 0
    recipient_type: str = ""  # character, corporation, alliance, mailing_list


@dataclass
class MailHeader:
    """A mail header from the inbox."""

    mail_id: int
    subject: str = ""
    from_id: int = 0
    from_name: str = ""
    timestamp: datetime | None = None
    is_read: bool = False
    labels: list[int] = field(default_factory=list)
    recipients: list[MailRecipient] = field(default_factory=list)


@dataclass
class MailMessage:
    """A full mail message with body."""

    mail_id: int
    subject: str = ""
    from_id: int = 0
    from_name: str = ""
    body: str = ""
    timestamp: datetime | None = None
    is_read: bool = False
    labels: list[int] = field(default_factory=list)
    recipients: list[MailRecipient] = field(default_factory=list)


@dataclass
class MailLabel:
    """A mail label/folder."""

    label_id: int
    name: str = ""
    color: str = ""
    unread_count: int = 0


@dataclass
class MailingList:
    """A mailing list subscription."""

    mailing_list_id: int
    name: str = ""
