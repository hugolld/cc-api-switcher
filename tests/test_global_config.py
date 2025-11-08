"""Tests for global configuration functionality."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from cc_api_switcher.global_config import GlobalConfig, GlobalConfigError
from cc_api_switcher.config import ProfileStore


class TestGlobalConfig:
    """Test cases for GlobalConfig class."""

    def test_init_without_config_file(self, tmp_path):
        """Test GlobalConfig initialization without existing config file."""
        # Create a temporary directory for config
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        # When we provide a config_file, we should check if it works correctly
        global_config = GlobalConfig(config_file=config_dir / "config.json")

        assert global_config.config_file == config_dir / "config.json"
        # config_dir is derived from config_file parent or home directory logic
        # Create the profiles directory since it's needed for the test
        global_config.ensure_global_profiles_dir()
        assert global_config.global_profiles_dir.exists()
        assert global_config._config == {}

    def test_init_with_existing_config_file(self, tmp_path):
        """Test GlobalConfig initialization with existing config file."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        config_file = config_dir / "config.json"

        # Create test config
        test_config = {
            "default_profile_dir": "/test/profiles",
            "backup_retention_count": 5,
            "auto_backup": False
        }
        with open(config_file, "w") as f:
            json.dump(test_config, f)

        global_config = GlobalConfig(config_file=config_file)

        assert global_config._config == test_config
        assert global_config.get_config_value("backup_retention_count") == 5
        assert global_config.is_auto_backup_enabled() is False

    def test_get_config_dir_with_xdg_config_home(self):
        """Test config directory resolution with XDG_CONFIG_HOME."""
        with patch.dict(os.environ, {"XDG_CONFIG_HOME": "/custom/config"}):
            global_config = GlobalConfig()
            assert str(global_config.config_dir).endswith("/custom/config/cc-api-switcher")

    def test_get_config_dir_default(self):
        """Test config directory resolution with default path."""
        with patch.dict(os.environ, {}, clear=False):
            if "XDG_CONFIG_HOME" in os.environ:
                del os.environ["XDG_CONFIG_HOME"]
            global_config = GlobalConfig()
            assert str(global_config.config_dir).endswith("/.config/cc-api-switcher")

    def test_get_profile_directories(self, tmp_path):
        """Test profile directory search order."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        config_file = config_dir / "config.json"

        # Create test config with custom profile dir
        test_config = {
            "default_profile_dir": str(tmp_path / "custom_profiles")
        }
        with open(config_file, "w") as f:
            json.dump(test_config, f)

        global_config = GlobalConfig(config_file=config_file)

        directories = global_config.get_profile_directories()
        assert len(directories) >= 2  # Should have at least global and local
        assert str(tmp_path / "custom_profiles") in [str(d) for d in directories]
        assert str(Path.cwd()) in [str(d) for d in directories]

    def test_get_profile_directories_with_env_override(self, tmp_path):
        """Test profile directory search order with environment variable."""
        env_profile_dir = tmp_path / "env_profiles"
        with patch.dict(os.environ, {"CC_API_SWITCHER_PROFILE_DIR": str(env_profile_dir)}):
            global_config = GlobalConfig()
            directories = global_config.get_profile_directories()
            assert env_profile_dir in directories
            assert directories[0] == env_profile_dir  # Should be first priority

    def test_find_profile_file(self, tmp_path):
        """Test finding profile files in search directories."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        config_file = config_dir / "config.json"

        # Create test config
        test_config = {"default_profile_dir": str(tmp_path / "profiles")}
        with open(config_file, "w") as f:
            json.dump(test_config, f)

        global_config = GlobalConfig(config_file=config_file)

        # Create a profile file
        profiles_dir = tmp_path / "profiles"
        profiles_dir.mkdir()
        profile_file = profiles_dir / "test_settings.json"
        profile_file.write_text('{"env": {"ANTHROPIC_BASE_URL": "https://test.com"}}')

        found_path = global_config.find_profile_file("test")
        assert found_path == profile_file

        # Test non-existent profile
        assert global_config.find_profile_file("nonexistent") is None

    def test_list_available_profiles(self, tmp_path):
        """Test listing available profiles from all search directories."""
        import os

        # Change to a temporary directory to avoid contamination from project files
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            config_dir = tmp_path / "config"
            config_dir.mkdir()
            config_file = config_dir / "config.json"

            # Create test config with custom profile directory to avoid conflicts
            test_config = {"default_profile_dir": str(tmp_path / "profiles")}
            with open(config_file, "w") as f:
                json.dump(test_config, f)

            global_config = GlobalConfig(config_file=config_file)

            # Create profile files in global directory
            profiles_dir = tmp_path / "profiles"
            profiles_dir.mkdir()
            (profiles_dir / "global1_settings.json").write_text('{"env": {"ANTHROPIC_BASE_URL": "https://global1.com"}}')
            (profiles_dir / "global2_settings.json").write_text('{"env": {"ANTHROPIC_BASE_URL": "https://global2.com"}}')

            # Create a local profile in current directory
            local_profile = tmp_path / "local_settings.json"
            local_profile.write_text('{"env": {"ANTHROPIC_BASE_URL": "https://local.com"}}')

            profiles = global_config.list_available_profiles()
            profile_names = [p["name"] for p in profiles]

            assert "global1" in profile_names
            assert "global2" in profile_names
            assert "local" in profile_names

            # Check source information
            global_profiles = [p for p in profiles if p["source"] == "global"]
            local_profiles = [p for p in profiles if p["source"] == "local"]

            assert len(global_profiles) == 2
            assert len(local_profiles) == 1
        finally:
            os.chdir(original_cwd)

    def test_ensure_global_profiles_dir(self, tmp_path):
        """Test ensuring global profiles directory exists."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        config_file = config_dir / "config.json"

        global_config = GlobalConfig(config_file=config_file)

        profiles_dir = global_config.ensure_global_profiles_dir()
        assert profiles_dir.exists()
        assert profiles_dir.is_dir()

    def test_config_value_operations(self, tmp_path):
        """Test configuration value get/set operations."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        config_file = config_dir / "config.json"

        global_config = GlobalConfig(config_file=config_file)

        # Test default values
        assert global_config.get_config_value("nonexistent", "default") == "default"
        assert global_config.get_config_value("nonexistent") is None

        # Test setting values
        global_config.set_config_value("test_key", "test_value")
        assert global_config.get_config_value("test_key") == "test_value"

        # Test saving
        global_config.save_config()
        assert config_file.exists()

        # Load config from file
        new_config = GlobalConfig(config_file=config_file)
        assert new_config.get_config_value("test_key") == "test_value"

    def test_initialize_config(self, tmp_path):
        """Test configuration initialization."""
        config_dir = tmp_path / "config"
        config_file = config_dir / "config.json"

        global_config = GlobalConfig(config_file=config_file)
        global_config.initialize_config()

        assert config_file.exists()
        profiles_dir = global_config.global_profiles_dir
        assert profiles_dir.exists()

        # Check default configuration values
        with open(config_file, "r") as f:
            config_data = json.load(f)

        assert "default_profile_dir" in config_data
        assert "backup_retention_count" in config_data
        assert "auto_backup" in config_data
        assert config_data["backup_retention_count"] == 10
        assert config_data["auto_backup"] is True

    def test_invalid_config_file(self, tmp_path):
        """Test handling of invalid configuration file."""
        config_file = tmp_path / "invalid.json"
        config_file.write_text("invalid json content")

        with pytest.raises(GlobalConfigError):
            GlobalConfig(config_file=config_file)


