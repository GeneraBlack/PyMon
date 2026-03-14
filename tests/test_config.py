"""Tests for the configuration module."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from pymon.core.config import Config, DEFAULT_SCOPES


def test_config_defaults():
    """Config has sensible defaults."""
    config = Config()
    assert config.client_id == ""
    assert config.language == "en"
    assert config.debug is False
    assert len(config.scopes) > 0
    assert "esi-skills.read_skills.v1" in config.scopes


def test_config_save_load(tmp_path):
    """Config can be saved and loaded."""
    config = Config(data_dir=tmp_path)
    config.client_id = "test-client-id"
    config.language = "de"
    config.save()

    # Verify file was written
    assert config.config_file.exists()
    data = json.loads(config.config_file.read_text())
    assert data["client_id"] == "test-client-id"
    assert data["language"] == "de"

    # Load into new config
    config2 = Config(data_dir=tmp_path)
    assert config2.client_id == "test-client-id"
    assert config2.language == "de"
