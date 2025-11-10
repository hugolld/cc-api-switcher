<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**CC API Switcher** is a Python CLI tool for switching between API provider settings for Claude Code. It manages multiple provider configurations (DeepSeek, GLM, MiniMax, Qwen, Kimi) with automatic backups, validation, secure file handling, global configuration management, and profile migration utilities.

## Development Commands

### Environment Setup
```bash
# Install dependencies in development mode
uv sync --group dev

# Install as a global tool (recommended)
uv tool install .

# Build package
uv build

# Reinstall after changes
uv sync --reinstall
```

### Testing
```bash
# Run all tests
PYTHONPATH=/Users/hugodong/Documents/Claude/cc-api-switcher/src uv run pytest

# Run tests with coverage
PYTHONPATH=/Users/hugodong/Documents/Claude/cc-api-switcher/src uv run pytest --cov=src

# Run specific test file
PYTHONPATH=/Users/hugodong/Documents/Claude/cc-api-switcher/src uv run pytest tests/test_cli.py

# Run single test
PYTHONPATH=/Users/hugodong/Documents/Claude/cc-api-switcher/src uv run pytest tests/test_cli.py::TestCLI::test_switch_profile

# Run tests with verbose output
PYTHONPATH=/Users/hugodong/Documents/Claude/cc-api-switcher/src uv run pytest -v

# Run tests matching a pattern
PYTHONPATH=/Users/hugodong/Documents/Claude/cc-api-switcher/src uv run pytest -k "test_switch"
```

### Code Quality
```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Type checking
uv run mypy src
```

### CLI Testing
```bash
# Test CLI with new module structure
PYTHONPATH=/Users/hugodong/Documents/Claude/cc-api-switcher/src uv run python -m cc_api_switcher.cli list

# Test installed command
uv run cc-api-switch list

# Test global configuration initialization
cc-api-switch init

# Test migration utilities
cc-api-switch migrate --dry-run
```

## Architecture

### Module Structure
```
src/cc_api_switcher/
├── __init__.py         # Package version info
├── cli.py              # Typer-based CLI commands (13 commands across 2 groups)
├── config.py           # Profile models and validation
├── core.py             # Core switching logic
├── exceptions.py       # Custom exceptions
├── global_config.py    # Global configuration management (NEW)
└── migration.py        # Profile migration utilities (NEW)
```

### Core Classes and Components

**`CcApiSwitcher` (core.py:17-198)**
- Main switching logic with atomic file operations
- Backup management: automatic backup creation, retention (last 10), cleanup
- Target path management: defaults to `~/.claude/settings.json`
- Security: sets 0o600 permissions on settings files
- Atomic switching: uses `temp_file + os.replace()` pattern

**`SettingsProfile` (config.py:12-93)**
- Pydantic model for profile validation
- Provider auto-detection from ANTHROPIC_BASE_URL patterns
- Required field validation: ANTHROPIC_BASE_URL, ANTHROPIC_AUTH_TOKEN
- API token masking algorithm (config.py:155-171)

**`GlobalConfig` (global_config.py:25-249)**
- XDG Base Directory specification compliance
- Hierarchical profile discovery with 4 levels: CLI arg → env var → global config → local
- Environment variable support (`CC_API_SWITCHER_PROFILE_DIR`, `XDG_CONFIG_HOME`)
- Configuration persistence in `~/.config/cc-api-switcher/config.json`
- Default target path and backup retention configuration

**`ProfileMigration` (migration.py:20-273)**
- Profile discovery from common locations (current dir, home, profiles dir)
- Safe migration with force/dry-run options and validation
- Local cleanup utilities with user confirmation
- Rich progress reporting and detailed status information

**Custom Exception Hierarchy (exceptions.py:4-32)**
- Base: `CcApiSwitcherError`
- Derived: `ProfileNotFoundError`, `InvalidProfileError`, `BackupError`, `ValidationError`

**CLI Architecture (cli.py:15-600+)**
- Entry point: `cc_api_switcher.cli:app`
- Rich-powered terminal output with tables and colors
- **Commands group** (9 commands): list, switch, show, validate, backup, restore, diff, import, edit
- **Configuration group** (4 commands): init, config, profile-dir, migrate
- Uses CliRunner for testing

### Provider Detection System

