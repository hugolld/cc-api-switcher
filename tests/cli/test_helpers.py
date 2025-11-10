"""Tests for CLI helper functions."""

import errno
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import typer
from rich.console import Console

from cc_api_switcher.cli.helpers import (
    resolve_store_and_config,
    resolve_target_path,
    handle_cli_error,
    get_editor_command,
    format_profile_for_display,
    create_profile_table,
    format_file_size,
    ensure_directory_exists,
    validate_profile_name,
    get_user_confirmation,
)
from cc_api_switcher.config import ProfileStore, SettingsProfile
from cc_api_switcher.global_config import GlobalConfig
from cc_api_switcher.exceptions import (
    ProfileNotFoundError,
    InvalidProfileError,
    BackupError,
    ValidationError,
)
from cc_api_switcher.global_config import GlobalConfigError


class TestResolveStoreAndConfig:
    """Test the resolve_store_and_config function."""

    def test_with_explicit_directory(self, tmp_path):
        """Test resolution with explicit directory."""
        store, global_config = resolve_store_and_config(directory=tmp_path)

        assert isinstance(store, ProfileStore)
        assert global_config is None

    def test_without_directory_global_mode(self, monkeypatch):
        """Test resolution without directory (global mode)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            monkeypatch.setenv("XDG_CONFIG_HOME", temp_dir)

            store, global_config = resolve_store_and_config()

            assert isinstance(store, ProfileStore)
            assert isinstance(global_config, GlobalConfig)

    def test_global_config_error(self, monkeypatch):
        """Test handling of GlobalConfig errors."""
        # Point to non-existent config directory
        monkeypatch.setenv("XDG_CONFIG_HOME", "/nonexistent/path")

        with pytest.raises(GlobalConfigError):
            resolve_store_and_config()


class TestResolveTargetPath:
    """Test the resolve_target_path function."""

    def test_with_explicit_target(self):
        """Test path resolution with explicit target."""
        explicit_target = Path("/custom/settings.json")
        result = resolve_target_path(target=explicit_target)

        assert result == explicit_target

    def test_with_global_config(self):
        """Test path resolution with global config."""
        mock_global_config = MagicMock()
        mock_global_config.get_default_target_path.return_value = Path("/global/settings.json")

        result = resolve_target_path(global_config=mock_global_config)

        assert result == Path("/global/settings.json")

    def test_fallback_default(self):
        """Test path resolution fallback to default."""
        result = resolve_target_path()

        expected = Path.home() / ".claude" / "settings.json"
        assert result == expected


class TestHandleCliError:
    """Test the handle_cli_error function."""

    def test_profile_not_found_error(self):
        """Test handling of ProfileNotFoundError."""
        console = Console()
        error = ProfileNotFoundError("Test profile not found")

        with pytest.raises((SystemExit, typer.Exit)):
            handle_cli_error(error, console)

    def test_invalid_profile_error(self):
        """Test handling of InvalidProfileError."""
        console = Console()
        error = InvalidProfileError("Invalid profile")

        with pytest.raises((SystemExit, typer.Exit)):
            handle_cli_error(error, console)

    def test_backup_error(self):
        """Test handling of BackupError."""
        console = Console()
        error = BackupError("Backup failed")

        with pytest.raises((SystemExit, typer.Exit)):
            handle_cli_error(error, console)

    def test_validation_error(self):
        """Test handling of ValidationError."""
        console = Console()
        error = ValidationError("Validation failed")

        with pytest.raises((SystemExit, typer.Exit)):
            handle_cli_error(error, console)

    def test_global_config_error(self):
        """Test handling of GlobalConfigError."""
        console = Console()
        error = GlobalConfigError("Config error")

        with pytest.raises((SystemExit, typer.Exit)):
            handle_cli_error(error, console)

    def test_permission_error(self):
        """Test handling of PermissionError."""
        console = Console()
        error = PermissionError(errno.EACCES, "Permission denied")

        with pytest.raises((SystemExit, typer.Exit)):
            handle_cli_error(error, console)

    def test_unexpected_error(self):
        """Test handling of unexpected errors."""
        console = Console()
        error = ValueError("Unexpected error")

        with pytest.raises((SystemExit, typer.Exit)):
            handle_cli_error(error, console)


class TestGetEditorCommand:
    """Test the get_editor_command function."""

    def test_with_editor_env_var(self, monkeypatch):
        """Test getting editor from environment variable."""
        monkeypatch.setenv("EDITOR", "custom-editor")
        with patch('shutil.which', return_value="/usr/bin/custom-editor"):
            result = get_editor_command()
            assert result == "custom-editor"

    def test_fallback_to_code(self):
        """Test fallback to VS Code."""
        with patch('shutil.which') as mock_which:
            def which_side_effect(editor):
                if editor == 'code':
                    return '/usr/bin/code'
                return None

            mock_which.side_effect = which_side_effect
            result = get_editor_command()
            assert result == 'code'

    def test_fallback_to_nano(self):
        """Test fallback to nano."""
        with patch('shutil.which') as mock_which:
            def which_side_effect(editor):
                if editor == 'nano':
                    return '/usr/bin/nano'
                return None

            mock_which.side_effect = which_side_effect
            result = get_editor_command()
            assert result == 'nano'


class TestFormatProfileForDisplay:
    """Test the format_profile_for_display function."""

    def test_with_secrets_masked(self):
        """Test profile formatting with masked secrets."""
        profile_data = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://api.test.com",
                "ANTHROPIC_AUTH_TOKEN": "sk-1234567890abcdef1234567890abcdef12345678",
            }
        }
        profile = SettingsProfile.from_dict(profile_data, name="test")

        result = format_profile_for_display(profile, show_secrets=False)

        assert result["env"]["ANTHROPIC_AUTH_TOKEN"] != "sk-1234567890abcdef1234567890abcdef12345678"
        assert "sk-1234" in result["env"]["ANTHROPIC_AUTH_TOKEN"]  # Should show partial

    def test_with_secrets_shown(self):
        """Test profile formatting with secrets shown."""
        full_token = "sk-1234567890abcdef1234567890abcdef12345678"
        profile_data = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://api.test.com",
                "ANTHROPIC_AUTH_TOKEN": full_token,
            }
        }
        profile = SettingsProfile.from_dict(profile_data, name="test")

        result = format_profile_for_display(profile, show_secrets=True)

        assert result["env"]["ANTHROPIC_AUTH_TOKEN"] == full_token

    def test_with_source(self):
        """Test profile formatting with source information."""
        profile_data = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://api.test.com",
                "ANTHROPIC_AUTH_TOKEN": "sk-test123",
            }
        }
        profile = SettingsProfile.from_dict(profile_data, name="test")

        result = format_profile_for_display(profile, source="test_source")

        assert result["_source"] == "test_source"


class TestUtilityFunctions:
    """Test utility helper functions."""

    def test_create_profile_table(self):
        """Test profile table creation."""
        console = Console()
        table = create_profile_table(console)

        assert table is not None
        assert table.title == "Available Profiles"

    def test_format_file_size(self):
        """Test file size formatting."""
        assert format_file_size(0) == "0B"
        assert format_file_size(1024) == "1.0KB"
        assert format_file_size(1024 * 1024) == "1.0MB"

    def test_ensure_directory_exists_new(self, tmp_path):
        """Test creating new directory."""
        new_dir = tmp_path / "new_directory"
        ensure_directory_exists(new_dir)
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_ensure_directory_exists_existing(self, tmp_path):
        """Test existing directory."""
        existing_dir = tmp_path / "existing_directory"
        existing_dir.mkdir()

        # Should not raise an exception
        ensure_directory_exists(existing_dir)
        assert existing_dir.exists()

    def test_ensure_directory_exists_permission_error(self):
        """Test permission error when creating directory."""
        # Mock PermissionError instead of trying to create in /root
        from unittest.mock import patch

        invalid_path = Path("/root/invalid_path")

        with patch('pathlib.Path.mkdir') as mock_mkdir:
            import errno
            mock_mkdir.side_effect = PermissionError(errno.EACCES, "Permission denied")

            with pytest.raises(PermissionError):
                ensure_directory_exists(invalid_path)

    def test_validate_profile_name_valid(self):
        """Test validation of valid profile names."""
        assert validate_profile_name("test_profile") == "test_profile"
        assert validate_profile_name("  spaced_name  ") == "spaced_name"
        assert validate_profile_name("profile-123") == "profile-123"

    def test_validate_profile_name_invalid(self):
        """Test validation of invalid profile names."""
        with pytest.raises(ValidationError):
            validate_profile_name("")

        with pytest.raises(ValidationError):
            validate_profile_name("   ")

        with pytest.raises(ValidationError):
            validate_profile_name("profile/name")

        with pytest.raises(ValidationError):
            validate_profile_name("profile\\name")

        with pytest.raises(ValidationError):
            validate_profile_name("a" * 51)  # Too long

    def test_get_user_confirmation_with_input(self):
        """Test getting user confirmation with mocked input."""
        console = Console()

        with patch('rich.prompt.Confirm.ask', return_value=True):
            result = get_user_confirmation("Test question", console=console)
            assert result is True

        with patch('rich.prompt.Confirm.ask', return_value=False):
            result = get_user_confirmation("Test question", console=console)
            assert result is False