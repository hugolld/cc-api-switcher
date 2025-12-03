# CC API Switcher

A powerful CLI tool for switching between API provider settings for Claude Code. Manage multiple provider configurations (DeepSeek, GLM, MiniMax, Qwen) with global access, automatic backups, and validation.

## Features

- ✅ **Global Tool**: Install once, use from any directory
- 📋 **List Profiles**: View all available profiles with source indicators
- 🔍 **Show Current**: Display current active profile
- ✔️ **Validation**: Validate profiles before switching
- 💾 **Automatic Backups**: Automatic backup before switching
- 🔄 **Restore Backups**: Restore from previous backups
- 📊 **Compare Profiles**: Diff two profiles
- ✏️ **Edit Profiles**: Edit profiles with your default editor
- 📤 **Import/Export**: Import profiles from JSON files
- 🌍 **Migration Tools**: Migrate local profiles to global configuration
- 🔒 **Secure**: API tokens are masked in output
- 🎨 **Beautiful Output**: Rich formatting with colors and tables
- ⚙️ **Global Configuration**: Hierarchical profile discovery with environment variable support

## Platform Compatibility

**macOS Only** - This tool is currently developed, tested, and supported exclusively on macOS.

- ✅ **Fully Supported**: macOS (Monterey 12.0 and later)
- ❌ **Not Supported**: Windows, Linux, or other operating systems
- 🔄 **Future Plans**: Cross-platform support may be considered in future releases

The tool is designed to work with Claude Code, which is primarily available on macOS. All documentation and troubleshooting guidance assumes a macOS environment.

## Installation

### Prerequisites for macOS

Before installing, ensure you have:

- **macOS 12.0 (Monterey)** or later
- **Python 3.8+** installed (comes with macOS by default)
- **uv** package manager - install with:
  ```bash
  # Using Homebrew (recommended)
  brew install uv

  # Or install directly
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **Terminal access** with shell (zsh or bash)

**Note**: This tool is designed for macOS systems with Claude Code installed. Ensure you have Claude Code properly set up before using this switcher.

### Using uv (Recommended)

```bash
# Install globally as a tool (recommended)
uv tool install .