Auto-detects providers from URL patterns in `SettingsProfile.provider` property:
- DeepSeek: `api.deepseek.com`
- GLM: `open.bigmodel.cn`
- MiniMax: `api.minimaxi.com`
- Qwen: `dashscope.aliyuncs.com`
- Kimi: `api.kimi.com`

### Global Configuration System

**Profile Discovery Priority:**
1. Command line `--dir` parameter
2. `CC_API_SWITCHER_PROFILE_DIR` environment variable
3. `~/.config/cc-api-switcher/profiles/` (global directory)
4. Current working directory (backwards compatibility)

**Configuration File Structure** (`~/.config/cc-api-switcher/config.json`):
```json
{
  "default_profile_dir": "~/.config/cc-api-switcher/profiles",
  "default_target_path": "~/.claude/settings.json",
  "backup_retention_count": 10,
  "auto_backup": true
}
```

**Environment Variables:**
- `CC_API_SWITCHER_PROFILE_DIR`: Override profile directory
- `XDG_CONFIG_HOME`: Override config directory location

### Backup and Atomic Operations Pattern

**Atomic Switching Process:**
1. Validate profile before switching
2. Create backup (if enabled) using `temp_file + os.replace()`
3. Write new settings to temporary file
4. Atomic move to target path
5. Set secure permissions (0o600)

**Backup System:**
- Location: `~/.config/cc-api-switcher/backups/`
- Format: `{target_filename}.backup.{timestamp}`
- Retention: Configurable count (default 10), auto-cleanup of older backups

### Profile Migration System

**Migration Process:**
1. **Discovery**: Search common locations for existing profile files
2. **Validation**: Verify profile integrity and required fields
3. **Migration**: Copy profiles to global configuration directory
4. **Cleanup**: Optionally remove original local files

**Migration Sources:**
- Current working directory
- User home directory
- Custom profile directories
- Existing `~/.config/cc-api-switcher/profiles/` (detect existing setup)

**Migration Commands:**
- `cc-api-switch migrate --dry-run`: Preview migration without changes
- `cc-api-switch migrate`: Perform migration with confirmation
- `cc-api-switch migrate --force`: Skip confirmation prompts
- `cc-api-switch migrate --cleanup`: Remove original files after migration

### Profile File Structure

Profile files follow this JSON format (stored as `{name}_settings.json`):
```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
    "ANTHROPIC_AUTH_TOKEN": "sk-your-token",
    "API_TIMEOUT_MS": "600000",
    "ANTHROPIC_MODEL": "deepseek-chat",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": 1
  },
  "statusLine": {
    "type": "command",
    "command": "/path/to/statusline.sh",
    "padding": 0
  },
  "enabledPlugins": {
    "plugin-name": true
  },
  "alwaysThinkingEnabled": false
}
```

## Configuration Details

**pyproject.toml Key Settings:**
- Entry point: `cc-api-switch = "cc_api_switcher.cli:app"`
- Package: `packages = ["src/cc_api_switcher"]`
- Line length: 88 characters (ruff)
- Python: >=3.8, tested on 3.12
- Uses modern `dependency-groups` for dev dependencies
- pytest: Coverage reports with HTML output

**Testing Architecture:**
- 91 total tests across 5 test files
- CLI tests: Typer CliRunner for command testing
- Config tests: Profile validation, token masking
- Core tests: Atomic operations, backup/restore
- Global config tests: Configuration management, migration testing

**Development Dependencies:**
- Testing: pytest>=8.3.5, pytest-cov>=5.0.0, pytest-mock>=3.14.1
- Code quality: ruff>=0.14.3, mypy>=1.14.1
- Uses `dependency-groups` (uv v2 style) instead of `optional-dependencies`

## Key Implementation Patterns

**Security Patterns:**
- Token masking: Shows only first 4 + last 4 characters
- File permissions: 0o600 on all settings files
- Path validation: Prevents directory traversal attacks
- Secure temporary file handling

**Error Handling:**
- Custom exception hierarchy with specific error types
- Rich-formatted error messages with actionable guidance
- Graceful degradation for missing optional configuration

**Atomic Operations:**
- All file writes use temp file + os.replace() pattern
- Prevents corruption during switching operations
- Automatic backup before any changes

