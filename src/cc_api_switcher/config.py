"""Configuration and validation for settings profiles."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator

from .exceptions import InvalidProfileError, ProfileNotFoundError


class SettingsProfile(BaseModel):
    """Model for a settings profile."""

    name: str
    env: Dict[str, Any] = Field(default_factory=dict)
    status_line: Optional[Dict[str, Any]] = Field(None, alias="statusLine")
    enabled_plugins: Optional[Dict[str, bool]] = Field(None, alias="enabledPlugins")
    always_thinking_enabled: bool = Field(False, alias="alwaysThinkingEnabled")

    @property
    def provider(self) -> str:
        """Extract provider name from base URL or env."""
        base_url = self.env.get("ANTHROPIC_BASE_URL", "").lower()
        if "deepseek" in base_url:
            return "DeepSeek"
        elif "bigmodel" in base_url:
            return "GLM"
        elif "minimaxi" in base_url:
            return "MiniMax"
        elif "dashscope" in base_url:
            return "Qwen"
        elif "kimi" in base_url:
            return "Kimi"
        elif "deepseek" in self.name.lower():
            return "DeepSeek"
        elif "glm" in self.name.lower():
            return "GLM"
        elif "minimax" in self.name.lower():
            return "MiniMax"
        elif "qwen" in self.name.lower():
            return "Qwen"
        elif "kimi" in self.name.lower():
            return "Kimi"
        return "Unknown"

    @field_validator("env")
    @classmethod
    def validate_env(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate environment variables."""
        if not isinstance(v, dict):
            raise ValueError("env must be a dictionary")
        return v

    def validate_profile(self) -> List[str]:
        """Validate profile and return list of issues."""
        issues: List[str] = []

        if "ANTHROPIC_BASE_URL" not in self.env:
            issues.append("Missing ANTHROPIC_BASE_URL in env")
        else:
            base_url = self.env.get("ANTHROPIC_BASE_URL", "")
            if not base_url.startswith(("http://", "https://")):
                issues.append(
                    "Invalid ANTHROPIC_BASE_URL format (must start with http:// or https://)"
                )

        if "ANTHROPIC_AUTH_TOKEN" not in self.env:
            issues.append("Missing ANTHROPIC_AUTH_TOKEN in env")

        return issues

    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary."""
        return self.model_dump()

    @classmethod
    def from_file(
        cls, file_path: Path, name: Optional[str] = None
    ) -> "SettingsProfile":
        """Load profile from JSON file."""
        try:
            with open(file_path) as f:
                data = json.load(f)
        except FileNotFoundError:
            raise ProfileNotFoundError(f"Profile file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise InvalidProfileError(f"Invalid JSON in {file_path}: {e}")

        profile_name = name or file_path.stem.replace("_settings", "").replace("_", "-")
        return cls(name=profile_name, **data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any], name: str) -> "SettingsProfile":
        """Create profile from dictionary."""
        return cls(name=name, **data)


class ProfileStore:
    """Store and manage multiple profiles with global configuration support."""

    def __init__(self, profiles_dir: Optional[Path] = None, global_config=None):
        """
        Initialize profile store.

        Args:
            profiles_dir: Optional explicit directory (overrides global config)
            global_config: Optional GlobalConfig instance
        """
        # Import here to avoid circular imports
        from .global_config import GlobalConfig

        self.global_config = global_config or GlobalConfig()
        self.explicit_dir = profiles_dir

        # If explicit directory provided, use it (for backwards compatibility)
        if profiles_dir:
            self.profiles_dir = profiles_dir
            self.profiles_dir.mkdir(parents=True, exist_ok=True)
        else:
            # Use global config for profile discovery
            self.profiles_dir = None  # Not used in global mode

    def list_profiles(self) -> List[SettingsProfile]:
        """List all available profiles from all search directories."""
        profiles: List[SettingsProfile] = []
        seen_names = set()

        if self.explicit_dir:
            # Backwards compatibility: single directory mode
            for profile_file in self.explicit_dir.glob("*.json"):
                try:
                    profile = SettingsProfile.from_file(profile_file)
                    if profile.name not in seen_names:
                        profiles.append(profile)
                        seen_names.add(profile.name)
                except Exception:
                    # Skip invalid profiles
                    continue
        else:
            # Global mode: hierarchical discovery
            profile_info_list = self.global_config.list_available_profiles()
            for profile_info in profile_info_list:
                if profile_info["name"] not in seen_names:
                    try:
                        profile_path = Path(profile_info["file"])
                        profile = SettingsProfile.from_file(profile_path)
                        profiles.append(profile)
                        seen_names.add(profile_info["name"])
                    except Exception:
                        # Skip invalid profiles
                        continue

        return sorted(profiles, key=lambda p: p.name)

    def get_profile(self, name: str) -> SettingsProfile:
        """Get a profile by name using hierarchical discovery."""
        if self.explicit_dir:
            # Backwards compatibility: single directory mode
            profile_file = self.explicit_dir / f"{name}_settings.json"
            if not profile_file.exists():
                profile_file = self.explicit_dir / f"{name}.json"

            if not profile_file.exists():
                raise ProfileNotFoundError(f"Profile '{name}' not found")

            return SettingsProfile.from_file(profile_file, name=name)
        else:
            # Global mode: hierarchical discovery
            profile_path = self.global_config.find_profile_file(name)
            if not profile_path:
                # Provide helpful error message with available profiles
                available_profiles = [p["name"] for p in self.global_config.list_available_profiles()]
                if available_profiles:
                    profiles_str = ", ".join(available_profiles)
                    raise ProfileNotFoundError(
                        f"Profile '{name}' not found. Available profiles: {profiles_str}"
                    )
                else:
                    raise ProfileNotFoundError(
                        f"Profile '{name}' not found. No profiles found in any search directory. "
                        f"Use 'cc-api-switch init' to set up global configuration."
                    )

            return SettingsProfile.from_file(profile_path, name=name)

    def save_profile(self, profile: SettingsProfile, target_dir: Optional[Path] = None) -> None:
        """
        Save a profile to file.

        Args:
            profile: Profile to save
            target_dir: Optional target directory (defaults to global profiles dir)
        """
        if self.explicit_dir:
            # Backwards compatibility: save to explicit directory
            profile_file = self.explicit_dir / f"{profile.name}_settings.json"
        else:
            # Global mode: save to global profiles directory by default
            if target_dir:
                save_dir = target_dir
            else:
                save_dir = self.global_config.ensure_global_profiles_dir()
            profile_file = save_dir / f"{profile.name}_settings.json"

        with open(profile_file, "w") as f:
            json.dump(profile.to_dict(), f, indent=2)

    def get_profile_info(self, name: str) -> Optional[Dict[str, str]]:
        """
        Get profile information including source and location.

        Args:
            name: Profile name

        Returns:
            Dictionary with profile info or None if not found
        """
        if self.explicit_dir:
            # Backwards compatibility
            profile_file = self.explicit_dir / f"{name}_settings.json"
            if not profile_file.exists():
                profile_file = self.explicit_dir / f"{name}.json"

            if profile_file.exists():
                return {
                    "name": name,
                    "file": str(profile_file),
                    "source": "explicit"
                }
        else:
            # Global mode
            profile_info_list = self.global_config.list_available_profiles()
            for info in profile_info_list:
                if info["name"] == name:
                    return info

        return None

    def get_profile_path(self, name: str) -> Path:
        """
        Get the file path for a profile by name.

        This method works in both explicit and global modes without exposing
        internal directory attributes.

        Args:
            name: Profile name

        Returns:
            Path to the profile file (in explicit mode, returns path even if file doesn't exist)

        Raises:
            ProfileNotFoundError: In global mode, if the profile cannot be found
        """
        if self.explicit_dir:
            # Backwards compatibility: single directory mode
            # Return the preferred path even if file doesn't exist (for creation)
            return self.explicit_dir / f"{name}_settings.json"
        else:
            # Global mode: hierarchical discovery
            profile_path = self.global_config.find_profile_file(name)
            if not profile_path:
                raise ProfileNotFoundError(
                    f"Profile '{name}' not found. No profiles found in any search directory. "
                    f"Use 'cc-api-switch init' to set up global configuration."
                )
            return profile_path

    def profile_exists(self, name: str) -> bool:
        """
        Check if a profile file exists.

        This method works in both explicit and global modes without exposing
        internal directory attributes.

        Args:
            name: Profile name

        Returns:
            True if the profile file exists, False otherwise
        """
        if self.explicit_dir:
            # Backwards compatibility: single directory mode
            profile_file = self.explicit_dir / f"{name}_settings.json"
            if not profile_file.exists():
                profile_file = self.explicit_dir / f"{name}.json"
            return profile_file.exists()
        else:
            # Global mode: hierarchical discovery
            profile_path = self.global_config.find_profile_file(name)
            return profile_path is not None


def mask_token(token: str) -> str:
    """Mask API token for safe display."""
    if not token or len(token) < 8:
        return "*" * len(token) if token else ""

    # For tokens >= 8 chars: keep first 4, last 4, mask the middle
    if len(token) < 12:
        # If token is 8-11 chars, mask everything except first and last
        # (which means last 4 includes some of the masked part)
        # To preserve length, mask middle section
        middle_len = len(token) - 8
        return token[:4] + "*" * middle_len + token[-4:]

    # For tokens >= 12 chars: keep first 4, last 4, mask the middle
    # Use exactly 8 asterisks in the middle
    middle_len = len(token) - 8  # Calculate how many characters to mask
    return token[:4] + "*" * middle_len + token[-4:]


def get_default_target_path(global_config=None) -> Path:
    """
    Get the default target path for Claude settings.

    Args:
        global_config: Optional GlobalConfig instance

    Returns:
        Path to Claude settings file
    """
    if global_config:
        return global_config.get_default_target_path()

    # Fallback to default behavior
    return Path.home() / ".claude" / "settings.json"
