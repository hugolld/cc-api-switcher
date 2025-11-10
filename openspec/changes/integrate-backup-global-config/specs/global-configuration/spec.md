# global-configuration Specification

## ADDED Requirements

### Requirement: Backup Settings Integration
The GlobalConfig system SHALL provide comprehensive backup configuration settings that are consumed by CcApiSwitcher and CLI commands.

#### Scenario: Configure backup retention count
- **GIVEN** a GlobalConfig instance
- **WHEN** setting `backup_retention_count` to a valid integer
- **THEN** the configuration is persisted correctly
- **AND** `get_backup_retention_count()` returns the configured value
- **AND** the value is used by CcApiSwitcher for backup cleanup

#### Scenario: Configure auto-backup toggle
- **GIVEN** a GlobalConfig instance
- **WHEN** setting `auto_backup` to true or false
- **THEN** the configuration is persisted correctly
- **AND** `is_auto_backup_enabled()` returns the configured boolean
- **AND** the value is respected by backup creation logic

#### Scenario: Configure default target path for backups
- **GIVEN** a GlobalConfig instance
- **WHEN** setting `default_target_path` to a valid file path
- **THEN** the configuration is persisted correctly
- **AND** `get_default_target_path()` returns the configured path
- **AND** the path is used by backup/restore commands when no target is specified

#### Scenario: Default configuration values
- **GIVEN** a fresh GlobalConfig without backup settings
- **WHEN** accessing backup configuration methods
- **THEN** `get_backup_retention_count()` returns 10 (default)
- **AND** `is_auto_backup_enabled()` returns true (default)
- **AND** `get_default_target_path()` returns `~/.claude/settings.json` (default)
- **AND** backward compatibility is maintained

### Requirement: Configuration Precedence and Resolution
The system SHALL implement clear precedence rules for backup configuration between CLI parameters and GlobalConfig settings.

#### Scenario: CLI target parameter vs GlobalConfig
- **GIVEN** GlobalConfig has `default_target_path` configured
- **WHEN** CLI command is run with explicit `--target` parameter
- **THEN** the CLI parameter takes precedence
- **AND** the GlobalConfig setting is ignored for this operation
- **AND** user can override configuration when needed

#### Scenario: No CLI parameter with GlobalConfig
- **GIVEN** GlobalConfig has `default_target_path` configured
- **WHEN** CLI command is run without `--target` parameter
- **THEN** the GlobalConfig setting is used
- **AND** the system resolves the target from configuration
- **AND** user configuration is properly honored

#### Scenario: No CLI parameter and no GlobalConfig
- **GIVEN** no CLI target parameter and no GlobalConfig target configuration
- **WHEN** CLI command is run without `--target` parameter
- **THEN** the system falls back to default target path
- **AND** `~/.claude/settings.json` is used as the target
- **AND** existing behavior is preserved

### Requirement: Configuration Validation and Safety
The GlobalConfig system SHALL validate backup configuration values and provide safe fallbacks for invalid settings.

#### Scenario: Validate backup retention count
- **WHEN** setting `backup_retention_count` to invalid value (negative, zero, non-integer)
- **THEN** the system rejects the invalid value
- **AND** provides a clear error message
- **AND** maintains the previous valid setting
- **AND** does not allow corrupt configuration

#### Scenario: Validate target path format
- **WHEN** setting `default_target_path` to invalid path
- **THEN** the system performs basic path validation
- **AND** rejects obviously invalid paths
- **AND** provides actionable error messages
- **AND** suggests proper path formats

#### Scenario: Configuration upgrade and migration
- **GIVEN** existing GlobalConfig without backup settings
- **WHEN** the system starts or configuration is accessed
- **THEN** missing backup settings are automatically populated with defaults
- **AND** existing configuration is preserved
- **AND** migration happens transparently to users
- **AND** no manual intervention is required