# Build and install from wheel
uv build
uv tool install dist/*.whl
```

### Using pip

```bash
pip install cc-api-switcher
```

### First Time Setup

After installation, initialize global configuration:

```bash
cas init
```

If you have existing profile files, migrate them to global configuration:

```bash
cas migrate --force
```

### Migration from Previous Versions

**⚠️ BREAKING CHANGE**: The command has been renamed from `cc-api-switch` to `cas` for convenience.

If you were using the previous `cc-api-switch` command:
- The new command is `cas` (shorter and easier to type)
- All functionality and arguments remain identical
- Update any scripts or automation to use `cas` instead of `cc-api-switch`
- The old `cc-api-switch` command is no longer available after updating

```bash
# Old command (no longer available)
cc-api-switch list

# New command (use this instead)
cas list
```

## Usage

### Basic Commands

#### List all available profiles
```bash
cas list
```

#### Switch to a profile
```bash
cas switch deepseek
cas switch glm
cas switch minimax
cas switch qwen
```

#### Show current profile
```bash
cas show
```

#### Validate a profile
```bash
cas validate deepseek
```

#### Create manual backup
```bash
cas backup
```

#### List available backups
```bash
cas restore --list
```

#### Restore from backup
```bash
cas restore settings.json.backup.20251103_143022
```

#### Compare two profiles
```bash
cas diff deepseek glm
```

#### Import a profile from file
```bash
cas import ~/Downloads/my-profile.json --name custom
```

#### Edit a profile
```bash
cas edit deepseek
```

### Advanced Usage

#### Specify custom directories
```bash
# List profiles from a specific directory
cas list --dir ~/my-profiles

# Switch using profiles from a specific directory
cas switch deepseek --dir ~/my-profiles

# Import into a specific directory
cas import profile.json --name new --dir ~/my-profiles
```

#### Specify custom target path
```bash
# Switch to a different settings file location
cas switch deepseek --target ~/.config/claude/settings.json
```

#### Disable automatic backup
```bash
cas switch deepseek --no-backup
```

#### Verbose output
```bash
cas switch deepseek --verbose
```

### Global Configuration

#### Initialize global configuration
```bash
cas init
```

#### Show profile directory search order
```bash
cas profile-dir
```

#### Manage configuration settings
```bash
# Show all configuration
cas config show

# Get specific setting
cas config get default_profile_dir

# Set configuration value
cas config set auto_backup false
```

#### Migrate existing profiles to global configuration
```bash
# Preview migration (dry run)
cas migrate --dry-run

# Perform migration
cas migrate

# Migrate and clean up local files
cas migrate --cleanup
```

#### Environment Variables
```bash
# Override profile directory
export CC_API_SWITCHER_PROFILE_DIR="~/my-profiles"
cas list

# Use custom config directory
export XDG_CONFIG_HOME="~/.my-config"
cas init
```

## Profile Files

Profile files are JSON files containing your API provider settings. They should follow this structure:

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
    "ANTHROPIC_AUTH_TOKEN": "sk-your-token-here",
    "API_TIMEOUT_MS": "600000",
    "ANTHROPIC_MODEL": "deepseek-chat",
    "ANTHROPIC_SMALL_FAST_MODEL": "deepseek-chat",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "deepseek-chat",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "deepseek-chat",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "deepseek-chat"
  },
  "statusLine": {
    "type": "command",
    "command": "/Users/username/.claude/dracula-statusline.sh",
    "padding": 0
  },
  "enabledPlugins": {
    "uni-secretary-tools@hugolld-CC-plugins": true
  },
  "alwaysThinkingEnabled": false
}
```

### Example Profiles

#### DeepSeek
```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
    "ANTHROPIC_AUTH_TOKEN": "sk-deepseek-example-placeholder",
    "API_TIMEOUT_MS": "600000",
    "ANTHROPIC_MODEL": "deepseek-chat"
  }
}
```

#### GLM
```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://open.bigmodel.cn/api/anthropic",
    "ANTHROPIC_AUTH_TOKEN": "sk-glm-example-placeholder",
    "API_TIMEOUT_MS": "3000000",
    "ANTHROPIC_MODEL": "glm-4.6"
  }
}
```

#### MiniMax
```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.minimaxi.com/anthropic",
    "ANTHROPIC_AUTH_TOKEN": "sk-minimax-example-placeholder",
    "API_TIMEOUT_MS": "3000000",
    "ANTHROPIC_MODEL": "MiniMax-M2"
  }
}
```

#### Qwen
```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://dashscope.aliyuncs.com/api/v2/apps/claude-code-proxy",
    "ANTHROPIC_AUTH_TOKEN": "sk-qwen-example-placeholder",
    "API_TIMEOUT_MS": "3000000",
    "ANTHROPIC_MODEL": "qwen-max"
  }
}
```

**⚠️ IMPORTANT**: Replace the example placeholder tokens above with your actual API keys from:
- **DeepSeek**: https://platform.deepseek.com/
- **GLM**: https://open.bigmodel.cn/
- **MiniMax**: https://api.minimaxi.com/
- **Qwen**: https://dashscope.aliyun.com/
- **Kimi**: https://platform.moonshot.cn/

## Project Structure

```
cc-api-switcher/
├── pyproject.toml              # Project configuration
├── README.md                   # This file
├── src/
│   └── settings_switcher/
│       ├── __init__.py         # Package info
│       ├── cli.py              # Command-line interface
│       ├── config.py           # Profile models and validation
│       ├── core.py             # Core switching logic
│       └── exceptions.py       # Custom exceptions
├── tests/
│   ├── __init__.py
│   ├── test_config.py          # Config tests
│   ├── test_core.py            # Core tests
│   └── test_cli.py             # CLI tests
```

## Development

### Setup

```bash
# Clone and setup
git clone <repo>
cd cc-api-switcher

# Install dependencies
uv sync --dev

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src

# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Type checking
uv run mypy src
```

### Adding New Providers

To add support for a new provider:

1. Add a new profile file following the JSON structure above
2. The provider will be automatically detected from the `ANTHROPIC_BASE_URL`
3. Update the `provider` property in `SettingsProfile` class if needed

## Security Notes

- ⚠️ **API tokens are sensitive**: Keep your profile files secure
- 🔒 **File permissions**: The tool automatically sets settings file permissions to 0o600 (owner read/write only)
- 🔍 **Token masking**: API tokens are masked in all output (showing only first/last 4 characters)
- 💾 **Backups**: Automatic backups protect against configuration loss
- 🚫 **Path traversal**: Input paths are validated to prevent directory traversal attacks

## Troubleshooting

### Platform-Specific Issues

#### Tool Not Found on macOS
```bash
zsh: command not found: cas
```
**Solution**:
1. Ensure uv is installed: `brew install uv`
2. Check installation: `uv tool list`
3. Verify PATH includes uv's bin directory: `echo $PATH`
4. Add uv bin to PATH if needed: `export PATH="$HOME/.cargo/bin:$PATH"`

#### Permission Issues on macOS
```
Error: Permission denied when accessing ~/.claude/settings.json
```
**Solution**:
1. Check file permissions: `ls -la ~/.claude/settings.json`
2. Fix permissions: `chmod 600 ~/.claude/settings.json`
3. Ensure ownership: `chown $USER ~/.claude/settings.json`

#### Shell Compatibility (zsh/bash)
```bash
# For zsh (default on modern macOS)
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# For bash
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bash_profile
source ~/.bash_profile
```

### Common Issues

#### Profile not found
```
Error: Profile 'deepseek' not found
```
**Solution**: Use `cas list` to see available profiles, or use `--dir` to specify the profile directory.

#### Validation failed
```
Profile validation failed:
  - Missing ANTHROPIC_BASE_URL in env
```
**Solution**: Ensure your profile JSON has all required fields: `ANTHROPIC_BASE_URL` and `ANTHROPIC_AUTH_TOKEN` in the `env` section.

#### Backup fails
```
Error: Failed to create backup
```
**Solution**: Check that you have write permissions to the backup directory (`~/.config/cc-api-switcher/backups/`).

### Claude Code Integration Issues

#### Settings file location
- **Default**: `~/.claude/settings.json` on macOS
- **Custom**: Use `--target` flag for different locations
- **Verification**: Check if Claude Code can read the settings file

#### macOS Path Issues
If experiencing path-related issues:
1. Use absolute paths: `cas switch deepseek --target ~/Documents/custom-settings.json`
2. Check Home Directory: `echo $HOME`
3. Verify Claude Code installation: `which claude`

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.
