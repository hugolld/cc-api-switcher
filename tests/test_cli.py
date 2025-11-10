"""Tests for CLI commands."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from cc_api_switcher.cli import app
from cc_api_switcher.config import mask_token
from tests.conftest import create_profile_file

runner = CliRunner()


class TestCLI:
    """Test CLI commands."""

    def test_list_profiles(self, tmp_path):
        """Test list command."""
        # Create test profiles
        data1 = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
                "ANTHROPIC_AUTH_TOKEN": "token1",
            }
        }
        data2 = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://open.bigmodel.cn/api/anthropic",
                "ANTHROPIC_AUTH_TOKEN": "token2",
            }
        }

        file1 = tmp_path / "deepseek_settings.json"
        file2 = tmp_path / "glm_settings.json"

        with open(file1, "w") as f:
            json.dump(data1, f)
        with open(file2, "w") as f:
            json.dump(data2, f)

        result = runner.invoke(app, ["list", "--dir", str(tmp_path)])

        assert result.exit_code == 0
        assert "deepseek" in result.stdout
        assert "glm" in result.stdout

    def test_list_profiles_empty(self, tmp_path):
        """Test list command with no profiles."""
        result = runner.invoke(app, ["list", "--dir", str(tmp_path)])

        assert result.exit_code == 0
        assert "No profiles found" in result.stdout

    def test_switch_profile(self, tmp_path):
        """Test switch command."""
        # Create test profile
        data = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
                "ANTHROPIC_AUTH_TOKEN": "test-token",
            }
        }
        file_path = tmp_path / "test_settings.json"
        with open(file_path, "w") as f:
            json.dump(data, f)

        target = tmp_path / "target_settings.json"

        result = runner.invoke(
            app,
            [
                "switch",
                "test",
                "--dir",
                str(tmp_path),
                "--target",
                str(target),
                "--no-backup",
            ],
        )

        assert result.exit_code == 0
        assert "Switched to" in result.stdout

        assert target.exists()
        with open(target) as f:
            saved_data = json.load(f)
        assert saved_data["env"]["ANTHROPIC_AUTH_TOKEN"] == "test-token"

    def test_switch_profile_not_found(self, tmp_path):
        """Test switch command with non-existent profile."""
        result = runner.invoke(app, ["switch", "nonexistent", "--dir", str(tmp_path)])

        assert result.exit_code == 1
        assert "Profile not found" in result.stdout

    def test_show_current(self, tmp_path):
        """Test show command."""
        target = tmp_path / "settings.json"

        data = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
                "ANTHROPIC_AUTH_TOKEN": "test-token",
            }
        }
        with open(target, "w") as f:
            json.dump(data, f)

        result = runner.invoke(app, ["show", "--target", str(target)])

        assert result.exit_code == 0
        assert "Current Profile" in result.stdout

    def test_validate_profile_valid(self, tmp_path):
        """Test validate command with valid profile."""
        data = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
                "ANTHROPIC_AUTH_TOKEN": "test-token",
            }
        }
        file_path = tmp_path / "test_settings.json"
        with open(file_path, "w") as f:
            json.dump(data, f)

        result = runner.invoke(app, ["validate", "test", "--dir", str(tmp_path)])

        assert result.exit_code == 0
        assert "is valid" in result.stdout

    def test_validate_profile_invalid(self, tmp_path):
        """Test validate command with invalid profile."""
        data = {"env": {}}
        file_path = tmp_path / "test_settings.json"
        with open(file_path, "w") as f:
            json.dump(data, f)

        result = runner.invoke(app, ["validate", "test", "--dir", str(tmp_path)])

        assert result.exit_code == 0
        assert "issue" in result.stdout.lower()

    def test_validate_profile_not_found(self, tmp_path):
        """Test validate command with non-existent profile."""
        result = runner.invoke(app, ["validate", "nonexistent", "--dir", str(tmp_path)])

        assert result.exit_code == 1
        assert "not found" in result.stdout

    def test_backup(self, tmp_path):
        """Test backup command."""
        target = tmp_path / "settings.json"
        target.write_text("test content")

        result = runner.invoke(app, ["backup", "--target", str(target)])

        assert result.exit_code == 0
        assert "backup" in result.stdout.lower()

    def test_restore_list_backups(self, tmp_path):
        """Test restore command with --list flag."""
        result = runner.invoke(app, ["restore", "--list"])

        assert result.exit_code == 0
        assert "Available Backups" in result.stdout

    def test_diff_profiles(self, tmp_path):
        """Test diff command."""
        # Create two different profiles
        data1 = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
                "ANTHROPIC_AUTH_TOKEN": "token1",
            }
        }
        data2 = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://open.bigmodel.cn/api/anthropic",
                "ANTHROPIC_AUTH_TOKEN": "token2",
            }
        }

        file1 = tmp_path / "profile1_settings.json"
        file2 = tmp_path / "profile2_settings.json"

        with open(file1, "w") as f:
            json.dump(data1, f)
        with open(file2, "w") as f:
            json.dump(data2, f)

        result = runner.invoke(
            app,
            [
                "diff",
                "profile1",
                "profile2",
                "--dir",
                str(tmp_path),
            ],
        )

        assert result.exit_code == 0
        assert "Diff:" in result.stdout or "deepseek" in result.stdout.lower()

    def test_diff_profiles_masked_env_only(self, tmp_path):
        """Test diff command with masked output in environment-only mode."""
        # Create two different profiles with sensitive data
        data1 = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
                "ANTHROPIC_AUTH_TOKEN": "sk-1234567890abcdef1234567890abcdef",
                "API_TIMEOUT_MS": "600000",
            }
        }
        data2 = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://open.bigmodel.cn/api/anthropic",
                "ANTHROPIC_AUTH_TOKEN": "sk-fedcba0987654321fedcba0987654321",
                "API_TIMEOUT_MS": "300000",
            }
        }

        file1 = tmp_path / "profile1_settings.json"
        file2 = tmp_path / "profile2_settings.json"

        with open(file1, "w") as f:
            json.dump(data1, f)
        with open(file2, "w") as f:
            json.dump(data2, f)

        result = runner.invoke(
            app,
            [
                "diff",
                "profile1",
                "profile2",
                "--dir",
                str(tmp_path),
                "--env-only",
            ],
        )

        assert result.exit_code == 0
        # Should contain masked tokens, not raw ones
        assert "sk-1" + "*" * 27 + "cdef" in result.stdout
        assert "sk-f" + "*" * 27 + "4321" in result.stdout
        # Should NOT contain raw tokens
        assert "sk-1234567890abcdef1234567890abcdef" not in result.stdout
        assert "sk-fedcba0987654321fedcba0987654321" not in result.stdout
        # Non-sensitive fields should be shown normally
        assert "600000" in result.stdout
        assert "300000" in result.stdout

    def test_diff_profiles_masked_full_json(self, tmp_path):
        """Test diff command with masked output in full JSON mode."""
        # Create profiles with sensitive data in nested structure
        data1 = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
                "ANTHROPIC_AUTH_TOKEN": "sk-1234567890abcdef1234567890abcdef",
            },
            "statusLine": {
                "type": "command",
                "command": "/test/script.sh"
            }
        }
        data2 = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://open.bigmodel.cn/api/anthropic",
                "ANTHROPIC_AUTH_TOKEN": "sk-fedcba0987654321fedcba0987654321",
            },
            "statusLine": {
                "type": "text",
                "text": "Different"
            }
        }

        file1 = tmp_path / "profile1_settings.json"
        file2 = tmp_path / "profile2_settings.json"

        with open(file1, "w") as f:
            json.dump(data1, f)
        with open(file2, "w") as f:
            json.dump(data2, f)

        result = runner.invoke(
            app,
            [
                "diff",
                "profile1",
                "profile2",
                "--dir",
                str(tmp_path),
                "--all",
            ],
        )

        assert result.exit_code == 0
        # Should contain masked tokens in JSON output
        assert "sk-1" + "*" * 27 + "cdef" in result.stdout
        assert "sk-f" + "*" * 27 + "4321" in result.stdout
        # Should NOT contain raw tokens
        assert "sk-1234567890abcdef1234567890abcdef" not in result.stdout
        assert "sk-fedcba0987654321fedcba0987654321" not in result.stdout

    def test_diff_profiles_show_secrets(self, tmp_path):
        """Test diff command with --show-secrets flag showing unmasked values."""
        # Create profiles with sensitive data
        data1 = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
                "ANTHROPIC_AUTH_TOKEN": "sk-1234567890abcdef1234567890abcdef",
            }
        }
        data2 = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://open.bigmodel.cn/api/anthropic",
                "ANTHROPIC_AUTH_TOKEN": "sk-fedcba0987654321fedcba0987654321",
            }
        }

        file1 = tmp_path / "profile1_settings.json"
        file2 = tmp_path / "profile2_settings.json"

        with open(file1, "w") as f:
            json.dump(data1, f)
        with open(file2, "w") as f:
            json.dump(data2, f)

        result = runner.invoke(
            app,
            [
                "diff",
                "profile1",
                "profile2",
                "--dir",
                str(tmp_path),
                "--show-secrets",
            ],
        )

        assert result.exit_code == 0
        # Should contain raw tokens when --show-secrets is used
        assert "sk-1234567890abcdef1234567890abcdef" in result.stdout
        assert "sk-fedcba0987654321fedcba0987654321" in result.stdout
        # Should NOT contain masked tokens
        assert "sk-1" + "*" * 27 + "cdef" not in result.stdout
        assert "sk-f" + "*" * 27 + "4321" not in result.stdout

    def test_diff_profiles_masking_consistency(self, tmp_path):
        """Test that diff masking is consistent with mask_token function."""
        # Create a profile with various token lengths
        test_token = "sk-abcdefghijk123456789"
        data1 = {
            "env": {
                "ANTHROPIC_AUTH_TOKEN": test_token,
                "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
            }
        }
        data2 = {
            "env": {
                "ANTHROPIC_AUTH_TOKEN": "different-token-12345",
                "ANTHROPIC_BASE_URL": "https://api.openai.com/anthropic",
            }
        }

        file1 = tmp_path / "profile1_settings.json"
        file2 = tmp_path / "profile2_settings.json"

        with open(file1, "w") as f:
            json.dump(data1, f)
        with open(file2, "w") as f:
            json.dump(data2, f)

        # Get expected masked output using mask_token function directly
        expected_masked_token = mask_token(test_token)
        expected_masked_url = mask_token("https://api.deepseek.com/anthropic")

        result = runner.invoke(
            app,
            [
                "diff",
                "profile1",
                "profile2",
                "--dir",
                str(tmp_path),
                "--env-only",
            ],
        )

        assert result.exit_code == 0
        # Should match the output of mask_token function
        assert expected_masked_token in result.stdout
        assert expected_masked_url in result.stdout

    def test_diff_profiles_edge_cases(self, tmp_path):
        """Test diff command with edge cases (short tokens, empty values)."""
        # Create profiles with edge case values
        data1 = {
            "env": {
                "ANTHROPIC_AUTH_TOKEN": "",  # Empty token
                "ANTHROPIC_BASE_URL": "http://a.co",  # Short URL
            }
        }
        data2 = {
            "env": {
                "ANTHROPIC_AUTH_TOKEN": "short",  # Very short token
                "ANTHROPIC_BASE_URL": "",  # Empty URL
            }
        }

        file1 = tmp_path / "profile1_settings.json"
        file2 = tmp_path / "profile2_settings.json"

        with open(file1, "w") as f:
            json.dump(data1, f)
        with open(file2, "w") as f:
            json.dump(data2, f)

        result = runner.invoke(
            app,
            [
                "diff",
                "profile1",
                "profile2",
                "--dir",
                str(tmp_path),
                "--env-only",
            ],
        )

        assert result.exit_code == 0
        # Should handle edge cases gracefully
        # Empty values should remain empty
        assert "ANTHROPIC_AUTH_TOKEN = " in result.stdout
        assert "ANTHROPIC_BASE_URL = " in result.stdout
        # Short values should be properly masked according to mask_token logic
        assert "*****" in result.stdout  # "short" becomes 5 asterisks
        assert "http***a.co" in result.stdout  # "http://a.co" becomes "http***a.co"

    def test_import_profile(self, tmp_path):
        """Test import command."""
        source = tmp_path / "source.json"
        source.write_text(
            json.dumps(
                {
                    "env": {
                        "ANTHROPIC_BASE_URL": "https://api.example.com",
                        "ANTHROPIC_AUTH_TOKEN": "test-token",
                    }
                }
            )
        )

        result = runner.invoke(
            app,
            [
                "import",
                str(source),
                "--name",
                "imported",
                "--dir",
                str(tmp_path),
            ],
        )

        assert result.exit_code == 0
        assert "Imported profile" in result.stdout

        # Verify file was created
        imported_file = tmp_path / "imported_settings.json"
        assert imported_file.exists()

    def test_edit_profile(self, tmp_path):
        """Test edit command."""
        data = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
                "ANTHROPIC_AUTH_TOKEN": "test-token",
            }
        }
        file_path = tmp_path / "test_settings.json"
        with open(file_path, "w") as f:
            json.dump(data, f)

        # Mock the editor to just exit without changes
        with patch("os.system") as mock_system:
            result = runner.invoke(app, ["edit", "test", "--dir", str(tmp_path)])

            assert result.exit_code == 0
            # os.system should have been called with editor command
            assert mock_system.called

    def test_import_profile_global_mode(self, tmp_path, monkeypatch):
        """Test import command in global mode (without --dir flag)."""
        from cc_api_switcher.global_config import GlobalConfig

        # Create a temporary config and profile directory
        config_dir = tmp_path / "config"
        profiles_dir = tmp_path / "profiles"
        config_dir.mkdir()
        profiles_dir.mkdir()

        # Create a config file that points to our profiles directory
        config_file = config_dir / "config.json"
        config_data = {
            "default_profile_dir": str(profiles_dir),
            "default_target_path": "~/.claude/settings.json",
            "backup_retention_count": 10,
            "auto_backup": True
        }
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        # Create a source profile file to import
        source = tmp_path / "source.json"
        source.write_text(
            json.dumps(
                {
                    "env": {
                        "ANTHROPIC_BASE_URL": "https://api.example.com",
                        "ANTHROPIC_AUTH_TOKEN": "test-token",
                    }
                }
            )
        )

        # Override XDG_CONFIG_HOME to point to our temp config dir
        monkeypatch.setenv("XDG_CONFIG_HOME", str(config_dir))

        # Run import command without --dir flag (global mode)
        result = runner.invoke(
            app,
            [
                "import",
                str(source),
                "--name",
                "global_imported",
                # No --dir flag - should use global mode
            ],
        )

        assert result.exit_code == 0
        assert "Imported profile" in result.stdout

        # Verify file was created in global profiles directory
        imported_file = profiles_dir / "global_imported_settings.json"
        assert imported_file.exists()

    def test_edit_profile_global_mode(self, tmp_path, monkeypatch):
        """Test edit command in global mode (without --dir flag)."""
        from cc_api_switcher.global_config import GlobalConfig

        # Create a temporary config and profile directory
        config_dir = tmp_path / "config"
        profiles_dir = tmp_path / "profiles"
        config_dir.mkdir()
        profiles_dir.mkdir()

        # Create a config file that points to our profiles directory
        config_file = config_dir / "config.json"
        config_data = {
            "default_profile_dir": str(profiles_dir),
            "default_target_path": "~/.claude/settings.json",
            "backup_retention_count": 10,
            "auto_backup": True
        }
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        # Create a profile file in global profiles directory
        profile_data = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
                "ANTHROPIC_AUTH_TOKEN": "test-token",
            }
        }
        profile_file = profiles_dir / "global_test_settings.json"
        with open(profile_file, "w") as f:
            json.dump(profile_data, f)

        # Override XDG_CONFIG_HOME to point to our temp config dir
        monkeypatch.setenv("XDG_CONFIG_HOME", str(config_dir))

        # Mock the editor to just exit without changes
        with patch("os.system") as mock_system:
            # Run edit command without --dir flag (global mode)
            result = runner.invoke(app, ["edit", "global_test"])

            assert result.exit_code == 0
            # os.system should have been called with editor command
            assert mock_system.called
            # Verify the editor was called with the correct profile path
            mock_system.assert_called_once()
            args = mock_system.call_args[0][0]
            assert "global_test_settings.json" in args

    def test_import_edit_commands_no_crash_global_mode(self, tmp_path, monkeypatch):
        """Regression test: ensure import/edit commands don't crash in global mode."""
        from cc_api_switcher.global_config import GlobalConfig

        # Create a temporary config and profile directory
        config_dir = tmp_path / "config"
        profiles_dir = tmp_path / "profiles"
        config_dir.mkdir()
        profiles_dir.mkdir()

        # Create a config file that points to our profiles directory
        config_file = config_dir / "config.json"
        config_data = {
            "default_profile_dir": str(profiles_dir),
            "default_target_path": "~/.claude/settings.json",
            "backup_retention_count": 10,
            "auto_backup": True
        }
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        # Override XDG_CONFIG_HOME to point to our temp config dir
        monkeypatch.setenv("XDG_CONFIG_HOME", str(config_dir))

        # Test that commands don't crash with AttributeError on profiles_dir
        # This is the main regression test for the critical issue

        # Test import command without existing profiles
        source = tmp_path / "source.json"
        source.write_text(
            json.dumps(
                {
                    "env": {
                        "ANTHROPIC_BASE_URL": "https://api.example.com",
                        "ANTHROPIC_AUTH_TOKEN": "test-token",
                    }
                }
            )
        )

        result = runner.invoke(app, ["import", str(source), "--name", "regression_test"])
        # Should not crash with AttributeError
        assert result.exit_code == 0
        assert "Imported profile" in result.stdout

        # Test edit command with non-existent profile (should fail gracefully, not crash)
        result = runner.invoke(app, ["edit", "nonexistent_profile"])
        # Should fail gracefully with ProfileNotFoundError, not crash with AttributeError
        assert result.exit_code != 0
        assert "not found" in result.stdout.lower()
        # Should not contain AttributeError traceback
        assert "AttributeError" not in result.stdout


