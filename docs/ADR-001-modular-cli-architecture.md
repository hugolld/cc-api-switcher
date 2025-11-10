# ADR 001: Modular CLI Architecture

## Status
Accepted

## Context
The original `cli.py` module had grown to 976 lines with significant code duplication, inconsistent error handling, and maintenance challenges. This complexity contributed to multiple critical bugs and made testing and extension difficult.

## Decision
We implemented a modular CLI architecture with the following components:

### Architecture Overview
```
src/cc_api_switcher/cli/
├── __init__.py          # Package entry point
├── app.py              # Main typer app and command registration
├── base.py             # BaseCommand class and shared infrastructure
├── helpers.py          # Common helper functions
├── commands.py         # Core commands (9 commands)
└── config_commands.py  # Configuration commands (4 commands)
```

### Key Components

#### BaseCommand Class
- Automatically handles GlobalConfig and ProfileStore resolution
- Provides consistent error handling through `handle_error()` method
- Enforces security policies automatically
- Provides console output management

#### Helper Functions
- `resolve_store_and_config()` - Unified directory/global mode handling
- `resolve_target_path()` - Consistent target path resolution
- `handle_cli_error()` - Standardized error presentation
- `apply_security_policies()` - Automatic security enforcement

#### Command Factory Pattern
- `CommandFactory` class for creating new commands with automatic infrastructure
- `@command` decorator for simple command creation
- Automatic error handling and security policy inheritance

### Command Organization
- **Commands group**: Core functionality (list, switch, show, validate, backup, restore, diff, import, edit)
- **Configuration group**: Setup and management (init, config, profile-dir, migrate)

## Consequences

### Benefits
1. **Maintainability**: Reduced from 976-line monolith to focused modules (~200-300 lines each)
2. **Code Reuse**: Eliminated repeated GlobalConfig/ProfileStore patterns
3. **Consistency**: Unified error handling and security policies
4. **Testability**: Individual modules can be tested in isolation
5. **Extensibility**: Command factory pattern makes adding new commands straightforward
6. **Performance**: Optimized helper functions with caching and efficient algorithms

### Trade-offs
1. **Complexity**: More files and classes vs. single module
2. **Learning Curve**: New patterns for developers to learn
3. **Import Overhead**: Additional module imports (minimal impact)

### Migration Impact
- **Breaking Changes**: None - CLI interface remains identical
- **Backward Compatibility**: Fully maintained
- **Performance**: Improved due to optimized helpers and reduced duplication

## Future Considerations

### Plugin Architecture
The command factory pattern provides foundation for future plugin system:
- Commands can be dynamically registered
- Metadata system supports command discovery
- BaseCommand infrastructure ensures consistent behavior

### Extension Points
1. **Custom Commands**: Use `@command` decorator for new commands
2. **Command Groups**: Create new modules for different functional areas
3. **Security Policies**: Extend `apply_security_policies()` for new requirements
4. **Helper Functions**: Add new helpers to `helpers.py` for reusable patterns

### Monitoring and Metrics
- BaseCommand provides hook points for future telemetry
- Error handling patterns support consistent error reporting
- Command metadata enables usage tracking

## Implementation Notes

### Security
- All commands automatically inherit security policies
- Token masking and permission handling centralized
- Input validation patterns enforced consistently

### Testing
- Each module has corresponding test file
- BaseCommand and helpers extensively tested
- Integration tests verify end-to-end functionality

### Performance
- Helper functions use caching where appropriate
- Optimized algorithms for common operations
- Minimal overhead from abstraction layer

## Decision Record
- **Date**: 2025-11-10
- **Status**: Accepted
- **Implementors**: Claude Code
- **Reviewers**: N/A
- **Related Proposals**: refactor-cli-architecture

This ADR documents the architectural decision and provides guidance for future development and maintenance of the CLI system.