class TestProfileStoreWithGlobalConfig:
    """Test ProfileStore integration with global configuration."""

    def test_profile_store_with_global_config(self, tmp_path):
        """Test ProfileStore using global configuration."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        config_file = config_dir / "config.json"

        # Create test config
        test_config = {"default_profile_dir": str(tmp_path / "profiles")}
        with open(config_file, "w") as f:
            json.dump(test_config, f)

        global_config = GlobalConfig(config_file=config_file)

        # Test ProfileStore with global config
        store = ProfileStore(global_config=global_config)
        assert store.global_config == global_config
        assert store.explicit_dir is None

    def test_profile_store_backwards_compatibility(self, tmp_path):
        """Test ProfileStore backwards compatibility with explicit directory."""
        explicit_dir = tmp_path / "explicit"
        explicit_dir.mkdir()

        store = ProfileStore(explicit_dir)
        assert store.explicit_dir == explicit_dir
        assert store.profiles_dir == explicit_dir

    def test_profile_store_hierarchical_discovery(self, tmp_path):
        """Test ProfileStore hierarchical profile discovery."""
        import os

        # Change to a temporary directory to avoid contamination from project files
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            config_dir = tmp_path / "config"
            config_dir.mkdir()
            config_file = config_dir / "config.json"

            # Create test config
            test_config = {"default_profile_dir": str(tmp_path / "profiles")}
            with open(config_file, "w") as f:
                json.dump(test_config, f)

            global_config = GlobalConfig(config_file=config_file)

            # Create profiles in global directory
            profiles_dir = tmp_path / "profiles"
            profiles_dir.mkdir()
            global_profile = profiles_dir / "test_settings.json"
            global_profile.write_text('{"env": {"ANTHROPIC_BASE_URL": "https://global.com"}}')

            store = ProfileStore(global_config=global_config)
            profiles = store.list_profiles()

            assert len(profiles) == 1
            assert profiles[0].name == "test"
        finally:
            os.chdir(original_cwd)