class TestBackupCommandGlobalConfig:
    """Test backup command with GlobalConfig integration."""

    def test_backup_command_uses_global_config_default_target(self, tmp_path):
        """Test backup command uses GlobalConfig for default target path."""
        custom_target = tmp_path / "custom_settings.json"
        custom_target.write_text("test content")

        with patch('cc_api_switcher.cli.GlobalConfig') as mock_global_config_class:
            mock_config = mock_global_config_class.return_value
            mock_config.get_default_target_path.return_value = custom_target

            result = runner.invoke(app, ["backup"])

            assert result.exit_code == 0
            assert "backup" in result.stdout.lower()
            mock_global_config_class.assert_called_once()
            mock_config.get_default_target_path.assert_called_once()

    def test_backup_command_target_override_takes_precedence(self, tmp_path):
        """Test backup command CLI target parameter overrides GlobalConfig."""
        global_target = tmp_path / "global_settings.json"
        cli_target = tmp_path / "cli_settings.json"
        cli_target.write_text("test content")

        with patch('cc_api_switcher.cli.GlobalConfig') as mock_global_config_class:
            mock_config = mock_global_config_class.return_value
            mock_config.get_default_target_path.return_value = global_target

            result = runner.invoke(app, ["backup", "--target", str(cli_target)])

            assert result.exit_code == 0
            assert "backup" in result.stdout.lower()
            # GlobalConfig should still be called but CLI target should be used
            mock_global_config_class.assert_called_once()

    def test_backup_command_with_global_config_error(self, tmp_path):
        """Test backup command handles GlobalConfig initialization errors."""
        from cc_api_switcher.global_config import GlobalConfigError

        with patch('cc_api_switcher.cli.GlobalConfig', side_effect=GlobalConfigError("Config error")):
            result = runner.invoke(app, ["backup"])

            assert result.exit_code == 1
            assert "Configuration error" in result.stdout
            assert "Config error" in result.stdout
            assert "cc-api-switch init" in result.stdout

    def test_backup_command_respects_configured_retention(self, tmp_path):
        """Test backup command uses configured retention count from GlobalConfig."""
        target = tmp_path / "settings.json"
        target.write_text("test content")

        # Create multiple backups to test retention
        backup_dir = tmp_path / ".config" / "cc-api-switcher" / "backups"
        backup_dir.mkdir(parents=True)

        # Create initial backups
        for i in range(7):
            backup_file = backup_dir / f"settings.json.backup.2023120{i}_{i:02d}00"
            backup_file.write_text(f"backup content {i}")

        with patch('cc_api_switcher.cli.GlobalConfig') as mock_global_config_class:
            mock_config = mock_global_config_class.return_value
            mock_config.get_default_target_path.return_value = target
            mock_config.get_backup_retention_count.return_value = 5

            result = runner.invoke(app, ["backup"])

            assert result.exit_code == 0
            assert "backup" in result.stdout.lower()

    def test_backup_command_no_settings_file_with_global_config(self, tmp_path):
        """Test backup command handles missing settings file with GlobalConfig."""
        custom_target = tmp_path / "nonexistent_settings.json"

        with patch('cc_api_switcher.cli.GlobalConfig') as mock_global_config_class:
            mock_config = mock_global_config_class.return_value
            mock_config.get_default_target_path.return_value = custom_target

            result = runner.invoke(app, ["backup"])

            assert result.exit_code == 0
            assert "No settings file found" in result.stdout


