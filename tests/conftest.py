"""
Pytest configuration and fixtures for cc_api_switcher tests.

This module provides common fixtures and utilities for testing CLI commands
in both explicit directory mode and global configuration mode.
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Dict, Generator, List, Optional

import pytest
from typer.testing import CliRunner

from cc_api_switcher.cli import app
from cc_api_switcher.config import SettingsProfile, ProfileStore
from cc_api_switcher.global_config import GlobalConfig
from cc_api_switcher.core import CcApiSwitcher


@pytest.fixture
def runner():
    """Provide a CliRunner instance for testing."""
    return CliRunner()


@pytest.fixture
def global_config_fixture() -> Generator[GlobalConfig, None, None]:
    """
    Provide a temporary GlobalConfig instance for testing.

    Creates a temporary directory for XDG_CONFIG_HOME and initializes
    a clean GlobalConfig instance that doesn't interfere with user's
    actual configuration.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Set up temporary XDG config directory
        original_xdg = os.environ.get('XDG_CONFIG_HOME')
        original_profile_dir = os.environ.get('CC_API_SWITCHER_PROFILE_DIR')

        try:
            os.environ['XDG_CONFIG_HOME'] = temp_dir
            # Force reinitialization of GlobalConfig by clearing any cached instances
            if hasattr(GlobalConfig, '_instance'):
                delattr(GlobalConfig, '_instance')
            config = GlobalConfig()
            yield config
        finally:
            # Restore original environment
            if original_xdg is not None:
                os.environ['XDG_CONFIG_HOME'] = original_xdg
            elif 'XDG_CONFIG_HOME' in os.environ:
                del os.environ['XDG_CONFIG_HOME']

            if original_profile_dir is not None:
                os.environ['CC_API_SWITCHER_PROFILE_DIR'] = original_profile_dir
            elif 'CC_API_SWITCHER_PROFILE_DIR' in os.environ:
                del os.environ['CC_API_SWITCHER_PROFILE_DIR']


