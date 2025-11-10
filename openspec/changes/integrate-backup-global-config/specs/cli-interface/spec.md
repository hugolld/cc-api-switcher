# cli-interface Specification

## MODIFIED Requirements

### Requirement: Backup Command GlobalConfig Integration
The backup CLI command SHALL initialize GlobalConfig and use it for target resolution and backup settings.

#### Scenario: Backup command uses GlobalConfig for target resolution
- **GIVEN** GlobalConfig is configured with `default_target_path: "/custom/path/settings.json"`
- **WHEN** user runs `cc-api-switch backup` without `--target` flag
- **THEN** the command initializes GlobalConfig
- **AND** resolves the target path using `global_config.get_default_target_path()`
- **AND** creates backup from the configured target path
- **AND** does not fall back to hardcoded `~/.claude/settings.json`

#### Scenario: Backup command with explicit target
- **GIVEN** GlobalConfig is configured with a default target path
- **WHEN** user runs `cc-api-switch backup --target "/explicit/path/settings.json"`
- **THEN** the CLI parameter takes precedence over GlobalConfig
- **AND** backup is created from the explicitly provided target
- **AND** parameter precedence is maintained

#### Scenario: Backup command passes GlobalConfig to CcApiSwitcher
- **WHEN** creating a CcApiSwitcher instance in the backup command
- **THEN** the GlobalConfig instance is passed to the constructor
- **AND** CcApiSwitcher can access backup retention settings
- **AND** auto-backup settings are available if needed
- **AND** full integration between CLI and core logic is established

### Requirement: Restore Command GlobalConfig Integration
The restore CLI command SHALL initialize GlobalConfig and use it for target resolution and restore operations.

#### Scenario: Restore command uses GlobalConfig for target resolution
- **GIVEN** GlobalConfig is configured with `default_target_path: "/custom/path/settings.json"`
- **WHEN** user runs `cc-api-switch restore` without `--target` flag
- **THEN** the command initializes GlobalConfig
- **AND** resolves the target path using `global_config.get_default_target_path()`
- **AND** restore operation targets the configured path
- **AND** backup listing respects the target configuration

#### Scenario: Restore command with explicit target
- **GIVEN** GlobalConfig is configured with a default target path
- **WHEN** user runs `cc-api-switch restore --target "/explicit/path/settings.json"`
- **THEN** the CLI parameter takes precedence over GlobalConfig
- **AND** restore operation targets the explicitly provided path
- **AND** backup listing is filtered for the explicit target

#### Scenario: Restore command passes GlobalConfig to CcApiSwitcher
- **WHEN** creating a CcApiSwitcher instance in the restore command
- **THEN** the GlobalConfig instance is passed to the constructor
- **AND** restore operations can access backup settings
- **AND** integration is consistent with backup command

#### Scenario: Restore command lists backups for correct target
- **GIVEN** multiple backup directories for different targets
- **WHEN** running `cc-api-switch restore --list` with resolved target
- **THEN** only backups relevant to the resolved target are listed
- **AND** backup listing respects target resolution from GlobalConfig or CLI
- **AND** users see relevant backups for their target

## ADDED Requirements

### Requirement: Error Handling and User Guidance
The backup/restore CLI commands SHALL provide clear error messages and guidance when GlobalConfig integration issues occur.

#### Scenario: Missing GlobalConfig for backup
- **WHEN** GlobalConfig cannot be initialized or loaded
- **THEN** the backup command fails with a clear error message
- **AND** suggests running `cc-api-switch init` to set up configuration
- **AND** provides actionable guidance for users
- **AND** operation fails gracefully without data corruption

#### Scenario: Invalid target path resolution
- **GIVEN** GlobalConfig has invalid `default_target_path` configuration
- **WHEN** backup/restore command tries to resolve the target
- **THEN** the command fails with a clear error message
- **AND** indicates the problematic configuration setting
- **AND** suggests using `--target` parameter as a workaround
- **AND** provides steps to fix the configuration

#### Scenario: Backup operation with custom settings
- **WHEN** backup operation completes with custom retention or settings
- **THEN** the command output indicates the settings used
- **AND** shows retention count if different from default
- **AND** provides clear feedback about backup configuration
- **AND** users understand what settings were applied

### Requirement: CLI Help and Documentation Updates
The backup/restore CLI commands SHALL include help text and documentation that reflects GlobalConfig integration.

#### Scenario: Backup command help text
- **WHEN** user runs `cc-api-switch backup --help`
- **THEN** help text mentions GlobalConfig integration
- **AND** explains default target resolution behavior
- **AND** documents configuration precedence
- **AND** references `cc-api-switch config` for backup settings

#### Scenario: Restore command help text
- **WHEN** user runs `cc-api-switch restore --help`
- **THEN** help text mentions GlobalConfig integration
- **AND** explains default target resolution behavior
- **AND** documents backup discovery and listing
- **AND** references related configuration commands

#### Scenario: Configuration reference in help
- **WHEN** users explore backup/restore command help
- **THEN** help text references relevant GlobalConfig settings
- **AND** suggests configuration commands for customization
- **AND** provides examples of configuration usage
- **AND** links to comprehensive documentation