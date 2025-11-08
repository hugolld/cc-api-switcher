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
cc-api-switch init
```

If you have existing profile files, migrate them to global configuration:

```bash
cc-api-switch migrate --force
```

## Usage

### Basic Commands

#### List all available profiles
```bash
cc-api-switch list
```

#### Switch to a profile
```bash
cc-api-switch switch deepseek
cc-api-switch switch glm
cc-api-switch switch minimax
cc-api-switch switch qwen
```

#### Show current profile
```bash
cc-api-switch show
```

#### Validate a profile
```bash
cc-api-switch validate deepseek
```

#### Create manual backup
```bash
cc-api-switch backup
```

#### List available backups
```bash
cc-api-switch restore --list
```

#### Restore from backup
```bash
cc-api-switch restore settings.json.backup.20251103_143022
```

#### Compare two profiles
```bash
cc-api-switch diff deepseek glm
```

#### Import a profile from file
```bash
cc-api-switch import ~/Downloads/my-profile.json --name custom
```

#### Edit a profile
```bash
cc-api-switch edit deepseek
```

### Advanced Usage

#### Specify custom directories
```bash
# List profiles from a specific directory
cc-api-switch list --dir ~/my-profiles

# Switch using profiles from a specific directory
cc-api-switch switch deepseek --dir ~/my-profiles

# Import into a specific directory
cc-api-switch import profile.json --name new --dir ~/my-profiles
```

#### Specify custom target path
```bash
# Switch to a different settings file location
cc-api-switch switch deepseek --target ~/.config/claude/settings.json
```

#### Disable automatic backup
```bash
cc-api-switch switch deepseek --no-backup
```

#### Verbose output
```bash
cc-api-switch switch deepseek --verbose
```

### Global Configuration

#### Initialize global configuration
```bash
cc-api-switch init
```

#### Show profile directory search order
```bash
cc-api-switch profile-dir
```

#### Manage configuration settings
```bash
# Show all configuration
cc-api-switch config show

# Get specific setting
cc-api-switch config get default_profile_dir

# Set configuration value
cc-api-switch config set auto_backup false
```

#### Migrate existing profiles to global configuration
```bash
# Preview migration (dry run)
cc-api-switch migrate --dry-run

# Perform migration
cc-api-switch migrate

# Migrate and clean up local files
cc-api-switch migrate --cleanup
```

#### Environment Variables
```bash
# Override profile directory
export CC_API_SWITCHER_PROFILE_DIR="~/my-profiles"
cc-api-switch list

# Use custom config directory
export XDG_CONFIG_HOME="~/.my-config"
cc-api-switch init
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
zsh: command not found: cc-api-switch
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
**Solution**: Use `cc-api-switch list` to see available profiles, or use `--dir` to specify the profile directory.

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
1. Use absolute paths: `cc-api-switch switch deepseek --target ~/Documents/custom-settings.json`
2. Check Home Directory: `echo $HOME`
3. Verify Claude Code installation: `which claude`

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.
