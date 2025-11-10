"""Tests for CLI base classes."""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import typer
from rich.console import Console

from cc_api_switcher.cli.base import BaseCommand, CommandContext, with_error_handling
from cc_api_switcher.config import ProfileStore
from cc_api_switcher.global_config import GlobalConfig, GlobalConfigError
from cc_api_switcher.exceptions import ProfileNotFoundError, InvalidProfileError


class TestBaseCommand:
    """Test the BaseCommand class."""

    def test_init_with_directory(self, tmp_path):
        """Test BaseCommand initialization with explicit directory."""
        command = BaseCommand(directory=tmp_path)

        assert command.directory == tmp_path
        assert command.store is not None
        assert command.global_config is None
        assert command.console is not None

    def test_init_without_directory(self, monkeypatch):
        """Test BaseCommand initialization without directory (global mode)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            monkeypatch.setenv("XDG_CONFIG_HOME", temp_dir)

            command = BaseCommand()

            assert command.directory is None
            assert command.store is not None
            assert command.global_config is not None
            assert command.console is not None

    def test_handle_error_profile_not_found(self):
        """Test error handling for ProfileNotFoundError."""
        command = BaseCommand()
        error = ProfileNotFoundError("Test profile not found")

        with pytest.raises(SystemExit):
            command.handle_error(error)

    def test_handle_error_invalid_profile(self):
        """Test error handling for InvalidProfileError."""
        command = BaseCommand()
        error = InvalidProfileError("Invalid profile format")

        with pytest.raises(SystemExit):
            command.handle_error(error)

    def test_get_target_path_explicit(self):
        """Test getting target path with explicit override."""
        command = BaseCommand()
        explicit_target = Path("/custom/target.json")

        result = command.get_target_path(target=explicit_target)

        assert result == explicit_target

    def test_get_target_path_default(self):
        """Test getting target path with default logic."""
        command = BaseCommand()
        # Since global_config might be None, test the fallback
        result = command.get_target_path()

        expected = Path.home() / ".claude" / "settings.json"
        assert result == expected

    def test_ensure_profile_exists_success(self, tmp_path):
        """Test profile existence check when profile exists."""
        # Create a test profile
        profile_data = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://api.test.com",
                "ANTHROPIC_AUTH_TOKEN": "sk-test123",
            }
        }
        profile_file = tmp_path / "test_profile_settings.json"
        import json
        profile_file.write_text(json.dumps(profile_data))

        command = BaseCommand(directory=tmp_path)
        # Should not raise any exception
        command.ensure_profile_exists("test_profile")

    def test_ensure_profile_exists_not_found(self, tmp_path):
        """Test profile existence check when profile doesn't exist."""
        command = BaseCommand(directory=tmp_path)

        with pytest.raises(SystemExit):
            command.ensure_profile_exists("nonexistent_profile")

    def test_output_methods(self):
        """Test console output methods."""
        command = BaseCommand()

        # These should not raise exceptions
        command.success("Test success")
        command.error("Test error")
        command.info("Test info")
        command.warning("Test warning")


class TestCommandContext:
    """Test the CommandContext class."""

    def test_init_with_all_parameters(self, tmp_path):
        """Test CommandContext initialization with all parameters."""
        global_config = MagicMock()
        store = MagicMock()
        console = Console()

        context = CommandContext(
            directory=tmp_path,
            global_config=global_config,
            store=store,
            console=console
        )

        assert context.directory == tmp_path
        assert context.global_config == global_config
        assert context.store == store
        assert context.console == console

    def test_get_or_resolve_store_and_config_cached(self, tmp_path):
        """Test context returns cached store and config."""
        store = MagicMock()
        global_config = MagicMock()

        context = CommandContext(
            directory=tmp_path,
            global_config=global_config,
            store=store
        )

        result_store, result_config = context.get_or_resolve_store_and_config()

        assert result_store == store
        assert result_config == global_config

    def test_get_or_resolve_store_and_config_resolve(self, monkeypatch):
        """Test context resolves store and config when not cached."""
        with tempfile.TemporaryDirectory() as temp_dir:
            monkeypatch.setenv("XDG_CONFIG_HOME", temp_dir)

            context = CommandContext()

            store, global_config = context.get_or_resolve_store_and_config()

            assert store is not None
            assert global_config is not None


class TestErrorHandlingDecorator:
    """Test the error handling decorator."""

    def test_with_error_handling_success(self):
        """Test decorator with successful function."""
        @with_error_handling
        def test_function():
            return "success"

        result = test_function()
        assert result == "success"

    def test_with_error_handling_cc_api_error(self):
        """Test decorator with CcApiSwitcherError."""
        @with_error_handling
        def test_function():
            raise ProfileNotFoundError("Test error")

        with pytest.raises((SystemExit, typer.Exit)):
            test_function()

    def test_with_error_handling_unexpected_error(self):
        """Test decorator with unexpected error."""
        @with_error_handling
        def test_function():
            raise ValueError("Unexpected error")

        # Should still raise SystemExit due to the decorator
        with pytest.raises((SystemExit, typer.Exit)):
            test_function()