## ADDED Requirements

### Requirement: CLI-001 Short Command Name Entry Point
The CLI tool SHALL provide a short, convenient command entry point named `cas` for all operations.

#### Scenario: User invokes short command
**Given** the cc-api-switcher tool is installed
**WHEN** a user runs the `cas` command
**THEN** the tool SHALL execute with the same functionality as the previous `cc-api-switch` command
**AND** all existing subcommands and options SHALL be available
**AND** the tool SHALL respond normally to all CLI operations

#### Scenario: Command help and usage
**Given** a user runs `cas --help` or `cas --help`
**THEN** the help output SHALL display the `cas` command name
**AND** all subcommands SHALL be listed with proper descriptions
**AND** usage examples SHALL use the `cas` command format

#### Scenario: All subcommands work with short name
**Given** the tool is accessed via the `cas` command
**WHEN** a user runs any subcommand (list, switch, show, validate, backup, restore, diff, import, edit, init, config, profile-dir, migrate)
**THEN** each subcommand SHALL function identically to the previous `cc-api-switch` invocation
**AND** all options and arguments SHALL be accepted
**AND** output SHALL be consistent with previous behavior

## MODIFIED Requirements

### Requirement: DOC-001 Platform Compatibility Disclosure
Documentation SHALL clearly indicate that the tool is currently supported and tested only on macOS and SHALL reference the new `cas` command name.

#### Scenario: User Visiting Project README
**Given** a potential user visits the project README
**WHEN** they look for installation or usage instructions
**THEN** they SHALL see references to the `cas` command instead of `cc-api-switch`
**AND** installation instructions SHALL show `uv tool install .` results in the `cas` command
**AND** usage examples SHALL demonstrate the `cas` command

#### Scenario: Installation Instructions Update
**Given** a user is following installation instructions
**WHEN** they reach the usage verification section
**THEN** they SHALL see `cas --help` or `cas list` as verification commands
**AND** documentation SHALL emphasize that the installed command is `cas`
**AND** migration notes SHALL explain the change from `cc-api-switch` to `cas`

### Requirement: DOC-003 Troubleshooting Platform Guidance
Troubleshooting documentation SHALL include updated command references using the new `cas` command name.

#### Scenario: Command Not Found Troubleshooting
**Given** a user experiences "command not found" errors
**WHEN** they consult the troubleshooting section
**THEN** they SHALL see troubleshooting guidance for the `cas` command
**AND** solutions SHALL reference ensuring `cas` is in PATH
**AND** verification steps SHALL use `cas --version` or similar

#### Scenario: Usage Examples in Documentation
**Given** a user is reading through documentation examples
**WHEN** they encounter command examples
**THEN** all examples SHALL use the `cas` command prefix
**AND** no references to `cc-api-switch` SHALL remain in current documentation
**AND** migration notes SHALL explain the command name change if needed