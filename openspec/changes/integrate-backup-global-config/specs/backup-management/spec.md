# backup-management Specification

## MODIFIED Requirements

### Requirement: Configurable Backup Retention
The system SHALL honor user-configured backup retention counts from GlobalConfig instead of hard-coding to 10 backups.

#### Scenario: Backup with custom retention count
- **GIVEN** GlobalConfig is configured with `backup_retention_count: 5`
- **WHEN** a backup is created automatically or manually
- **THEN** only the 5 most recent backups are retained
- **AND** older backups are automatically cleaned up
- **AND** the retention logic uses the configured value instead of hard-coding 10

#### Scenario: Backup with default retention count
- **GIVEN** GlobalConfig is not configured with a custom retention count
- **WHEN** a backup is created
- **THEN** the default retention count of 10 is used
- **AND** backward compatibility is maintained

#### Scenario: Cleanup honors configured retention
- **WHEN** `_cleanup_old_backups()` is called
- **THEN** the method uses `global_config.get_backup_retention_count()` instead of hard-coding
- **AND** the retention count is passed as a parameter to the cleanup method
- **AND** cleanup behavior matches user configuration

### Requirement: Auto-Backup Toggle Integration
The system SHALL respect the auto-backup toggle setting from GlobalConfig when creating automatic backups.

#### Scenario: Auto-backup enabled
- **GIVEN** GlobalConfig has `auto_backup: true` (default)
- **WHEN** switching profiles with the `--backup` flag
- **THEN** automatic backups are created
- **AND** the backup creation proceeds normally
- **AND** user intent for auto-backup is honored

#### Scenario: Auto-backup disabled
- **GIVEN** GlobalConfig has `auto_backup: false`
- **WHEN** switching profiles without explicit backup flag
- **THEN** no automatic backup is created
- **AND** the profile switching proceeds without backup
- **AND** user preference for no auto-backup is respected

#### Scenario: Manual backup overrides settings
- **GIVEN** GlobalConfig has `auto_backup: false`
- **WHEN** user explicitly runs `cc-api-switch backup` command
- **THEN** a backup is created regardless of auto-backup setting
- **AND** manual backup commands always work
- **AND** user can override auto-backup settings when desired

## ADDED Requirements

### Requirement: GlobalConfig Integration in CcApiSwitcher
The CcApiSwitcher class SHALL fully utilize GlobalConfig for all backup-related settings and target resolution.

#### Scenario: CcApiSwitcher with GlobalConfig
- **WHEN** CcApiSwitcher is initialized with a GlobalConfig instance
- **THEN** backup_retention_count is retrieved from the configuration
- **AND** auto_backup settings are available for backup logic
- **AND** target path resolution uses GlobalConfig when no explicit target is provided
- **AND** all backup behavior reflects user configuration

#### Scenario: CcApiSwitcher without GlobalConfig
- **WHEN** CcApiSwitcher is initialized without GlobalConfig
- **THEN** default backup retention of 10 is used
- **AND** default auto_backup setting of true is used
- **AND** backward compatibility is maintained
- **AND** existing code continues to work unchanged

#### Scenario: Backup settings precedence
- **GIVEN** CLI parameters, GlobalConfig settings, and defaults
- **WHEN** creating backups
- **THEN** CLI parameters take highest precedence
- **AND** GlobalConfig settings override defaults
- **AND** fallback to hard-coded defaults when no configuration exists
- **AND** parameter precedence is clearly documented

### Requirement: Default Target Resolution in Backup/Restore Commands
The backup and restore CLI commands SHALL resolve default target paths using GlobalConfig when no explicit target is provided.

#### Scenario: Backup command with configured default target
- **GIVEN** GlobalConfig is configured with `default_target_path: "/custom/path/settings.json"`
- **WHEN** user runs `cc-api-switch backup` without `--target` flag
- **THEN** backup is created from the configured default target path
- **AND** the system does not fall back to `~/.claude/settings.json`
- **AND** user's configured target is respected

#### Scenario: Backup command with CLI target override
- **GIVEN** GlobalConfig is configured with a default target path
- **WHEN** user runs `cc-api-switch backup --target "/override/path/settings.json"`
- **THEN** backup is created from the CLI-specified target path
- **AND** the CLI parameter overrides the GlobalConfig setting
- **AND** parameter precedence is maintained

#### Scenario: Restore command with configured default target
- **GIVEN** GlobalConfig is configured with a default target path
- **WHEN** user runs `cc-api-switch restore` without `--target` flag
- **THEN** restore operation targets the configured default path
- **AND** the system resolves the target using GlobalConfig
- **AND** user configuration is properly honored

#### Scenario: Restore command with explicit target
- **GIVEN** GlobalConfig is configured with a default target path
- **WHEN** user runs `cc-api-switch restore --target "/explicit/path/settings.json"`
- **THEN** restore operation targets the explicitly provided path
- **AND** CLI parameter takes precedence over GlobalConfig
- **AND** user can override configuration when needed

### Requirement: Backup Configuration Validation
The system SHALL validate backup configuration values and provide clear error messages for invalid settings.

#### Scenario: Invalid retention count
- **GIVEN** GlobalConfig has invalid `backup_retention_count` (e.g., negative number or zero)
- **WHEN** backup operations are performed
- **THEN** the system falls back to default retention count
- **AND** a warning is logged about invalid configuration
- **AND** backup operations continue safely

#### Scenario: Invalid target path
- **GIVEN** GlobalConfig has invalid `default_target_path` (e.g., non-existent parent directory)
- **WHEN** backup operations are attempted
- **THEN** the system provides a clear error message
- **AND** suggests using `--target` parameter or fixing configuration
- **AND** operation fails gracefully without corruption

#### Scenario: Configuration migration
- **GIVEN** existing installation without backup configuration
- **WHEN** system starts or configuration is updated
- **THEN** missing backup settings are populated with safe defaults
- **AND** migration handles missing keys gracefully
- **AND** existing functionality is preserved