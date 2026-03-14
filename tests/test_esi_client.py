"""Tests for the ESI client."""

from __future__ import annotations

from pymon.api.esi_client import ESIClient


def test_esi_client_creation():
    """ESIClient can be instantiated."""
    client = ESIClient()
    assert client._cache == {}
    assert callable(client._make_client)


def test_esi_client_user_agent():
    """ESIClient has a proper user agent."""
    assert "PyMon" in ESIClient.USER_AGENT
