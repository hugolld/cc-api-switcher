## MODIFIED Requirements

### Requirement: Package Module Structure
The project SHALL use `cc_api_switcher` as the internal module name to align with the public project identity.

#### Scenario: Package structure reflects project name
- **WHEN** examining the source code directory structure
- **THEN** the main module directory SHALL be `src/cc_api_switcher/`
- **AND** all Python modules SHALL be organized under this directory
- **AND** the package SHALL import as `cc_api_switcher.*`

#### Scenario: Package configuration uses consistent naming
- **WHEN** building or installing the package
- **THEN** pyproject.toml SHALL reference `cc_api_switcher` as the package name
- **AND** the entry point SHALL resolve to the correct module location
- **AND** the package SHALL build without naming conflicts

#### Scenario: CLI command remains stable
- **WHEN** users run `cc-api-switch` command
- **THEN** the command SHALL work exactly as before the rename
- **AND** all CLI functionality SHALL remain unchanged
- **AND** user experience SHALL not be affected by internal renaming