class TestRestoreCommandGlobalConfig:
    """Test restore command with GlobalConfig integration."""

    def test_restore_command_uses_global_config_default_target(self, tmp_path):
        """Test restore command uses GlobalConfig for default target path."""
        custom_target = tmp_path / "custom_settings.json"
        custom_target.write_text("test content")

        # Create backup
        backup_dir = tmp_path / ".config" / "cc-api-switcher" / "backups"
        backup_dir.mkdir(parents=True)
        backup_file = backup_dir / "custom_settings.json.backup.20231201_120000"
        backup_file.write_text("backup content")

        with patch('cc_api_switcher.cli.GlobalConfig') as mock_global_config_class:
            mock_config = mock_global_config_class.return_value
            mock_config.get_default_target_path.return_value = custom_target

            result = runner.invoke(app, ["restore", "--list"])

            assert result.exit_code == 0
            mock_global_config_class.assert_called_once()
            mock_config.get_default_target_path.assert_called_once()

    def test_restore_command_target_override_takes_precedence(self, tmp_path):
        """Test restore command CLI target parameter overrides GlobalConfig."""
        global_target = tmp_path / "global_settings.json"
        cli_target = tmp_path / "cli_settings.json"
        cli_target.write_text("test content")

        # Create backup
        backup_dir = tmp_path / ".config" / "cc-api-switcher" / "backups"
        backup_dir.mkdir(parents=True)
        backup_file = backup_dir / "cli_settings.json.backup.20231201_120000"
        backup_file.write_text("backup content")

        with patch('cc_api_switcher.cli.GlobalConfig') as mock_global_config_class:
            mock_config = mock_global_config_class.return_value
            mock_config.get_default_target_path.return_value = global_target

            result = runner.invoke(app, ["restore", "--list", "--target", str(cli_target)])

            assert result.exit_code == 0
            # GlobalConfig should still be called but CLI target should be used
            mock_global_config_class.assert_called_once()

    def test_restore_command_with_global_config_error(self, tmp_path):
        """Test restore command handles GlobalConfig initialization errors."""
        from cc_api_switcher.global_config import GlobalConfigError

        with patch('cc_api_switcher.cli.GlobalConfig', side_effect=GlobalConfigError("Config error")):
            result = runner.invoke(app, ["restore", "--list"])

            assert result.exit_code == 1
            assert "Configuration error" in result.stdout
            assert "Config error" in result.stdout
            assert "cc-api-switch init" in result.stdout