@pytest.fixture
def temp_global_profiles() -> Generator[Path, None, None]:
    """
    Provide a temporary directory for global profile testing.

    Creates a temporary profiles directory and sets CC_API_SWITCHER_PROFILE_DIR
    to point to it. Cleans up automatically after the test.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        profiles_dir = Path(temp_dir) / "profiles"
        profiles_dir.mkdir(parents=True, exist_ok=True)

        original_profile_dir = os.environ.get('CC_API_SWITCHER_PROFILE_DIR')
        try:
            os.environ['CC_API_SWITCHER_PROFILE_DIR'] = str(profiles_dir)
            yield profiles_dir
        finally:
            if original_profile_dir is not None:
                os.environ['CC_API_SWITCHER_PROFILE_DIR'] = original_profile_dir
            elif 'CC_API_SWITCHER_PROFILE_DIR' in os.environ:
                del os.environ['CC_API_SWITCHER_PROFILE_DIR']


@pytest.fixture
def mock_profile_store() -> Mock:
    """
    Provide a mocked ProfileStore for testing.

    Returns a Mock object that simulates ProfileStore behavior
    with controllable profile listings and configurations.
    """
    mock_store = Mock(spec=ProfileStore)
    mock_store.profiles_dir = None  # Simulates global mode
    mock_store.list_profiles.return_value = []
    mock_store.get_profile.return_value = None
    mock_store.profile_exists.return_value = False
    return mock_store


@pytest.fixture
def sample_profiles_data() -> Dict[str, Dict]:
    """
    Provide sample profile data for testing.

    Returns a dictionary of profile names to their configuration data,
    covering all supported providers with realistic test values.
    """
    return {
        "deepseek": {
            "env": {
                "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
                "ANTHROPIC_AUTH_TOKEN": "sk-1234567890abcdef",
                "ANTHROPIC_MODEL": "deepseek-chat",
                "API_TIMEOUT_MS": "600000",
            },
            "statusLine": {
                "type": "text",
                "text": "DeepSeek",
                "padding": 0
            },
            "alwaysThinkingEnabled": False
        },
        "glm": {
            "env": {
                "ANTHROPIC_BASE_URL": "https://open.bigmodel.cn/api/anthropic",
                "ANTHROPIC_AUTH_TOKEN": "sk-abcdef1234567890",
                "ANTHROPIC_MODEL": "glm-4",
                "API_TIMEOUT_MS": "300000",
            },
            "statusLine": {
                "type": "text",
                "text": "GLM",
                "padding": 0
            },
            "alwaysThinkingEnabled": True
        },
        "minimax": {
            "env": {
                "ANTHROPIC_BASE_URL": "https://api.minimaxi.com/v1/anthropic",
                "ANTHROPIC_AUTH_TOKEN": "sk-zyxw9876543210",
                "ANTHROPIC_MODEL": "abab6.5s-chat",
                "API_TIMEOUT_MS": "120000",
            },
            "statusLine": {
                "type": "text",
                "text": "MiniMax",
                "padding": 0
            },
            "alwaysThinkingEnabled": False
        },
        "qwen": {
            "env": {
                "ANTHROPIC_BASE_URL": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "ANTHROPIC_AUTH_TOKEN": "sk-0987654321fedcba",
                "ANTHROPIC_MODEL": "qwen-turbo",
                "API_TIMEOUT_MS": "240000",
            },
            "statusLine": {
                "type": "text",
                "text": "Qwen",
                "padding": 0
            },
            "alwaysThinkingEnabled": False
        },
        "kimi": {
            "env": {
                "ANTHROPIC_BASE_URL": "https://api.kimi.com/v1/anthropic",
                "ANTHROPIC_AUTH_TOKEN": "sk-bcaflkjihgqwertrewq",
                "ANTHROPIC_MODEL": "moonshot-v1-8k",
                "API_TIMEOUT_MS": "180000",
            },
            "statusLine": {
                "type": "text",
                "text": "Kimi",
                "padding": 0
            },
            "alwaysThinkingEnabled": True
        }
    }


@pytest.fixture
def temp_env_setup() -> Generator[callable, None, None]:
    """
    Provide a utility function for temporary environment variable setup.

    Yields a function that can set environment variables temporarily
    and automatically restore them after the test completes.
    """
    original_env = {}

    def set_temp_env(env_vars: Dict[str, str]):
        """Set temporary environment variables."""
        for key, value in env_vars.items():
            # Store original value if it exists
            if key in os.environ:
                original_env[key] = os.environ[key]
            os.environ[key] = value

    try:
        yield set_temp_env
    finally:
        # Restore original environment variables
        for key in list(original_env.keys()):
            if original_env[key] is None:
                if key in os.environ:
                    del os.environ[key]
            else:
                os.environ[key] = original_env[key]
        original_env.clear()


def create_profile_file(profiles_dir: Path, name: str, data: Dict) -> Path:
    """
    Utility function to create a profile file in the given directory.

    Args:
        profiles_dir: Directory where profile files should be created
        name: Profile name (without _settings.json suffix)
        data: Profile configuration data

    Returns:
        Path to the created profile file
    """
    profile_file = profiles_dir / f"{name}_settings.json"
    with open(profile_file, 'w') as f:
        json.dump(data, f, indent=2)
    return profile_file


def create_global_config(config_dir: Path, **kwargs) -> Path:
    """
    Utility function to create a global configuration file.

    Args:
        config_dir: Directory where config should be created
        **kwargs: Configuration values to override defaults

    Returns:
        Path to the created config file
    """
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "config.json"

    default_config = {
        "default_profile_dir": str(config_dir / "profiles"),
        "default_target_path": str(Path.home() / ".claude" / "settings.json"),
        "backup_retention_count": 10,
        "auto_backup": True
    }

    default_config.update(kwargs)

    with open(config_file, 'w') as f:
        json.dump(default_config, f, indent=2)

    return config_file


# Global test data that can be shared across tests
SAMPLE_TOKEN = "sk-1234567890abcdef1234567890abcdef"
SAMPLE_BASE_URL = "https://api.example.com/anthropic"
SAMPLE_MODEL = "test-model"


@pytest.fixture
def mock_settings_file(tmp_path: Path) -> Path:
    """
    Create a mock Claude settings file for testing.

    Returns the path to a temporary settings file with sample data.
    """
    settings_data = {
        "env": {
            "ANTHROPIC_BASE_URL": SAMPLE_BASE_URL,
            "ANTHROPIC_AUTH_TOKEN": SAMPLE_TOKEN,
            "ANTHROPIC_MODEL": SAMPLE_MODEL,
        },
        "statusLine": {
            "type": "text",
            "text": "Test",
            "padding": 0
        },
        "alwaysThinkingEnabled": False
    }

    settings_file = tmp_path / "settings.json"
    with open(settings_file, 'w') as f:
        json.dump(settings_data, f, indent=2)

    return settings_file