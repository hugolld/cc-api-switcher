## MODIFIED Requirements

### Requirement: CMD-001 Command Module Organization
CLI commands SHALL be organized into separate modules based on functional domains while maintaining the same external interface.

#### Scenario: Core commands module
**Given** the refactored CLI architecture
**WHEN** implementing profile management commands
**THEN** list, switch, show, validate, backup, restore, diff, import, edit commands SHALL be in `cli/commands.py`
**AND** each command SHALL inherit from BaseCommand
**AND** shared functionality SHALL be provided by the base class

#### Scenario: Configuration commands module
**Given** the refactored CLI architecture
**WHEN** implementing configuration management commands
**THEN** init, config, profile-dir, migrate commands SHALL be in `cli/config_commands.py`
**AND** these commands SHALL share common configuration patterns
**AND** global configuration handling SHALL be consistent

#### Scenario: Command inheritance patterns
**Given** the modular command structure
**WHEN** implementing any CLI command
**THEN** the command SHALL use BaseCommand for common functionality
**AND** SHALL use helper functions for repeated patterns
**AND** SHALL implement consistent error handling

### Requirement: CMD-002 Eliminated Code Duplication
Repeated patterns in CLI commands SHALL be eliminated through shared helpers and base classes.

#### Scenario: GlobalConfig and ProfileStore initialization
**Given** multiple commands need to resolve configuration and stores
**WHEN** implementing the commands
**THEN** the pattern "if directory: ... else: global_config = GlobalConfig()..." SHALL be eliminated
**AND** all commands SHALL use resolve_store_and_config helper
**AND** the logic SHALL be centralized in one location

#### Scenario: Error handling patterns
**Given** multiple commands handle the same exception types
**WHEN** implementing error handling
**THEN** try/except blocks for common errors SHALL use shared helpers
**AND** error message formatting SHALL be consistent
**AND** exit code handling SHALL be standardized

#### Scenario: Console output patterns
**Given** multiple commands display similar formatted output
**WHEN** implementing console interactions
**THEN** common output patterns SHALL use shared helper functions
**AND** Rich console formatting SHALL be consistent
**AND** user interaction patterns SHALL be reusable

### Requirement: CMD-003 Consistent Security Policy Application
All CLI commands SHALL automatically apply consistent security policies.

#### Scenario: Secret masking enforcement
**Given** any command displays potentially sensitive information
**WHEN** the command executes
**THEN** sensitive values SHALL be automatically masked by default
**AND** the masking behavior SHALL be consistent across commands
**AND** security policies SHALL be enforced without explicit implementation

#### Scenario: Global mode security defaults
**Given** commands operating in global mode
**WHEN** handling sensitive operations
**THEN** secure defaults SHALL be applied automatically
**AND** file permissions SHALL be set appropriately
**AND** security policies SHALL align with project standards

### Requirement: CMD-004 Simplified Command Implementation
New commands SHALL be significantly simpler to implement due to shared infrastructure.

#### Scenario: New command implementation
**Given** a developer needs to add a new CLI command
**WHEN** implementing the command
**THEN** the command SHALL inherit most functionality from BaseCommand
**AND** boilerplate code SHALL be minimal
**AND** security and configuration SHALL be handled automatically

#### Scenario: Command testing
**Given** the modular command structure
**WHEN** writing tests for individual commands
**THEN** commands SHALL be easily testable in isolation
**AND** shared functionality SHALL be tested separately
**AND** test setup SHALL be simplified through helper functions