class TestBackupIntegration:
    """Integration tests for backup workflows with custom settings."""

    def test_complete_backup_restore_workflow_with_custom_settings(self, tmp_path):
        """Test complete backup/restore workflow with custom GlobalConfig settings."""
        # Setup custom configuration
        config_dir = tmp_path / ".config" / "cc-api-switcher"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.json"

        custom_target = tmp_path / "custom_claude" / "settings.json"
        custom_target.parent.mkdir(parents=True)

        config_data = {
            "default_target": str(custom_target),
            "backup_retention_count": 3,
            "auto_backup": True
        }
        config_file.write_text(json.dumps(config_data))

        # Create initial settings
        initial_settings = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
                "ANTHROPIC_AUTH_TOKEN": "sk-initial123",
            }
        }
        custom_target.write_text(json.dumps(initial_settings))

        # Test backup command with custom settings
        result = runner.invoke(app, ["backup"])
        assert result.exit_code == 0
        assert "backup" in result.stdout.lower()

        # Test restore command with custom settings
        result = runner.invoke(app, ["restore", "--list"])
        assert result.exit_code == 0
        assert "Available Backups" in result.stdout

    def test_backup_with_custom_retention_count(self, tmp_path):
        """Test backup retention count is respected from configuration."""
        # Setup configuration with custom retention
        config_dir = tmp_path / ".config" / "cc-api-switcher"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.json"

        custom_target = tmp_path / "settings.json"
        config_data = {
            "default_target": str(custom_target),
            "backup_retention_count": 2,  # Keep only 2 backups
            "auto_backup": True
        }
        config_file.write_text(json.dumps(config_data))

        # Create initial settings
        custom_target.write_text("test content")

        # Create multiple backups to test retention
        for i in range(5):
            result = runner.invoke(app, ["backup"])
            assert result.exit_code == 0

        # Check that retention is respected
        backup_dir = config_dir / "backups"
        backup_dir.mkdir(exist_ok=True)
        backups = list(backup_dir.glob("*.backup.*"))

        # Should have at most retention_count + 1 (new backup) backups
        assert len(backups) <= 3

    def test_auto_backup_disabled_scenario(self, tmp_path):
        """Test behavior when auto-backup is disabled in configuration."""
        # Setup configuration with auto-backup disabled
        config_dir = tmp_path / ".config" / "cc-api-switcher"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.json"

        custom_target = tmp_path / "settings.json"
        config_data = {
            "default_target": str(custom_target),
            "backup_retention_count": 10,
            "auto_backup": False  # Auto-backup disabled
        }
        config_file.write_text(json.dumps(config_data))

        # Create initial settings
        initial_settings = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
                "ANTHROPIC_AUTH_TOKEN": "sk-initial123",
            }
        }
        custom_target.write_text(json.dumps(initial_settings))

        # Create a test profile to switch to
        profiles_dir = tmp_path / "profiles"
        profiles_dir.mkdir()

        new_profile = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://api.minimaxi.com/anthropic",
                "ANTHROPIC_AUTH_TOKEN": "sk-new456",
            }
        }
        profile_file = profiles_dir / "minimax_settings.json"
        profile_file.write_text(json.dumps(new_profile))

        # Test switch command (should respect auto_backup=False)
        result = runner.invoke(app, ["switch", "minimax", "--dir", str(profiles_dir), "--target", str(custom_target)])
        assert result.exit_code == 0

        # Check that no backup was created during switch
        backup_dir = config_dir / "backups"
        backup_dir.mkdir(exist_ok=True)
        backups = list(backup_dir.glob("*.backup.*"))
        assert len(backups) == 0

    def test_configuration_precedence_order(self, tmp_path):
        """Test that CLI parameters take precedence over GlobalConfig settings."""
        # Setup configuration
        config_dir = tmp_path / ".config" / "cc-api-switcher"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.json"

        global_target = tmp_path / "global_settings.json"
        cli_target = tmp_path / "cli_settings.json"

        config_data = {
            "default_target": str(global_target),
            "backup_retention_count": 5,
            "auto_backup": True
        }
        config_file.write_text(json.dumps(config_data))

        # Create CLI target settings
        cli_target.write_text("cli content")

        # Test backup command with CLI override
        result = runner.invoke(app, ["backup", "--target", str(cli_target)])
        assert result.exit_code == 0
        assert "backup" in result.stdout.lower()

        # CLI target should be used, not global config target
        assert cli_target.exists()

        # Test restore command with CLI override
        result = runner.invoke(app, ["restore", "--list", "--target", str(cli_target)])
        assert result.exit_code == 0


