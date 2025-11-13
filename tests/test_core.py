"""Tests for core switching functionality."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from cc_api_switcher.config import SettingsProfile
from cc_api_switcher.core import CcApiSwitcher
from cc_api_switcher.exceptions import BackupError, CcApiSwitcherError
from cc_api_switcher.global_config import GlobalConfig


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

        switcher._cleanup_old_backups()

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


class TestCcApiSwitcherGlobalConfig:
    """Test CcApiSwitcher integration with GlobalConfig."""

    def test_init_with_global_config_default_target(self, tmp_path):
        """Test initialization with GlobalConfig for default target path."""
        config_file = tmp_path / "config.json"
        custom_target = tmp_path / "custom_settings.json"

        # Create a config with custom target
        config_data = {
            "default_target": str(custom_target),
            "backup_retention_count": 5,
            "auto_backup": False
        }
        config_file.write_text(json.dumps(config_data))

        # Mock GlobalConfig to use our test config
        with patch('cc_api_switcher.core.GlobalConfig') as mock_global_config:
            mock_config = mock_global_config.return_value
            mock_config.get_default_target_path.return_value = custom_target
            mock_config.get_backup_retention_count.return_value = 5
            mock_config.is_auto_backup_enabled.return_value = False

            switcher = CcApiSwitcher(global_config=mock_config)

            assert switcher.target_path == custom_target
            assert switcher.global_config == mock_config

    def test_init_without_global_config_uses_default(self, tmp_path):
        """Test initialization without GlobalConfig uses system default."""
        target = tmp_path / "settings.json"

        with patch('cc_api_switcher.core.get_default_target_path') as mock_default:
            mock_default.return_value = target

            switcher = CcApiSwitcher()

            assert switcher.target_path == target
            assert switcher.global_config is None

    def test_get_backup_retention_count_with_global_config(self, tmp_path):
        """Test backup retention count from GlobalConfig."""
        with patch('cc_api_switcher.core.GlobalConfig') as mock_global_config:
            mock_config = mock_global_config.return_value
            mock_config.get_backup_retention_count.return_value = 7

            switcher = CcApiSwitcher(global_config=mock_config)
            retention = switcher._get_backup_retention_count()

            assert retention == 7
            # Called once during validation and once in the test
            assert mock_config.get_backup_retention_count.call_count == 2

    def test_get_backup_retention_count_without_global_config(self, tmp_path):
        """Test backup retention count fallback without GlobalConfig."""
        switcher = CcApiSwitcher()
        retention = switcher._get_backup_retention_count()

        assert retention == 10  # Default fallback

    def test_get_backup_retention_count_invalid_value(self, tmp_path):
        """Test backup retention count with invalid value falls back to default."""
        with patch('cc_api_switcher.core.GlobalConfig') as mock_global_config:
            mock_config = mock_global_config.return_value
            mock_config.get_backup_retention_count.return_value = -5  # Invalid

            switcher = CcApiSwitcher(global_config=mock_config)
            retention = switcher._get_backup_retention_count()

            assert retention == 10  # Fallback for invalid value

    def test_is_auto_backup_enabled_with_global_config(self, tmp_path):
        """Test auto-backup toggle from GlobalConfig."""
        with patch('cc_api_switcher.core.GlobalConfig') as mock_global_config:
            mock_config = mock_global_config.return_value
            mock_config.is_auto_backup_enabled.return_value = False

            switcher = CcApiSwitcher(global_config=mock_config)
            auto_backup = switcher._is_auto_backup_enabled()

            assert auto_backup is False
            mock_config.is_auto_backup_enabled.assert_called_once()

    def test_is_auto_backup_enabled_without_global_config(self, tmp_path):
        """Test auto-backup toggle fallback without GlobalConfig."""
        switcher = CcApiSwitcher()
        auto_backup = switcher._is_auto_backup_enabled()

        assert auto_backup is True  # Default fallback

    def test_cleanup_old_backups_uses_configured_retention(self, tmp_path):
        """Test cleanup uses configured retention count."""
        target = tmp_path / "settings.json"
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()

        # Create more than 5 backups
        for i in range(8):
            backup_file = backup_dir / f"settings.json.backup.2023120{i}_{i:02d}00"
            backup_file.write_text(f"backup content {i}")

        with patch('cc_api_switcher.core.GlobalConfig') as mock_global_config:
            mock_config = mock_global_config.return_value
            mock_config.get_backup_retention_count.return_value = 5

            switcher = CcApiSwitcher(target_path=target, backup_dir=backup_dir, global_config=mock_config)
            switcher._cleanup_old_backups()

            # Should keep only 5 most recent backups
            remaining_backups = list(backup_dir.glob("*.backup.*"))
            assert len(remaining_backups) == 5

    def test_switch_to_respects_auto_backup_setting(self, tmp_path):
        """Test switch_to respects auto-backup setting from GlobalConfig."""
        target = tmp_path / "settings.json"
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()

        # Create existing target file
        target.write_text('{"existing": "settings"}')

        profile_data = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
                "ANTHROPIC_AUTH_TOKEN": "sk-test123",
            }
        }
        profile = SettingsProfile.from_dict(profile_data, name="test")

        with patch('cc_api_switcher.core.GlobalConfig') as mock_global_config:
            mock_config = mock_global_config.return_value
            mock_config.is_auto_backup_enabled.return_value = False  # Auto-backup disabled

            switcher = CcApiSwitcher(target_path=target, backup_dir=backup_dir, global_config=mock_config)
            switcher.switch_to(profile, create_backup=True)

            # No backup should be created when auto-backup is disabled
            backups = list(backup_dir.glob("*.backup.*"))
            assert len(backups) == 0

    def test_backup_settings_validation_warnings(self, tmp_path, capsys):
        """Test backup settings validation produces warnings for invalid settings."""
        with patch('cc_api_switcher.core.GlobalConfig') as mock_global_config:
            mock_config = mock_global_config.return_value
            mock_config.get_backup_retention_count.return_value = -3  # Invalid
            mock_config.get_default_target_path.return_value = tmp_path / "nonexistent" / "settings.json"

            switcher = CcApiSwitcher(global_config=mock_config)

            # Capture stderr to check for warnings
            captured = capsys.readouterr()
            assert "Invalid backup_retention_count" in captured.err
            assert "Target parent directory does not exist" in captured.err