**Global Configuration System:**
- Hierarchical profile discovery with fallbacks
- Environment variable support for customization
- XDG config directory compliance
- Migration tools for transitioning from local to global config
- Persistent configuration with validation

**Migration Safety Patterns:**
- Dry-run mode for previewing changes
- User confirmation for destructive operations
- Profile validation before and after migration
- Progress reporting with rich output
- Rollback capabilities for failed operations

## Development Workflow

### Making Changes
1. Always run tests before committing: `PYTHONPATH=src .venv/bin/pytest` (or `PYTHONPATH=/Users/hugodong/Documents/Claude/cc-api-switcher/src uv run pytest`)
2. Address test failures: Currently 12 failed, 79 passed (61% coverage)
3. Format and lint code: `uv run ruff format . && uv run ruff check .`
4. Run type checking: `uv run mypy src`
5. Test CLI manually: `PYTHONPATH=/Users/hugodong/Documents/Claude/cc-api-switcher/src uv run python -m cc_api_switcher.cli list`
6. Test global configuration: `cc-api-switch init && cc-api-switch profile-dir`
7. Verify global workflow: Test commands without `--dir` flag to ensure no crashes

### Testing Patterns
- **CLI Tests**: Use `typer.testing.CliRunner` for command testing
- **Mocking**: Use `pytest-mock` for mocking file operations and user input
- **Temporary Files**: Tests use temporary directories for file operations
- **Isolated Tests**: Each test should be independent and not rely on external state
- **Migration Tests**: Test with temporary profile directories and cleanup
- **Global Config Tests**: Test XDG directory compliance and environment variables

### Common Test Patterns
```python
# Mocking file operations
with patch('cc_api_switcher.core.Path') as mock_path:
    mock_path.return_value.exists.return_value = True
    # test code here

# Testing CLI commands
from typer.testing import CliRunner
from cc_api_switcher.cli import app

runner = CliRunner()
result = runner.invoke(app, ['list'])
assert result.exit_code == 0

# Testing global configuration
from cc_api_switcher.global_config import GlobalConfig
import tempfile
import os

with tempfile.TemporaryDirectory() as temp_dir:
    os.environ['XDG_CONFIG_HOME'] = temp_dir
    config = GlobalConfig()
    # test global config features here

# Testing global workflow (CRITICAL - no --dir flag)
from cc_api_switcher.global_config import GlobalConfig
from cc_api_switcher.config import ProfileStore
import tempfile
import os

with tempfile.TemporaryDirectory() as temp_dir:
    os.environ['XDG_CONFIG_HOME'] = temp_dir
    os.environ['CC_API_SWITCHER_PROFILE_DIR'] = temp_dir

    # Test global mode without --dir (this is where bugs exist)
    runner = CliRunner()
    result = runner.invoke(app, ['list'])  # No --dir flag
    assert result.exit_code == 0

    # Test import/edit commands in global mode (currently crash)
    result = runner.invoke(app, ['import', 'test_profile'])
    # Should not crash with AttributeError on profiles_dir
```

## Working with This Codebase

**When Adding New Providers:**
1. Create `{provider}_settings.json` with base URL and auth token
2. Provider auto-detection works from URL patterns
3. Update `SettingsProfile.provider` property if new pattern needed
4. Test with global configuration system

**When Testing CLI Changes:**
- Use `PYTHONPATH=/path/to/src uv run python -m cc_api_switcher.cli` for testing
- Install with `uv sync --reinstall` after structural changes
- Test both module execution and installed command
- Test with global configuration initialized: `cc-api-switch init`

**When Modifying Core Logic:**
- Follow atomic operations pattern for file writes
- Maintain backup compatibility (keep 10 most recent)
- Ensure token masking works for new token formats
- Update corresponding tests for coverage
- Consider global configuration impact

**When Working with Global Config:**
- Understand the hierarchical discovery order
- Test with and without environment variables
- Ensure migration utilities work correctly
- Respect XDG config directory specifications
- Test configuration persistence and validation

**When Working with Migration:**
- Always test with dry-run mode first
- Use temporary directories for profile testing
- Test with various profile locations and formats
- Validate profiles before and after migration
- Test cleanup operations thoroughly
- Ensure user confirmation works correctly

**OpenSpec Integration:**
- Use `/openspec:proposal` for significant changes
- Follow change proposal process for breaking changes
- Archive completed changes with `/openspec:archive`