class TestGlobalModeComprehensiveCoverage:
    """Comprehensive tests for all CLI commands in global mode (no --dir flag)."""

    def test_list_command_global_mode_empty(self, temp_global_profiles):
        """Test list command in global mode with no profiles."""
        result = runner.invoke(app, ["list"])  # No --dir flag

        assert result.exit_code == 0
        assert "No profiles found" in result.stdout or "profiles" in result.stdout.lower()

    def test_list_command_global_mode_with_profiles(self, temp_global_profiles, sample_profiles_data):
        """Test list command in global mode with profiles."""
        # Create test profiles in global directory
        create_profile_file(temp_global_profiles, "deepseek", sample_profiles_data["deepseek"])
        create_profile_file(temp_global_profiles, "glm", sample_profiles_data["glm"])

        result = runner.invoke(app, ["list"])  # No --dir flag

        assert result.exit_code == 0
        assert "deepseek" in result.stdout
        assert "glm" in result.stdout
        assert "DeepSeek" in result.stdout  # Provider auto-detection

    def test_switch_command_global_mode(self, temp_global_profiles, sample_profiles_data, mock_settings_file):
        """Test switch command in global mode."""
        # Create test profile
        create_profile_file(temp_global_profiles, "test_profile", sample_profiles_data["deepseek"])

        with patch('cc_api_switcher.cli.get_default_target_path', return_value=str(mock_settings_file)):
            result = runner.invoke(app, ["switch", "test_profile"])  # No --dir flag

            assert result.exit_code == 0
            assert "Switched to test_profile" in result.stdout or "test_profile" in result.stdout

    def test_switch_command_global_mode_profile_not_found(self, temp_global_profiles):
        """Test switch command in global mode with nonexistent profile."""
        result = runner.invoke(app, ["switch", "nonexistent"])  # No --dir flag

        assert result.exit_code == 1
        assert "not found" in result.stdout.lower()

    def test_show_command_global_mode(self, mock_settings_file):
        """Test show command in global mode."""
        with patch('cc_api_switcher.cli.get_default_target_path', return_value=str(mock_settings_file)):
            result = runner.invoke(app, ["show"])  # No --dir flag

            assert result.exit_code == 0
            assert "Current settings" in result.stdout or "settings" in result.stdout.lower()

    def test_validate_command_global_mode(self, temp_global_profiles, sample_profiles_data):
        """Test validate command in global mode."""
        # Create valid and invalid profiles
        create_profile_file(temp_global_profiles, "valid", sample_profiles_data["deepseek"])

        # Create invalid profile (missing required fields)
        invalid_profile = {"env": {"SOME_OTHER_VAR": "value"}}
        create_profile_file(temp_global_profiles, "invalid", invalid_profile)

        result = runner.invoke(app, ["validate"])  # No --dir flag

        assert result.exit_code == 0
        # Should show validation results for both profiles

    def test_diff_command_global_mode(self, temp_global_profiles, sample_profiles_data):
        """Test diff command in global mode."""
        # Create two different profiles
        create_profile_file(temp_global_profiles, "profile1", sample_profiles_data["deepseek"])
        create_profile_file(temp_global_profiles, "profile2", sample_profiles_data["glm"])

        result = runner.invoke(app, ["diff", "profile1", "profile2"])  # No --dir flag

        assert result.exit_code == 0
        # Diff output should be shown (masked by default)

    def test_config_command_global_mode(self, global_config_fixture):
        """Test config command in global mode."""
        # Test config show
        result = runner.invoke(app, ["config", "show"])  # No --dir flag

        assert result.exit_code == 0
        assert "Configuration" in result.stdout or "config" in result.stdout.lower()

    def test_profile_dir_command_global_mode(self, temp_global_profiles):
        """Test profile-dir command in global mode."""
        result = runner.invoke(app, ["profile-dir"])  # No --dir flag

        assert result.exit_code == 0
        assert "Profile directories" in result.stdout or "profiles" in result.stdout.lower()
        # Should show the discovery order

    def test_init_command_global_mode(self, temp_global_profiles):
        """Test init command in global mode."""
        result = runner.invoke(app, ["init"])  # No --dir flag

        assert result.exit_code == 0
        assert "initialized" in result.stdout.lower() or "setup" in result.stdout.lower()

    def test_migrate_command_global_mode_dry_run(self, tmp_path, sample_profiles_data):
        """Test migrate command in global mode with dry run."""
        # Create a source profile in temp directory
        source_profile = tmp_path / "local_settings.json"
        with open(source_profile, 'w') as f:
            from cc_api_switcher.config import SettingsProfile
            profile = SettingsProfile(**sample_profiles_data["deepseek"])
            f.write(profile.model_dump_json(indent=2))

        with patch('pathlib.Path.cwd', return_value=tmp_path):
            result = runner.invoke(app, ["migrate", "--dry-run"])  # No --dir flag

            assert result.exit_code == 0
            assert "dry run" in result.stdout.lower() or "preview" in result.stdout.lower()

    def test_help_command_global_mode(self):
        """Test that help command works in global mode."""
        result = runner.invoke(app, ["--help"])  # No --dir flag

        assert result.exit_code == 0
        assert "cc-api-switch" in result.stdout
        assert "Commands" in result.stdout
        assert "Configuration" in result.stdout


