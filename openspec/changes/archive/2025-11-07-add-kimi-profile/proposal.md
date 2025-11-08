# Change: Add Kimi API Provider Profile

## Why
Enable users to switch to Kimi (Moonshot AI) as an additional API provider option for Claude Code, expanding the available provider choices beyond the current four providers (DeepSeek, GLM, MiniMax, Qwen).

## What Changes
- Add a new `kimi_settings.json` profile configuration file following the established pattern
- Update provider auto-detection logic to recognize Kimi's base URL pattern (`api.kimi.com`)
- Ensure the profile includes all standard configuration fields (timeout, plugins, status line, etc.)

## Impact
- **Affected specs**: Profile Management, Provider Detection
- **Affected code**: `src/settings_switcher/config.py` (provider detection), new profile file
- **User impact**: New `kimi` profile available via `cc-api-switch switch kimi`