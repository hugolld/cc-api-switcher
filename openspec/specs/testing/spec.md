# testing Specification

## Purpose
TBD - created by archiving change expand-global-workflow-tests. Update Purpose after archive.
## Requirements
### Requirement: TEST-001 Global Workflow Test Coverage
All CLI commands SHALL be tested in default global mode (without --dir flag) to ensure proper functionality and prevent critical bugs.

#### Scenario: Import command global mode functionality
**Given** a user runs the import command without specifying --dir
**When** they import a valid profile
**THEN** the command SHALL succeed without crashing
**AND** the profile SHALL be saved to the global profiles directory
**AND** no AttributeError about profiles_dir being None SHALL occur

#### Scenario: Edit command global mode functionality
**Given** a user runs the edit command without specifying --dir
**WHEN** they edit an existing global profile
**THEN** the command SHALL succeed without crashing
**AND** the correct profile SHALL be opened for editing
**AND** no AttributeError about profiles_dir being None SHALL occur

#### Scenario: Backup command respects GlobalConfig settings
**Given** a user has configured a custom default target path in GlobalConfig
**WHEN** they run the backup command without --target
**THEN** the backup SHALL be created from the configured default target path
**AND** the configured backup retention count SHALL be respected
**AND** the auto-backup setting SHALL be honored

#### Scenario: Restore command uses GlobalConfig defaults
**Given** a user has configured a custom default target path in GlobalConfig
**WHEN** they run the restore command without --target
**THEN** the restore SHALL use the configured default target path
**AND** the restore SHALL search for backups in the correct location

### Requirement: TEST-002 Secret Masking Test Coverage
The diff command SHALL be tested to ensure sensitive values are properly masked by default in global mode.

#### Scenario: Diff command masks secrets in global mode
**Given** two profiles with different API tokens and base URLs
**WHEN** a user runs `cc-api-switch diff profile1 profile2` without --dir
**THEN** the output SHALL show masked tokens instead of raw values
**AND** the masking format SHALL match the mask_token function behavior
**AND** no sensitive credentials SHALL be visible in the test output

#### Scenario: Diff command --show-secrets functionality
**Given** two profiles with different sensitive values
**WHEN** a user runs `cc-api-switch diff profile1 profile2 --show-secrets`
**THEN** the output SHALL display raw unmasked values
**AND** a security warning SHALL be present
**AND** this behavior SHALL be testable without exposing secrets in test logs

### Requirement: TEST-003 Config-Driven Path Resolution Testing
Tests SHALL verify that GlobalConfig properly drives path resolution and hierarchical profile discovery.

#### Scenario: Hierarchical profile discovery in tests
**Given** a test environment with profiles in multiple locations
**WHEN** a CLI command is run without --dir
**THEN** the profile search SHALL follow the correct precedence order
**AND** environment variable overrides SHALL work correctly
**AND** XDG config directories SHALL be respected

#### Scenario: Environment variable precedence in tests
**Given** conflicting profile locations via CLI arg, env var, and global config
**WHEN** a command is run
**THEN** CLI argument SHALL take precedence
**AND** environment variable SHALL override global config
**AND** the correct profile SHALL be found and used

### Requirement: TEST-004 Pytest Fixtures for Global Testing
Comprehensive pytest fixtures SHALL be provided to facilitate global workflow testing.

#### Scenario: GlobalConfig fixture setup
**Given** a test function needs a GlobalConfig instance
**WHEN** using the global_config_fixture
**THEN** a temporary GlobalConfig SHALL be created with valid configuration
**AND** the fixture SHALL clean up temporary files after the test
**AND** the fixture SHALL be reusable across multiple tests

#### Scenario: Temporary profile environment fixture
**Given** a test needs isolated profile files
**WHEN** using the temp_global_profiles fixture
**THEN** a temporary global profiles directory SHALL be created
**AND** test profiles SHALL be available in the directory
**AND** the fixture SHALL restore the original environment after testing

### Requirement: TEST-005 Error Handling and Edge Cases
Global mode error handling SHALL be thoroughly tested to ensure graceful degradation.

#### Scenario: Missing global configuration handling
**Given** no global configuration exists
**WHEN** a CLI command is run without --dir
**THEN** the command SHALL create default configuration
**AND** the command SHALL succeed with appropriate defaults
**AND** the user SHALL be informed about the auto-initialization

#### Scenario: GlobalConfig initialization errors
**Given** GlobalConfig cannot be initialized (permissions, disk space, etc.)
**WHEN** a CLI command is run in global mode
**THEN** the command SHALL fail with a clear error message
**AND** the error SHALL be actionable for the user
**AND** the application SHALL not crash with an unhandled exception