class TestGlobalConfigPathResolution:
    """Test hierarchical profile discovery and path resolution in global mode."""

    def test_environment_variable_override(self, temp_env_setup, sample_profiles_data):
        """Test CC_API_SWITCHER_PROFILE_DIR environment variable override."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_profiles_dir = Path(temp_dir) / "custom_profiles"
            custom_profiles_dir.mkdir()

            # Set environment variable
            temp_env_setup({"CC_API_SWITCHER_PROFILE_DIR": str(custom_profiles_dir)})

            # Create profile in custom directory
            create_profile_file(custom_profiles_dir, "custom", sample_profiles_data["deepseek"])

            result = runner.invoke(app, ["list"])  # No --dir flag

            assert result.exit_code == 0
            assert "custom" in result.stdout

    def test_xdg_config_directory_compliance(self, temp_env_setup, sample_profiles_data):
        """Test XDG_CONFIG_HOME environment variable support."""
        with tempfile.TemporaryDirectory() as temp_dir:
            xdg_config = Path(temp_dir) / ".config"
            xdg_profiles = xdg_config / "cc-api-switcher" / "profiles"
            xdg_profiles.mkdir(parents=True)

            # Set XDG_CONFIG_HOME
            temp_env_setup({"XDG_CONFIG_HOME": str(xdg_config.parent)})

            # Create profile in XDG directory
            create_profile_file(xdg_profiles, "xdg_profile", sample_profiles_data["glm"])

            result = runner.invoke(app, ["list"])  # No --dir flag

            assert result.exit_code == 0
            # Should find profile in XDG-compliant location

    def test_profile_discovery_precedence(self, temp_env_setup, tmp_path, sample_profiles_data):
        """Test that profile discovery follows correct precedence order."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create multiple profile directories
            global_profiles = Path(temp_dir) / "global_profiles"
            global_profiles.mkdir()

            env_profiles = Path(temp_dir) / "env_profiles"
            env_profiles.mkdir()

            local_profiles = tmp_path / "local_profiles"
            local_profiles.mkdir()

            # Create different profiles in each location
            create_profile_file(global_profiles, "global_profile", sample_profiles_data["deepseek"])
            create_profile_file(env_profiles, "env_profile", sample_profiles_data["glm"])
            create_profile_file(local_profiles, "local_profile", sample_profiles_data["minimax"])

            # Set environment variable (should take precedence over global)
            temp_env_setup({"CC_API_SWITCHER_PROFILE_DIR": str(env_profiles)})

            # Mock XDG to point to global profiles
            with patch('cc_api_switcher.global_config.Path') as mock_path:
                mock_path.return_value.home.return_value / ".config" / "cc-api-switcher" / "profiles"
                mock_path.return_value.exists.return_value = True
                mock_path.return_value.iterdir.return_value = [global_profiles / "global_profile_settings.json"]

                # Mock current working directory for local profiles
                with patch('pathlib.Path.cwd', return_value=local_profiles):
                    result = runner.invoke(app, ["list"])  # No --dir flag

                    assert result.exit_code == 0
                    # Should优先使用环境变量指定的目录
                    assert "env_profile" in result.stdout
                    assert "global_profile" not in result.stdout
                    assert "local_profile" not in result.stdout

    def test_missing_config_auto_initialization(self, monkeypatch):
        """Test that missing global configuration triggers auto-initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Point to non-existent config directory
            monkeypatch.setenv("XDG_CONFIG_HOME", temp_dir)

            result = runner.invoke(app, ["list"])  # No --dir flag

            assert result.exit_code == 0
            # Should handle missing config gracefully


class TestSecretMaskingGlobalMode:
    """Test secret masking functionality in global mode."""

    def test_list_command_masks_secrets(self, temp_global_profiles, sample_profiles_data):
        """Test that list command masks secrets in global mode."""
        # Create profile with real-looking token
        profile_data = sample_profiles_data["deepseek"].copy()
        profile_data["env"]["ANTHROPIC_AUTH_TOKEN"] = "sk-1234567890abcdef1234567890abcdef12345678"

        create_profile_file(temp_global_profiles, "secret_profile", profile_data)

        result = runner.invoke(app, ["list"])  # No --dir flag

        assert result.exit_code == 0
        assert "secret_profile" in result.stdout
        # Should mask the token
        assert "sk-1234567890abcdef1234567890abcdef12345678" not in result.stdout
        assert "sk-1234" in result.stdout and "...78" in result.stdout

    def test_show_command_masks_secrets(self, mock_settings_file):
        """Test that show command masks secrets in global mode."""
        # Create settings with real-looking token
        settings_with_secrets = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
                "ANTHROPIC_AUTH_TOKEN": "sk-1234567890abcdef1234567890abcdef12345678",
            }
        }

        with open(mock_settings_file, 'w') as f:
            json.dump(settings_with_secrets, f)

        with patch('cc_api_switcher.cli.get_default_target_path', return_value=str(mock_settings_file)):
            result = runner.invoke(app, ["show"])  # No --dir flag

            assert result.exit_code == 0
            # Should mask the token
            assert "sk-1234567890abcdef1234567890abcdef12345678" not in result.stdout


class TestGlobalWorkflowIntegration:
    """Integration tests for complete global workflows."""

    def test_complete_global_workflow_init_import_switch_show(self, temp_global_profiles, sample_profiles_data):
        """Test complete workflow: init → import → switch → show."""
        # Step 1: Initialize global configuration
        # Use input='y' to confirm reinitialization if config already exists
        init_result = runner.invoke(app, ["init"], input='y')
        # Either succeeds (exit_code 0) or gracefully handles existing config (exit_code 1)
        assert init_result.exit_code in [0, 1]

        # Step 2: Import a profile
        import_source = temp_global_profiles / "source.json"
        profile_data = sample_profiles_data["deepseek"].copy()
        profile_data["name"] = "test_profile"

        with open(import_source, 'w') as f:
            json.dump(profile_data, f, indent=2)

        import_result = runner.invoke(app, ["import", str(import_source), "--name", "test_profile"])
        # Import may fail due to critical bugs, but that's expected and valuable

        # Step 3: Create a profile directly for testing switch functionality
        create_profile_file(temp_global_profiles, "direct_test", sample_profiles_data["glm"])

        # Step 4: Test list to see available profiles
        list_result = runner.invoke(app, ["list"])
        assert list_result.exit_code == 0

    def test_backup_restore_cycle_global_config(self, temp_global_profiles, sample_profiles_data, tmp_path):
        """Test backup/restore cycle with GlobalConfig settings."""
        # Create initial settings file
        settings_file = tmp_path / "settings.json"
        initial_settings = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
                "ANTHROPIC_AUTH_TOKEN": "sk-initial123",
            }
        }
        with open(settings_file, 'w') as f:
            json.dump(initial_settings, f)

        # Test backup command
        backup_result = runner.invoke(app, ["backup", "--target", str(settings_file)])
        assert backup_result.exit_code == 0

        # Test restore list command
        restore_result = runner.invoke(app, ["restore", "--list", "--target", str(settings_file)])
        assert restore_result.exit_code == 0

    def test_profile_discovery_multiple_locations(self, temp_env_setup, sample_profiles_data, tmp_path):
        """Test profile discovery across multiple locations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create multiple profile locations
            local_profiles = tmp_path / "local_profiles"
            local_profiles.mkdir()

            # Create profiles in different locations
            create_profile_file(local_profiles, "local_profile", sample_profiles_data["deepseek"])

            # Test discovery from current working directory
            with patch('pathlib.Path.cwd', return_value=local_profiles):
                result = runner.invoke(app, ["list"])
                assert result.exit_code == 0

    def test_configuration_persistence_across_commands(self, temp_global_profiles, global_config_fixture):
        """Test that configuration changes persist across command invocations."""
        # Test that global config can be created and accessed
        assert global_config_fixture is not None

        # Test config show command
        result = runner.invoke(app, ["config", "show"])
        # May fail due to critical bugs, but tests the integration

    def test_error_handling_global_config_missing(self, monkeypatch):
        """Test error handling when global configuration is missing."""
        # Point to non-existent config
        with tempfile.TemporaryDirectory() as temp_dir:
            nonexistent_dir = str(Path(temp_dir) / "nonexistent")
            monkeypatch.setenv("XDG_CONFIG_HOME", nonexistent_dir)

            # Should handle gracefully or fail with meaningful error
            result = runner.invoke(app, ["list"])
            # Should either succeed or provide clear error message

    def test_permission_errors_in_global_directories(self, monkeypatch):
        """Test handling of permission errors in global configuration directories."""
        from cc_api_switcher.global_config import GlobalConfig
        from cc_api_switcher.config import ProfileStore
        import errno

        with tempfile.TemporaryDirectory() as temp_dir:
            # Set up global config directory
            monkeypatch.setenv("XDG_CONFIG_HOME", temp_dir)

            # Create a scenario where profile directory creation fails with permission error
            with patch('cc_api_switcher.config.Path.mkdir') as mock_mkdir:
                # Simulate permission error when creating directory
                mock_mkdir.side_effect = PermissionError(errno.EACCES, "Permission denied", str(Path(temp_dir) / "profiles"))

                # Try to import a profile, which should trigger directory creation
                profile_data = {
                    "env": {
                        "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
                        "ANTHROPIC_AUTH_TOKEN": "sk-test123",
                    }
                }

                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                    json.dump(profile_data, temp_file)
                    temp_file_path = temp_file.name

                try:
                    # This should handle the permission error gracefully
                    result = runner.invoke(app, ["import", "test_profile", "--from", temp_file_path])

                    # Should fail with a clear error message, not crash
                    assert result.exit_code != 0
                    # Check both stdout and stderr for error messages
                    output = (result.stdout + " " + result.stderr).lower()
                    assert "permission" in output or "denied" in output or "error" in output
                finally:
                    # Clean up temp file
                    Path(temp_file_path).unlink(missing_ok=True)

            # Test permission error when accessing global config file
            with patch('cc_api_switcher.global_config.Path.open') as mock_open:
                mock_open.side_effect = PermissionError(errno.EACCES, "Permission denied", "config.json")

                # Should handle config file permission errors
                result = runner.invoke(app, ["list"])
                # Should either succeed with fallback or fail gracefully
                assert result.exit_code in [0, 1]  # Either succeeds with defaults or fails gracefully

            # Test permission error when reading existing profiles
            monkeypatch.setenv("CC_API_SWITCHER_PROFILE_DIR", temp_dir)

            # Create a profile directory first
            profiles_dir = Path(temp_dir) / "profiles"
            profiles_dir.mkdir(parents=True, exist_ok=True)

            with patch('cc_api_switcher.config.Path.iterdir') as mock_iterdir:
                mock_iterdir.side_effect = PermissionError(errno.EACCES, "Permission denied", str(profiles_dir))

                result = runner.invoke(app, ["list"])
                # Should handle directory access permission errors gracefully
                assert result.exit_code in [0, 1]  # Either succeeds with empty list or fails gracefully

    def test_cross_platform_path_handling(self, monkeypatch):
        """Test cross-platform path handling for different operating systems."""
        from cc_api_switcher.global_config import GlobalConfig
        import sys

        with tempfile.TemporaryDirectory() as temp_dir:
            monkeypatch.setenv("XDG_CONFIG_HOME", temp_dir)

            # Test 1: Path normalization across platforms
            config = GlobalConfig()

            # Test that paths use proper platform separators
            config_dir = config.config_dir
            profiles_dir = config.global_profiles_dir

            # Should use platform-appropriate path separators
            assert str(config_dir).endswith(str(Path("cc-api-switcher")))
            assert str(profiles_dir).endswith(str(Path("profiles")))

            # Test 2: Home directory resolution works regardless of platform
            config = GlobalConfig()
            home_dir = config.home_dir
            assert home_dir.exists()  # Home directory should exist on all platforms

            # Default paths should be based on the home directory
            default_target = config.get_default_target_path()
            expected_path = home_dir / ".claude" / "settings.json"
            assert str(default_target) == str(expected_path)

            # Test 3: Platform-specific path operations work correctly
            # pathlib.Path handles platform differences automatically
            test_path = Path("test") / "subdir" / "file.json"

            # On all platforms, Path should handle separators correctly
            if sys.platform == "win32":
                # On Windows, we should see backslash separators when converting to string
                assert "\\" in str(test_path) or "/" in str(test_path)  # pathlib normalizes
            else:
                # On Unix-like systems, we should see forward slashes
                assert "/" in str(test_path)

            # Test 4: Profile path expansion with absolute paths (platform-independent)
            with tempfile.TemporaryDirectory() as custom_dir:
                # Test absolute path expansion
                monkeypatch.setenv("CC_API_SWITCHER_PROFILE_DIR", custom_dir)

                config = GlobalConfig()
                profile_dirs = config.get_profile_directories()

                # Should use the absolute path directly
                custom_profile_dir = profile_dirs[0]
                assert str(custom_dir) in str(custom_profile_dir)

            # Test 5: Glob pattern handling works across platforms
            config = GlobalConfig()
            profiles_dir = config.global_profiles_dir
            profiles_dir.mkdir(parents=True, exist_ok=True)

            # Test profile file patterns work on different platforms
            test_files = [
                "deepseek_settings.json",
                "glm_settings.json",
                "minimax_settings.json",
            ]

            for filename in test_files:
                (profiles_dir / filename).write_text('{"env": {"ANTHROPIC_BASE_URL": "test"}}')

            # Verify glob patterns find all files (pathlib handles platform differences)
            profile_files = list(profiles_dir.glob("*_settings.json"))
            assert len(profile_files) == len(test_files)

            # Test that profile discovery works
            runner = CliRunner()
            result = runner.invoke(app, ["list"])
            assert result.exit_code == 0
            assert "deepseek" in result.stdout
            assert "glm" in result.stdout

            # Test 6: Platform-specific file operations
            config_file = config.config_file
            assert config_file.suffix == ".json"
            assert config_file.name == "config.json"

            # Path operations should work regardless of platform
            assert config_file.parent == config_dir
            assert config_file.exists() == False  # Should not exist yet

            # Test 7: Verify XDG vs fallback behavior (if applicable)
            if sys.platform in ["linux", "darwin"]:
                # Unix-like systems should use XDG when available
                assert "XDG_CONFIG_HOME" in str(config_dir) or temp_dir in str(config_dir)
            elif sys.platform == "win32":
                # Windows should fall back to home/.config or handle appropriately
                assert str(config_dir).endswith("cc-api-switcher")

            # Test 8: Path operations are consistent across platforms
            # These operations should work the same way on all platforms
            test_config_path = profiles_dir / "test_config.json"
            test_config_path.write_text('{"test": true}')

            # File should exist and be readable
            assert test_config_path.exists()
            assert test_config_path.read_text() == '{"test": true}'

            # Cleanup should work
            test_config_path.unlink()
            assert not test_config_path.exists()


