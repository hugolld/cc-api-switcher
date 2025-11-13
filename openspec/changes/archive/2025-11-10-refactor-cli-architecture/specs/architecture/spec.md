## ADDED Requirements

### Requirement: ARCH-001 Modular CLI Package Structure
The CLI SHALL be organized into a modular package structure with clear separation of concerns.

#### Scenario: CLI package organization
**Given** the refactored CLI architecture
**WHEN** examining the source code structure
**THEN** the code SHALL be organized into:
- `cli/__init__.py` - Main typer app entry point
- `cli/commands.py` - Core profile management commands
- `cli/config_commands.py` - Configuration management commands
- `cli/base.py` - Base command classes and shared functionality
- `cli/helpers.py` - Common helper functions and utilities
**AND** each module SHALL have a single, clear responsibility

#### Scenario: Module size limits
**Given** the modular CLI architecture
**WHEN** measuring individual module complexity
**THEN** no single module SHALL exceed 300 lines of code
**AND** each module SHALL focus on a specific functional domain
**AND** the total lines across all modules SHALL be approximately the same as the original

### Requirement: ARCH-002 Base Command Class with Shared Functionality
A base command class SHALL provide common functionality for all CLI commands.

#### Scenario: Base command initialization
**Given** a new CLI command inherits from BaseCommand
**WHEN** the command is initialized with optional directory parameter
**THEN** the base class SHALL automatically resolve ProfileStore and GlobalConfig
**AND** the command SHALL handle both explicit directory and global modes
**AND** consistent error handling SHALL be configured

#### Scenario: Automatic security policy application
**Given** a command inherits from BaseCommand
**WHEN** the command handles sensitive data
**THEN** the base class SHALL automatically apply security policies
**AND** secret masking SHALL be enforced by default
**AND** security policies SHALL be consistent across all commands

#### Scenario: Consistent error handling
**Given** a command inherits from BaseCommand
**WHEN** an exception occurs during command execution
**THEN** the base class SHALL provide consistent error formatting
**AND** appropriate exit codes SHALL be returned
**AND** user-friendly error messages SHALL be displayed

### Requirement: ARCH-003 Shared Helper Functions
Common CLI patterns SHALL be extracted into reusable helper functions.

#### Scenario: Store and configuration resolution
**Given** multiple commands need to resolve ProfileStore and GlobalConfig
**WHEN** using the resolve_store_and_config helper
**THEN** the helper SHALL handle directory vs global mode logic
**AND** it SHALL return properly initialized objects
**AND** the pattern SHALL be consistent across all commands

#### Scenario: Target path resolution
**Given** commands need to resolve target paths with GlobalConfig defaults
**WHEN** using the resolve_target_path helper
**THEN** it SHALL respect GlobalConfig default target settings
**AND** CLI parameter overrides SHALL take precedence
**AND** fallback paths SHALL be provided when needed

#### Scenario: Error handling standardization
**Given** multiple commands need to handle common error types
**WHEN** using the handle_cli_error helper
**THEN** ProfileNotFoundError SHALL display profile not found messages
**AND** GlobalConfigError SHALL display configuration error messages
**AND** BackupError SHALL display backup operation error messages

### Requirement: ARCH-004 Command Factory with Policy Injection
New commands SHALL automatically inherit security policies and global configuration support.

#### Scenario: Automatic policy inheritance
**Given** a new command is registered using the command factory
**WHEN** the command is executed
**THEN** it SHALL automatically inherit global configuration support
**AND** security policies SHALL be applied without explicit implementation
**AND** error handling patterns SHALL be consistent

#### Scenario: Decorator-based configuration
**Given** a command function needs specific configuration
**WHEN** applying command decorators
**THEN** the decorator SHALL inject required functionality
**AND** command-specific configuration SHALL be respected
**AND** global defaults SHALL be applied automatically

### Requirement: ARCH-005 Backward Compatibility Preservation
The refactoring SHALL maintain complete backward compatibility with existing CLI interfaces.

#### Scenario: CLI interface preservation
**Given** existing CLI scripts and user workflows
**WHEN** the refactored CLI is used
**THEN** all existing commands SHALL work identically
**AND** command-line arguments SHALL remain unchanged
**AND** output formats SHALL be preserved

#### Scenario: Import compatibility
**Given** existing code imports from cc_api_switcher.cli
**WHEN** the refactored code is used
**THEN** the main app object SHALL remain importable from the same location
**AND** public APIs SHALL remain stable
**AND** existing integrations SHALL continue to work