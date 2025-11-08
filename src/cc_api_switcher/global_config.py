"""
Global configuration management for CC API Switcher.

This module provides hierarchical configuration discovery and management
enabling true global usage of the CLI tool.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Union

from cc_api_switcher.exceptions import CcApiSwitcherError


class GlobalConfigError(CcApiSwitcherError):
    """Global configuration related errors."""
    pass


class GlobalConfig:
    """
    Manages global configuration with hierarchical discovery.

    Priority order for profile directory discovery:
    1. Command line --dir parameter (handled in CLI)
    2. CC_API_SWITCHER_PROFILE_DIR environment variable
    3. ~/.config/cc-api-switcher/profiles/ (global directory)
    4. Path.cwd() (local directory - backwards compatibility)
    """

    def __init__(self, config_file: Optional[Union[str, Path]] = None):
        """
        Initialize global configuration.

        Args:
            config_file: Optional path to configuration file
        """
        self.home_dir = Path.home()
        self.config_dir = self._get_config_dir()
        self.config_file = Path(config_file) if config_file else self.config_dir / "config.json"

        # If custom config file is provided, update config_dir to its parent
        if config_file:
            self.config_dir = self.config_file.parent
            self.global_profiles_dir = self.config_dir / "profiles"
        else:
            self.global_profiles_dir = self.config_dir / "profiles"

        # Note: Don't auto-create profiles directory here to avoid permission issues
        # Users should call ensure_global_profiles_dir() explicitly when needed

        # Load configuration if exists
        self._config: Dict[str, any] = {}
        self._load_config()

    def _get_config_dir(self) -> Path:
        """
        Get configuration directory following XDG Base Directory specification.

        Returns:
            Path to configuration directory
        """
        # Check XDG_CONFIG_HOME first
        xdg_config = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config:
            return Path(xdg_config) / "cc-api-switcher"

        # Fallback to ~/.config
        return self.home_dir / ".config" / "cc-api-switcher"

    def _load_config(self) -> None:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self._config = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                raise GlobalConfigError(f"Failed to load config from {self.config_file}: {e}")

    def save_config(self) -> None:
        """Save current configuration to file."""
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)

        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
        except IOError as e:
            raise GlobalConfigError(f"Failed to save config to {self.config_file}: {e}")

    def get_profile_directories(self) -> List[Path]:
        """
        Get list of profile directories in search order.

        Returns:
            List of directories to search for profiles
        """
        directories = []

        # Environment variable override
        env_dir = os.environ.get("CC_API_SWITCHER_PROFILE_DIR")
        if env_dir:
            directories.append(Path(env_dir).expanduser())

        # Global profiles directory
        if self._config.get("default_profile_dir"):
            default_dir = Path(self._config["default_profile_dir"]).expanduser()
            directories.append(default_dir)
        else:
            directories.append(self.global_profiles_dir)

        # Local directory (backwards compatibility)
        directories.append(Path.cwd())

        return directories

    def find_profile_file(self, profile_name: str) -> Optional[Path]:
        """
        Find profile file in search directories.

        Args:
            profile_name: Name of the profile (without _settings.json suffix)

        Returns:
            Path to profile file if found, None otherwise
        """
        profile_filename = f"{profile_name}_settings.json"

        for directory in self.get_profile_directories():
            profile_path = directory / profile_filename
            if profile_path.exists():
                return profile_path

        return None

    def list_available_profiles(self) -> List[Dict[str, str]]:
        """
        List all available profiles from search directories.

        Returns:
            List of dictionaries with profile information
        """
        profiles = {}
        seen_files = set()

        # Search in order, first occurrence wins
        for directory in self.get_profile_directories():
            if not directory.exists():
                continue

            for profile_file in directory.glob("*_settings.json"):
                if profile_file.name in seen_files:
                    continue  # Skip duplicates

                seen_files.add(profile_file.name)
                profile_name = profile_file.stem.replace("_settings", "")

                # Determine source type
                if directory == Path.cwd():
                    source = "local"
                elif directory == self.global_profiles_dir or \
                     (self._config.get("default_profile_dir") and
                      directory == Path(self._config["default_profile_dir"]).expanduser()):
                    source = "global"
                elif os.environ.get("CC_API_SWITCHER_PROFILE_DIR") and \
                     directory == Path(os.environ["CC_API_SWITCHER_PROFILE_DIR"]).expanduser():
                    source = "env"
                else:
                    source = "custom"

                profiles[profile_name] = {
                    "name": profile_name,
                    "file": str(profile_file),
                    "source": source
                }

        # Sort by name and return as list
        return sorted(profiles.values(), key=lambda x: x["name"])

    def ensure_global_profiles_dir(self) -> Path:
        """
        Ensure global profiles directory exists.

        Returns:
            Path to global profiles directory
        """
        self.global_profiles_dir.mkdir(parents=True, exist_ok=True)
        return self.global_profiles_dir

    def get_config_value(self, key: str, default: any = None) -> any:
        """
        Get configuration value.

        Args:
            key: Configuration key
            default: Default value if not found

        Returns:
            Configuration value or default
        """
        return self._config.get(key, default)

    def set_config_value(self, key: str, value: any) -> None:
        """
        Set configuration value.

        Args:
            key: Configuration key
            value: Value to set
        """
        self._config[key] = value

    def get_default_target_path(self) -> Path:
        """
        Get default target path for Claude settings.

        Returns:
            Path to Claude settings file
        """
        if self._config.get("default_target"):
            return Path(self._config["default_target"]).expanduser()
        return self.home_dir / ".claude" / "settings.json"

    def get_backup_retention_count(self) -> int:
        """
        Get backup retention count from configuration.

        Returns:
            Number of backups to retain
        """
        return self._config.get("backup_retention_count", 10)

    def is_auto_backup_enabled(self) -> bool:
        """
        Check if automatic backup is enabled.

        Returns:
            True if auto backup is enabled
        """
        return self._config.get("auto_backup", True)

    def initialize_config(self) -> None:
        """Initialize default configuration."""
        default_config = {
            "default_profile_dir": str(self.global_profiles_dir),
            "backup_retention_count": 10,
            "auto_backup": True,
            "search_order": ["global", "local"],
            "default_target": str(self.home_dir / ".claude" / "settings.json")
        }

        self._config = default_config
        self.save_config()

        # Ensure directories exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.global_profiles_dir.mkdir(parents=True, exist_ok=True)