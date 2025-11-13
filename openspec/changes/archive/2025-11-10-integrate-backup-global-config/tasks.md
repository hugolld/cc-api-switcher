# Implementation Tasks

## Phase 1: Core CcApiSwitcher Integration
- [x] **Modify CcApiSwitcher constructor** to store and use GlobalConfig for backup settings
  - Store `global_config` instance as instance variable
  - Add methods to get backup settings from GlobalConfig with fallbacks
  - Update constructor to initialize backup settings from configuration

- [x] **Update _create_backup method** to use GlobalConfig auto-backup setting
  - Check `global_config.is_auto_backup_enabled()` before creating backups
  - Respect auto-backup toggle for automatic backup creation
  - Maintain backward compatibility for manual backups

- [x] **Update _cleanup_old_backups method** to use configurable retention
  - Replace hard-coded `keep: int = 10` with configurable value
  - Use `global_config.get_backup_retention_count()` with fallback to 10
  - Ensure cleanup logic works with both configured and default values

- [x] **Add backup settings validation** in CcApiSwitcher
  - Validate retention count is positive integer
  - Handle invalid configuration gracefully with warnings
  - Provide fallback behavior for corrupt settings

## Phase 2: CLI Command Updates
- [x] **Update backup command** to use GlobalConfig for target resolution
  - Initialize GlobalConfig instance at command start
  - Resolve default target using `global_config.get_default_target_path()`
  - Pass GlobalConfig to CcApiSwitcher constructor
  - Maintain CLI parameter precedence

- [x] **Update restore command** to use GlobalConfig for target resolution
  - Initialize GlobalConfig instance at command start
  - Resolve default target using `global_config.get_default_target_path()`
  - Pass GlobalConfig to CcApiSwitcher constructor
  - Ensure backup listing respects resolved target

- [x] **Add error handling** for GlobalConfig integration in CLI commands
  - Handle GlobalConfig initialization failures gracefully
  - Provide clear error messages for invalid target configuration
  - Suggest fixes and workarounds for configuration issues

- [x] **Update CLI help text** to reflect GlobalConfig integration
  - Update backup command help to mention configuration integration
  - Update restore command help to explain target resolution
  - Add references to configuration commands

## Phase 3: Testing Implementation
- [x] **Create CcApiSwitcher GlobalConfig integration tests**
  - Test CcApiSwitcher with GlobalConfig for backup retention
  - Test auto-backup toggle functionality
  - Test configuration validation and fallback behavior
  - Test target resolution with and without GlobalConfig

- [x] **Add backup command GlobalConfig tests**
  - Test backup command with configured default target
  - Test backup command with CLI target override
  - Test backup command with custom retention settings
  - Test error handling for invalid configuration

- [x] **Add restore command GlobalConfig tests**
  - Test restore command with configured default target
  - Test restore command with CLI target override
  - Test backup listing with resolved targets
  - Test error handling for configuration issues

- [x] **Add integration tests for custom backup settings**
  - Test complete workflow with custom retention count
  - Test auto-backup enable/disable scenarios
  - Test configuration precedence and validation
  - Test edge cases and error recovery

## Phase 4: Validation and Documentation
- [x] **Run existing test suite** to ensure no regressions
  - Execute `PYTHONPATH=/Users/hugodong/Documents/Claude/cc-api-switcher/src uv run pytest`
  - Verify all existing tests still pass
  - Check backward compatibility is maintained

- [x] **Manual testing of backup configuration scenarios**
  - Test backup with custom retention counts manually
  - Test backup with auto-backap disabled/enabled
  - Test restore with custom target configurations
  - Verify configuration precedence works correctly

- [x] **End-to-end testing of critical scenarios**
  - Test complete backup/restore workflow with GlobalConfig
  - Test migration scenarios from existing installations
  - Test configuration upgrade and fallback behavior
  - Validate user experience with custom settings

## Dependencies and Notes

### Dependencies
- GlobalConfig system must be properly understood and working
- CcApiSwitcher constructor changes must not break existing callers
- CLI command updates must follow existing patterns
- Test fixtures must support GlobalConfig testing

### Risk Mitigation
- Maintain full backward compatibility for existing code
- Provide safe fallbacks for all configuration values
- Ensure CLI parameter precedence is preserved
- Add comprehensive error handling and validation
- Test all configuration edge cases thoroughly

### Technical Considerations
- GlobalConfig instance must be passed to all CcApiSwitcher instances
- Backup methods should check for None global_config gracefully
- Target resolution must follow CLI > GlobalConfig > default precedence
- Configuration validation should not prevent basic functionality
- Error messages must be actionable and user-friendly

### Validation Criteria
- All existing CLI functionality continues to work unchanged
- GlobalConfig settings are properly honored for all backup operations
- Configuration precedence works correctly in all scenarios
- Custom retention counts are respected and applied correctly
- Auto-backup toggle works as expected
- Error handling provides clear guidance for configuration issues
- Documentation accurately reflects new integration capabilities