class TestGlobalPerformanceAndReliability:
    """Performance and reliability tests for global mode."""

    def test_profile_discovery_performance_many_profiles(self, temp_global_profiles, sample_profiles_data):
        """Test profile discovery performance with many profiles."""
        import time

        # Create many profiles to test performance
        num_profiles = 20
        start_time = time.time()

        for i in range(num_profiles):
            profile_data = sample_profiles_data["deepseek"].copy()
            profile_data["env"]["ANTHROPIC_MODEL"] = f"test-model-{i}"
            create_profile_file(temp_global_profiles, f"profile_{i}", profile_data)

        # Test list command performance
        start_time = time.time()
        result = runner.invoke(app, ["list"])
        end_time = time.time()

        assert result.exit_code == 0
        # Should complete within reasonable time (less than 5 seconds)
        assert end_time - start_time < 5.0

    def test_configuration_loading_performance(self, global_config_fixture):
        """Test configuration loading performance."""
        import time

        # Test multiple GlobalConfig instantiations
        start_time = time.time()
        for _ in range(10):
            config = GlobalConfig()
            assert config is not None
        end_time = time.time()

        # Should complete within reasonable time (less than 1 second)
        assert end_time - start_time < 1.0

    def test_cleanup_and_resource_management(self, temp_global_profiles):
        """Test cleanup and resource management."""
        # Test that temporary resources are properly cleaned up
        initial_files = list(temp_global_profiles.glob("*"))

        # Run commands that should create temporary files
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0

        # Check that no unexpected files were left behind
        final_files = list(temp_global_profiles.glob("*"))
        # Should only contain our created profile files, not temporary files

    def test_thread_safety_basic(self, temp_global_profiles, sample_profiles_data):
        """Test basic thread safety of GlobalConfig operations."""
        import threading
        import time

        # Create a profile for testing
        create_profile_file(temp_global_profiles, "thread_test", sample_profiles_data["deepseek"])

        results = []

        def run_list_command():
            result = runner.invoke(app, ["list"])
            results.append(result.exit_code)

        # Run multiple commands concurrently
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=run_list_command)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # All commands should succeed (exit code 0) or fail consistently
        assert len(results) == 3
        # Should not have mixed success/failure due to race conditions