## Troubleshooting

### Common Issues

**Module Not Found Error**
```bash
# ❌ Wrong: uv run pytest
# ✅ Correct: PYTHONPATH=/Users/hugodong/Documents/Claude/cc-api-switcher/src uv run pytest
```

**Installation Issues**
```bash
# ❌ Wrong: uv tool install . --name cc-api-switch
# ✅ Correct: uv tool install .
```

**CLI Command Not Found**
```bash
# After installation, the command should be available as:
cc-api-switch list

# If not found, check if uv's bin directory is in PATH
# or use the module directly:
PYTHONPATH=/Users/hugodong/Documents/Claude/cc-api-switcher/src uv run python -m cc_api_switcher.cli list
```

**Global Configuration Issues**
- Configuration directory: `~/.config/cc-api-switcher/`
- Profile directory: `~/.config/cc-api-switcher/profiles/`
- Use `cc-api-switch profile-dir` to check discovery order
- Use `cc-api-switch config show` to view current configuration
- Initialize with `cc-api-switch init` if missing

**Migration Issues**
- Always test with `--dry-run` first
- Check file permissions before migration
- Use `cc-api-switch migrate --force` to skip confirmations
- Profiles are validated before and after migration
- Original files are preserved unless `--cleanup` is used

**Permission Errors**
- Settings files are created with 0o600 permissions (owner read/write only)
- Ensure you have write permissions to `~/.claude/` directory
- Backup directory `~/.config/cc-api-switcher/backups/` is created automatically
- Global config directory `~/.config/cc-api-switcher/` requires write permissions

### Debug Mode
```bash
# Run with debug output
PYTHONPATH=/Users/hugodong/Documents/Claude/cc-api-switcher/src uv run python -m cc_api_switcher.cli --debug list

# Check profile discovery order
cc-api-switch profile-dir

# Show global configuration
cc-api-switch config show
```

## Important Development Notes

### Correct Installation Command
The correct installation command is:
```bash
uv tool install .  # ✅ Correct - uses name from pyproject.toml
```
NOT:
```bash
uv tool install . --name cc-api-switch  # ❌ Incorrect -- --name flag doesn't exist
```

### Testing Requirements
Always use the full PYTHONPATH when running tests to ensure the module is found:
```bash
PYTHONPATH=/Users/hugodong/Documents/Claude/cc-api-switcher/src uv run pytest
```

### Module Import Path
The package name is `cc_api_switcher` (with underscores), not `cc-api-switcher`. When importing or running as module:
```bash
python -m cc_api_switcher.cli
```

### Global vs Local Configuration
The tool supports both legacy local configuration and modern global configuration:
- Legacy: Profile files in current working directory
- Modern: Global profiles in `~/.config/cc-api-switcher/profiles/` with hierarchical discovery
- Migration utilities available to transition from local to global
- Environment variables can override default locations
- XDG Base Directory specification compliance

## Current Known Issues

### Critical Bugs (CODE_REVIEW.md Verified)
1. **CLI Import/Edit Commands Crash in Global Mode** - Commands crash when `--dir` is not specified due to null pointer dereference on `store.profiles_dir`
2. **Backup/Restore Commands Ignore Configured Default Target** - Don't respect configured default target paths from global config
3. **Hard-coded Backup Retention** - Ignores `backup_retention_count` from GlobalConfig, always uses 10

### Testing Gaps
- CLI tests only use `--dir` flag, leaving global workflow (default mode) untested
- Missing tests for import/edit commands in global mode
- Missing integration tests between GlobalConfig and CLI commands

### Current Test Status
- **Suite Result**: 12 failed, 79 passed (61% coverage)
- **Test Command**: `PYTHONPATH=src .venv/bin/pytest` (PYTHONPATH required for module imports)
- **Total Tests**: 91 tests across 5 test files
- **Failure Rate**: 13.2% (12 failures indicate active bugs, particularly in global workflow)

### Development Priorities
1. **Fix failing tests** - Address 12 test failures (13.2% failure rate) to restore test suite health
2. Fix critical bugs that crash import/edit commands in global mode
3. Make backup/restore commands respect user configuration
4. Add comprehensive test coverage for global workflow scenarios
5. Consider CLI architecture modularization (cli.py is 943 lines)