"""Core functionality for switching settings."""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .config import SettingsProfile, get_default_target_path, mask_token
from .exceptions import (
    BackupError,
    CcApiSwitcherError,
)


class CcApiSwitcher:
    """Handles switching between CC API settings profiles."""

    def __init__(
        self,
        target_path: Optional[Path] = None,
        backup_dir: Optional[Path] = None,
        global_config=None,
    ):
        """
        Initialize CC API switcher.

        Args:
            target_path: Optional target path for settings file
            backup_dir: Optional backup directory
            global_config: Optional GlobalConfig instance
        """
        # Use global config for default target path if provided
        if global_config and not target_path:
            self.target_path = global_config.get_default_target_path()
        else:
            self.target_path = target_path or get_default_target_path()

        # Create backup directory in XDG_CONFIG_HOME or .config
        if backup_dir:
            self.backup_dir = backup_dir
        else:
            config_dir = Path.home() / ".config" / "cc-api-switcher" / "backups"
            self.backup_dir = config_dir

        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def switch_to(
        self, profile: SettingsProfile, create_backup: bool = True
    ) -> Optional[Path]:
        """Switch to a profile."""
        issues = profile.validate_profile()

        if issues:
            error_msg = "Profile validation failed:\n" + "\n".join(
                f"  - {issue}" for issue in issues
            )
            raise CcApiSwitcherError(error_msg)

        if create_backup and self.target_path.exists():
            backup_path = self._create_backup()
            print(f"✓ Created backup: {backup_path}")

        try:
            # Write to temporary file first for atomicity
            temp_path = f"{self.target_path}.tmp.{os.getpid()}"
            with open(temp_path, "w") as f:
                json.dump(profile.to_dict(), f, indent=2)

            # Atomic move
            os.replace(temp_path, self.target_path)

            # Set secure permissions
            os.chmod(self.target_path, 0o600)

            return self.target_path

        except Exception as e:
            raise CcApiSwitcherError(f"Failed to switch to profile: {e}")

    def _create_backup(self) -> Optional[Path]:
        """Create a timestamped backup of current settings."""
        if not self.target_path.exists():
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{self.target_path.name}.backup.{timestamp}"
        backup_path = self.backup_dir / backup_name

        try:
            shutil.copy2(self.target_path, backup_path)

            # Keep only last 10 backups
            self._cleanup_old_backups()

            return backup_path

        except Exception as e:
            raise BackupError(f"Failed to create backup: {e}")

    def _cleanup_old_backups(self, keep: int = 10) -> None:
        """Remove old backups, keeping only the most recent."""
        backup_pattern = f"{self.target_path.name}.backup.*"
        backups = sorted(
            self.backup_dir.glob(backup_pattern),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        for old_backup in backups[keep:]:
            try:
                old_backup.unlink()
            except Exception:
                pass

    def list_backups(self) -> List[Path]:
        """List all available backups."""
        if not self.backup_dir.exists():
            return []

        backup_pattern = f"{self.target_path.name}.backup.*"
        backups = sorted(
            self.backup_dir.glob(backup_pattern),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        return backups

    def restore_backup(self, backup_path: Path) -> Path:
        """Restore from a backup file."""
        if not backup_path.exists():
            raise BackupError(f"Backup file not found: {backup_path}")

        # Create backup of current settings before restoring
        if self.target_path.exists():
            current_backup = self._create_backup()
            print(f"✓ Created backup of current settings: {current_backup}")

        try:
            shutil.copy2(backup_path, self.target_path)
            os.chmod(self.target_path, 0o600)
            return self.target_path

        except Exception as e:
            raise BackupError(f"Failed to restore backup: {e}")

    def get_current_profile(self) -> Optional[SettingsProfile]:
        """Get the currently active profile by reading the settings file."""
        if not self.target_path.exists():
            return None

        try:
            with open(self.target_path) as f:
                data = json.load(f)

            # Try to determine profile name from environment
            base_url = data.get("env", {}).get("ANTHROPIC_BASE_URL", "")

            # Create a temporary profile copy without the name field to extract provider
            data_for_temp = data.copy()
            data_for_temp.pop("name", None)  # Remove name to avoid conflict
            temp_profile = SettingsProfile(name="current", **data_for_temp)
            provider = temp_profile.provider

            # Determine the most likely profile name
            if "deepseek" in base_url.lower():
                name = "deepseek"
            elif "bigmodel" in base_url.lower():
                name = "glm"
            elif "minimaxi" in base_url.lower():
                name = "minimax"
            elif "dashscope" in base_url.lower():
                name = "qwen"
            else:
                name = f"current-{provider.lower()}"

            # Override the name in the original data
            data["name"] = name
            return SettingsProfile(**data)

        except Exception:
            return None

    def show_profile_info(self, profile: SettingsProfile) -> str:
        """Format profile information for display."""
        env = profile.env
        base_url = env.get("ANTHROPIC_BASE_URL", "N/A")
        auth_token = env.get("ANTHROPIC_AUTH_TOKEN", "N/A")
        masked_token = mask_token(auth_token)

        lines = [
            f"Profile: {profile.name}",
            f"Provider: {profile.provider}",
            f"Base URL: {base_url}",
            f"Auth Token: {masked_token}",
        ]

        if env.get("ANTHROPIC_MODEL"):
            lines.append(f"Model: {env['ANTHROPIC_MODEL']}")

        if env.get("API_TIMEOUT_MS"):
            timeout_ms = int(env.get("API_TIMEOUT_MS", 0))
            timeout_sec = timeout_ms / 1000
            lines.append(f"Timeout: {timeout_sec}s")

        if profile.enabled_plugins:
            enabled = [k for k, v in profile.enabled_plugins.items() if v]
            if enabled:
                lines.append(f"Enabled Plugins: {', '.join(enabled[:3])}")

        return "\n".join(lines)
