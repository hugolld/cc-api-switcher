# profile-store-api Specification

## MODIFIED Requirements

### Requirement: Safe Profile Path Resolution
The ProfileStore SHALL provide API methods that return profile file paths without exposing internal directory attributes, ensuring compatibility with both explicit and global modes.

#### Scenario: Get profile file path in explicit mode
- **WHEN** a CLI command needs the file path for a profile in explicit directory mode
- **AND** the ProfileStore was initialized with a directory parameter
- **THEN** `get_profile_path(name)` returns the correct file path within that directory
- **AND** the path does not expose the internal `profiles_dir` attribute

#### Scenario: Get profile file path in global mode
- **WHEN** a CLI command needs the file path for a profile in global mode
- **AND** the ProfileStore was initialized without a directory parameter
- **THEN** `get_profile_path(name)` returns the correct file path from the global configuration
- **AND** the method works without crashing when `profiles_dir` is None
- **AND** the path is resolved using GlobalConfig's profile discovery

#### Scenario: Check profile existence without directory access
- **WHEN** a CLI command needs to check if a profile file exists
- **THEN** `profile_exists(name)` returns True if the profile file exists
- **AND** the check works in both explicit and global modes
- **AND** the method does not require direct access to `profiles_dir`

#### Scenario: Import command uses safe path resolution
- **WHEN** user runs `cc-api-switch import` in global mode (without --dir)
- **THEN** the command uses `store.get_profile_path()` to resolve the destination path
- **AND** the command does not crash with AttributeError
- **AND** the profile is imported to the correct global location

#### Scenario: Edit command uses safe path resolution
- **WHEN** user runs `cc-api-switch edit <profile>` in global mode (without --dir)
- **THEN** the command uses `store.get_profile_path()` to resolve the profile file path
- **AND** the command does not crash with AttributeError
- **AND** the correct profile file is opened for editing

### Requirement: Profile Path API Consistency
The ProfileStore API SHALL provide consistent behavior across explicit and global modes, abstracting the complexity of hierarchical profile discovery.

#### Scenario: Path resolution returns consistent format
- **WHEN** `get_profile_path(name)` is called in any mode
- **THEN** the returned path is always a Path object
- **AND** the path points to the actual profile file location
- **AND** the path format is consistent regardless of discovery method

#### Scenario: Error handling for missing profiles
- **WHEN** `get_profile_path(name)` is called for a non-existent profile
- **THEN** the method raises ProfileNotFoundError
- **AND** the error message provides actionable guidance
- **AND** the error handling is consistent across modes

#### Scenario: Path resolution respects profile naming convention
- **WHEN** resolving a profile path for profile name "example"
- **THEN** the returned path ends with "example_settings.json"
- **AND** the naming convention is consistent in both modes
- **AND** legacy "example.json" fallback is supported in explicit mode

## ADDED Requirements

### Requirement: Global Mode Regression Protection
The system SHALL include regression tests that verify CLI commands work correctly in global mode without requiring explicit directory parameters.

#### Scenario: Import command test in global mode
- **GIVEN** a temporary profile file to import
- **AND** a GlobalConfig setup with global profiles directory
- **WHEN** running `cc-api-switch import <file>` without --dir
- **THEN** the command completes successfully
- **AND** the profile is imported to the global profiles directory
- **AND** no AttributeError is raised

#### Scenario: Edit command test in global mode
- **GIVEN** a profile exists in the global profiles directory
- **WHEN** running `cc-api-switch edit <profile>` without --dir
- **THEN** the command completes successfully
- **AND** the correct profile file is opened for editing
- **AND** no AttributeError is raised

#### Scenario: List command test in global mode
- **GIVEN** multiple profiles in global discovery locations
- **WHEN** running `cc-api-switch list` without --dir
- **THEN** all discovered profiles are displayed
- **AND** the command does not crash
- **AND** profile sources are correctly identified

#### Scenario: Profile path API unit tests
- **WHEN** testing ProfileStore path resolution methods
- **THEN** both explicit and global modes are tested
- **AND** edge cases like missing profiles are covered
- **AND** path format consistency is verified