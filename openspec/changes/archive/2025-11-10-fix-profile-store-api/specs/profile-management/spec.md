# profile-management Specification

## ADDED Requirements

### Requirement: Profile Store API Encapsulation
The ProfileStore SHALL encapsulate internal directory attributes and provide safe API methods for profile path operations in both explicit and global modes.

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