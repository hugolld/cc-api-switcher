"""Tests for core switching functionality."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from cc_api_switcher.config import SettingsProfile
from cc_api_switcher.core import CcApiSwitcher
from cc_api_switcher.exceptions import BackupError, CcApiSwitcherError


class TestCcApiSwitcher:
    """Test CcApiSwitcher class."""

    def test_init(self):
        """Test initialization."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            target = Path(tmp_dir) / "settings.json"
            backup_dir = Path(tmp_dir) / "backups"

            switcher = CcApiSwitcher(target_path=target, backup_dir=backup_dir)

            assert switcher.target_path == target
            assert switcher.backup_dir == backup_dir
            assert backup_dir.exists()

    def test_create_backup(self, tmp_path):
        """Test creating backup."""
        target = tmp_path / "settings.json"
        backup_dir = tmp_path / "backups"

        # Create target file with content
        target.write_text("test content")

        switcher = CcApiSwitcher(target_path=target, backup_dir=backup_dir)
        backup_path = switcher._create_backup()

        assert backup_path is not None
        assert backup_path.exists()
        assert backup_path.read_text() == "test content"

    def test_create_backup_no_target(self, tmp_path):
        """Test creating backup when target doesn't exist."""
        target = tmp_path / "settings.json"
        backup_dir = tmp_path / "backups"

        switcher = CcApiSwitcher(target_path=target, backup_dir=backup_dir)
        backup_path = switcher._create_backup()

        assert backup_path is None

    def test_cleanup_old_backups(self, tmp_path):
        """Test cleanup of old backups."""
        target = tmp_path / "settings.json"
        backup_dir = tmp_path / "backups"

        switcher = CcApiSwitcher(target_path=target, backup_dir=backup_dir)

        # Create 15 backups
        for i in range(15):
            backup_file = backup_dir / f"settings.json.backup.{i}"
            backup_file.write_text(f"backup{i}")

        switcher._cleanup_old_backups(keep=10)

        # Should keep only 10
        remaining = list(backup_dir.glob("*"))
        assert len(remaining) == 10

    def test_switch_to_valid_profile(self, tmp_path):
        """Test switching to a valid profile."""
        target = tmp_path / "settings.json"
        backup_dir = tmp_path / "backups"

        profile_data = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://api.example.com",
                "ANTHROPIC_AUTH_TOKEN": "test-token",
            }
        }
        profile = SettingsProfile.from_dict(profile_data, name="test")

        switcher = CcApiSwitcher(target_path=target, backup_dir=backup_dir)

        with patch("os.chmod"):  # Don't actually change permissions in test
            switcher.switch_to(profile, create_backup=False)

        assert target.exists()

        with open(target) as f:
            saved_data = json.load(f)

        assert saved_data["env"]["ANTHROPIC_AUTH_TOKEN"] == "test-token"

    def test_switch_to_invalid_profile(self, tmp_path):
        """Test switching to an invalid profile."""
        target = tmp_path / "settings.json"
        backup_dir = tmp_path / "backups"

        # Profile missing required fields
        profile_data = {"env": {}}
        profile = SettingsProfile.from_dict(profile_data, name="invalid")

        switcher = CcApiSwitcher(target_path=target, backup_dir=backup_dir)

        with pytest.raises(CcApiSwitcherError) as exc_info:
            switcher.switch_to(profile, create_backup=False)

        assert "validation failed" in str(exc_info.value).lower()

    def test_list_backups(self, tmp_path):
        """Test listing backups."""
        target = tmp_path / "settings.json"
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Create some backups
        for i in range(3):
            backup_file = backup_dir / f"settings.json.backup.{i}"
            backup_file.write_text(f"backup{i}")

        switcher = CcApiSwitcher(target_path=target, backup_dir=backup_dir)
        backups = switcher.list_backups()

        assert len(backups) == 3

    def test_restore_backup(self, tmp_path):
        """Test restoring from backup."""
        target = tmp_path / "settings.json"
        backup_dir = tmp_path / "backups"

        # Create backup
        backup_path = backup_dir / "settings.json.backup.123"
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        backup_path.write_text("backup content")

        switcher = CcApiSwitcher(target_path=target, backup_dir=backup_dir)

        with patch("os.chmod"):  # Don't actually change permissions in test
            switcher.restore_backup(backup_path)

        assert target.read_text() == "backup content"

    def test_restore_backup_not_found(self, tmp_path):
        """Test restoring from non-existent backup."""
        target = tmp_path / "settings.json"
        backup_dir = tmp_path / "backups"

        backup_path = backup_dir / "nonexistent"

        switcher = CcApiSwitcher(target_path=target, backup_dir=backup_dir)

        with pytest.raises(BackupError) as exc_info:
            switcher.restore_backup(backup_path)

        assert "not found" in str(exc_info.value).lower()

    def test_get_current_profile(self, tmp_path):
        """Test getting current profile from settings file."""
        target = tmp_path / "settings.json"

        profile_data = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
                "ANTHROPIC_AUTH_TOKEN": "test-token",
            }
        }
        with open(target, "w") as f:
            json.dump(profile_data, f)

        switcher = CcApiSwitcher(target_path=target)
        profile = switcher.get_current_profile()

        assert profile is not None
        assert profile.env["ANTHROPIC_AUTH_TOKEN"] == "test-token"

    def test_get_current_profile_no_file(self, tmp_path):
        """Test getting current profile when file doesn't exist."""
        target = tmp_path / "settings.json"

        switcher = CcApiSwitcher(target_path=target)
        profile = switcher.get_current_profile()

        assert profile is None

    def test_show_profile_info(self, tmp_path):
        """Test formatting profile info."""
        profile_data = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
                "ANTHROPIC_AUTH_TOKEN": "12345678901234567890",
                "ANTHROPIC_MODEL": "deepseek-chat",
                "API_TIMEOUT_MS": "600000",
            }
        }
        profile = SettingsProfile.from_dict(profile_data, name="deepseek")

        switcher = CcApiSwitcher()
        info = switcher.show_profile_info(profile)

        assert "deepseek" in info.lower()
        assert "1234************7890" in info  # Masked token preserving original length
        assert "deepseek-chat" in info
        assert "600s" in info or "600.0s" in info  # Handle both formats
