# Change: Rename Project from settings-switcher to cc-api-switcher

## Why
Align the project naming with its actual identity and purpose. The project is already known as "cc-api-switcher" (CC API Switcher) but the internal code structure still uses the legacy "settings-switcher" naming, creating confusion and inconsistency between the public name and internal implementation.

## What Changes
- **BREAKING**: Rename module directory from `src/settings_switcher/` to `src/cc_api_switcher/`
- Update all class names: `SettingsSwitcher` → `CcApiSwitcher`, `SettingsSwitcherError` → `CcApiSwitcherError`
- Update all import statements across the codebase and tests
- Update package configuration in `pyproject.toml` (module references, entry points)
- Update documentation strings and comments to reflect new naming
- Maintain backward compatibility by keeping the CLI command name `cc-api-switch` unchanged

## Impact
- **Affected specs**: Package Structure, Internal API, Import Paths
- **Affected code**: All source files, tests, configuration files, documentation
- **User impact**: CLI command remains unchanged, but internal module structure changes
- **Breaking changes**: Import paths for any external consumers will change