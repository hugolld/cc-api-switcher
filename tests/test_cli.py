"""Tests for CLI commands."""

import json
from unittest.mock import patch

from typer.testing import CliRunner

from cc_api_switcher.cli import app

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
