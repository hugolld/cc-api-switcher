"""Tests for configuration and validation."""

import json

import pytest

from cc_api_switcher.config import ProfileStore, SettingsProfile, mask_token
from cc_api_switcher.exceptions import ProfileNotFoundError


class TestSettingsProfile:
    """Test SettingsProfile model."""

    def test_from_dict_valid(self):
        """Test creating profile from dictionary."""
        data = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://api.example.com",
                "ANTHROPIC_AUTH_TOKEN": "test-token",
            }
        }
        profile = SettingsProfile.from_dict(data, name="test")
        assert profile.name == "test"
        assert profile.env["ANTHROPIC_BASE_URL"] == "https://api.example.com"
        assert profile.env["ANTHROPIC_AUTH_TOKEN"] == "test-token"

    def test_from_file(self, tmp_path):
        """Test loading profile from JSON file."""
        data = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://api.example.com",
                "ANTHROPIC_AUTH_TOKEN": "test-token",
            }
        }
        file_path = tmp_path / "test_profile.json"
        with open(file_path, "w") as f:
            json.dump(data, f)

        profile = SettingsProfile.from_file(file_path, name="test")
        assert profile.name == "test"
        assert profile.env["ANTHROPIC_BASE_URL"] == "https://api.example.com"

    def test_provider_detection_deepseek(self):
        """Test provider detection for DeepSeek."""
        data = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
            }
        }
        profile = SettingsProfile.from_dict(data, name="deepseek")
        assert profile.provider == "DeepSeek"

    def test_provider_detection_glm(self):
        """Test provider detection for GLM."""
        data = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://open.bigmodel.cn/api/anthropic",
            }
        }
        profile = SettingsProfile.from_dict(data, name="glm")
        assert profile.provider == "GLM"

    def test_provider_detection_minimax(self):
        """Test provider detection for MiniMax."""
        data = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://api.minimaxi.com/anthropic",
            }
        }
        profile = SettingsProfile.from_dict(data, name="minimax")
        assert profile.provider == "MiniMax"

    def test_provider_detection_qwen(self):
        """Test provider detection for Qwen."""
        data = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://dashscope.aliyuncs.com/api/v2/apps/claude-code-proxy",
            }
        }
        profile = SettingsProfile.from_dict(data, name="qwen")
        assert profile.provider == "Qwen"

    def test_validate_missing_base_url(self):
        """Test validation catches missing base URL."""
        data = {
            "env": {
                "ANTHROPIC_AUTH_TOKEN": "test-token",
            }
        }
        profile = SettingsProfile.from_dict(data, name="test")
        issues = profile.validate_profile()
        assert "ANTHROPIC_BASE_URL" in "".join(issues)

    def test_validate_missing_auth_token(self):
        """Test validation catches missing auth token."""
        data = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://api.example.com",
            }
        }
        profile = SettingsProfile.from_dict(data, name="test")
        issues = profile.validate_profile()
        assert "ANTHROPIC_AUTH_TOKEN" in "".join(issues)

    def test_validate_invalid_base_url(self):
        """Test validation catches invalid base URL."""
        data = {
            "env": {
                "ANTHROPIC_BASE_URL": "not-a-url",
                "ANTHROPIC_AUTH_TOKEN": "test-token",
            }
        }
        profile = SettingsProfile.from_dict(data, name="test")
        issues = profile.validate_profile()
        assert any("Invalid ANTHROPIC_BASE_URL format" in issue for issue in issues)

    def test_mask_token(self):
        """Test token masking."""
        long_token = "12345678901234567890"
        masked = mask_token(long_token)
        assert masked[:4] == "1234"
        assert masked[-4:] == "7890"
        assert len(masked) == len(long_token)  # Preserve original length
        assert "********" in masked  # 8 asterisks in the middle

    def test_mask_short_token(self):
        """Test masking short tokens."""
        short_token = "123"
        masked = mask_token(short_token)
        assert masked == "***"

    def test_mask_empty_token(self):
        """Test masking empty token."""
        masked = mask_token("")
        assert masked == ""


class TestProfileStore:
    """Test ProfileStore."""

    def test_list_profiles_empty(self, tmp_path):
        """Test listing empty profile store."""
        store = ProfileStore(tmp_path)
        profiles = store.list_profiles()
        assert profiles == []

    def test_list_profiles(self, tmp_path):
        """Test listing profiles."""
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

        file1 = tmp_path / "profile1_settings.json"
        file2 = tmp_path / "profile2_settings.json"

        with open(file1, "w") as f:
            json.dump(data1, f)
        with open(file2, "w") as f:
            json.dump(data2, f)

        store = ProfileStore(tmp_path)
        profiles = store.list_profiles()

        assert len(profiles) == 2
        assert any(p.name == "profile1" for p in profiles)
        assert any(p.name == "profile2" for p in profiles)

    def test_get_profile(self, tmp_path):
        """Test getting a specific profile."""
        data = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://api.example.com",
                "ANTHROPIC_AUTH_TOKEN": "test-token",
            }
        }
        file_path = tmp_path / "test_settings.json"
        with open(file_path, "w") as f:
            json.dump(data, f)

        store = ProfileStore(tmp_path)
        profile = store.get_profile("test")

        assert profile.name == "test"
        assert profile.env["ANTHROPIC_AUTH_TOKEN"] == "test-token"

    def test_get_profile_not_found(self, tmp_path):
        """Test getting non-existent profile."""
        store = ProfileStore(tmp_path)

        with pytest.raises(ProfileNotFoundError):  # Should raise specific exception
            store.get_profile("nonexistent")

    def test_save_profile(self, tmp_path):
        """Test saving a profile."""
        data = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://api.example.com",
                "ANTHROPIC_AUTH_TOKEN": "test-token",
            }
        }
        profile = SettingsProfile.from_dict(data, name="newprofile")

        store = ProfileStore(tmp_path)
        store.save_profile(profile)

        saved_file = tmp_path / "newprofile_settings.json"
        assert saved_file.exists()

        with open(saved_file) as f:
            saved_data = json.load(f)

        assert saved_data["env"]["ANTHROPIC_AUTH_TOKEN"] == "test-token"
