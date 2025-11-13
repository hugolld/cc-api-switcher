# integrate-backup-global-config Proposal

## Summary
Fix critical issues where backup/restore commands ignore user-configured defaults and CcApiSwitcher hard-codes backup settings. This change ensures backup/restore commands honor GlobalConfig settings for default target paths, auto-backup toggles, and retention counts.

## Problem Statement

### Critical Issue 2: Backup/Restore Commands Ignore Configured Default Target
- **Location**: `src/cc_api_switcher/cli.py:322` and `src/cc_api_switcher/cli.py:371`
- **Issue**: Backup and restore commands instantiate `CcApiSwitcher` without `GlobalConfig`, ignoring user-configured default target paths
- **Impact**: Backups are taken from `~/.claude/settings.json` even when users configure different targets

### Critical Issue 3: Hard-coded Backup Retention
- **Location**: `src/cc_api_switcher/core.py:82-115`
- **Issue**: `CcApiSwitcher` hard-codes retention to 10 backups and ignores `auto_backup` settings
- **Impact**: User configuration for backup behavior is completely ignored

## Root Cause Analysis
1. **Backup/Restore CLI Commands**: Missing `GlobalConfig` initialization and target resolution
2. **CcApiSwitcher**: Constructor accepts `global_config` but never uses it for backup settings
3. **Core Backup Logic**: Hard-coded retention values in `_cleanup_old_backups()` method
4. **Auto-backup Logic**: Missing integration with `global_config.is_auto_backup_enabled()`

## Solution Overview
1. **Update CLI Commands**: Initialize `GlobalConfig` and resolve default targets in backup/restore commands
2. **Integrate Core Logic**: Modify `CcApiSwitcher` to consume `GlobalConfig` for backup settings
3. **Honor User Settings**: Use configured retention counts and auto-backup toggles
4. **Maintain Compatibility**: Preserve existing CLI parameter behavior with proper precedence

## Change Relationships
This change spans multiple capabilities:
- **backup-management**: Core backup logic and retention
- **global-configuration**: Integration with GlobalConfig settings
- **cli-interface**: Command parameter resolution and error handling

## Implementation Strategy
- Follow the existing `switch` command pattern for GlobalConfig integration
- Modify core backup methods to use configuration values instead of hard-coding
- Ensure proper precedence: CLI parameters > GlobalConfig > defaults
- Add comprehensive test coverage for custom configurations