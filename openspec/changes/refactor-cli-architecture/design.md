## Context
The current `cli.py` module has grown to 976 lines with significant code duplication and complexity. This architectural debt has directly contributed to multiple critical bugs identified in CODE_REVIEW.md.

### Current Architecture Problems

**Size and Complexity Issues:**
- **976 lines** in a single module with 13 commands
- **2 help panels** but no logical separation in code
- **Repeated patterns** across commands for GlobalConfig/ProfileStore initialization
- **Inconsistent error handling** leading to crashes in global mode

**Code Duplication Analysis:**
```python
# Pattern repeated 12+ times throughout cli.py:
if directory:
    store = ProfileStore(directory)
else:
    global_config = GlobalConfig()
    store = ProfileStore(global_config=global_config)

# Similar try/except patterns repeated:
except ProfileNotFoundError as e:
    console.print(f"[red]Profile not found: {e}[/red]")
    raise typer.Exit(1)
```

**Current Command Distribution:**
- **Commands group (9 commands)**: list, switch, show, validate, backup, restore, diff, import, edit
- **Configuration group (4 commands)**: init, config, profile-dir, migrate
- **Missing**: Shared helpers, base classes, consistent patterns

### Specific Issues Contributing to Critical Bugs

1. **Import/Edit Crashes (Critical Issue 1)**: Direct `store.profiles_dir` dereferencing without helper methods
2. **Backup/Restore Config Issues (Critical Issue 2)**: Inconsistent GlobalConfig usage patterns
3. **Secret Leakage (Critical Issue 4)**: No consistent security policy enforcement
4. **Poor Testability (Critical Issue 5)**: Monolithic structure makes targeted testing difficult

## Goals / Non-Goals
- **Goals**: Modular architecture, eliminate code duplication, consistent error handling, automatic security policies, improved maintainability, easier testing
- **Non-Goals**: Change CLI interface, break existing functionality, alter external dependencies

## Decisions

### Decision: Create Modular CLI Architecture
- **What**: Split `cli.py` into focused modules based on functional domains
- **Why**: Improves maintainability, enables targeted testing, reduces cognitive load
- **Structure**:
  - `cli/__init__.py` - Main entry point and app initialization
  - `cli/commands.py` - Core commands (list, switch, show, validate, backup, restore, diff, import, edit)
  - `cli/config_commands.py` - Configuration commands (init, config, profile-dir, migrate)
  - `cli/base.py` - Base classes and shared functionality
  - `cli/helpers.py` - Common helper functions

### Decision: Introduce Base Command Class with Automatic Policies
- **What**: Create `BaseCommand` class that handles GlobalConfig, ProfileStore, and error handling
- **Why**: Eliminates code duplication, ensures consistent behavior, automatically applies security policies
- **Implementation**:
  ```python
  class BaseCommand:
      def __init__(self, directory: Optional[Path] = None):
          self.store, self.global_config = resolve_store_and_config(directory)
          self.console = Console()

      def handle_error(self, error: Exception) -> None:
          # Consistent error handling pattern

      def ensure_security_policies(self) -> None:
          # Automatic security enforcement
  ```

### Decision: Create Shared Helper Functions
- **What**: Extract common patterns into reusable helper functions
- **Why**: Reduces code duplication, centralizes logic, improves consistency
- **Key Helpers**:
  - `resolve_store_and_config()` - Handle directory vs global mode logic
  - `resolve_target_path()` - Handle target path resolution with GlobalConfig
  - `handle_cli_error()` - Consistent error presentation and exit handling
  - `apply_security_policies()` - Ensure secret masking and security defaults

### Decision: Implement Command Factory Pattern
- **What**: Create command factory that automatically applies security and global configuration
- **Why**: Ensures all new commands inherit proper defaults and security policies
- **Implementation**: Decorator-based approach for automatic behavior injection

### Decision: Maintain Backward Compatibility
- **What**: Preserve all existing CLI interfaces and behaviors
- **Why**: No breaking changes for existing users
- **Implementation**: Internal refactoring only, same `typer` app structure

## Risks / Trade-offs

### Risks
- **Risk**: Refactoring complexity could introduce new bugs
  - **Mitigation**: Comprehensive test coverage, incremental migration, thorough validation
- **Risk**: Temporary breaking changes during development
  - **Mitigation**: Feature flags, incremental rollout, extensive testing
- **Risk**: Performance overhead from new abstractions
  - **Mitigation**: Minimal abstractions, performance testing, avoid over-engineering

### Trade-offs
- **Complexity**: More files and classes vs. single monolithic module
  - **Justification**: Improved maintainability and testability outweighs complexity
- **Abstraction**: Additional layers vs. direct implementation
  - **Justification**: Abstractions eliminate duplication and prevent bugs
- **Learning Curve**: New patterns vs. existing simple structure
  - **Justification**: Clear patterns and documentation reduce onboarding time

## Migration Plan

### Phase 1: Foundation (Low Risk)
1. Create `cli/` package structure
2. Implement `BaseCommand` class with shared functionality
3. Create helper functions for common patterns
4. Add comprehensive tests for new infrastructure

### Phase 2: Configuration Commands (Medium Risk)
1. Migrate `init`, `config`, `profile-dir`, `migrate` to `config_commands.py`
2. Apply `BaseCommand` pattern
3. Test thoroughly in isolation
4. Validate no behavioral changes

### Phase 3: Core Commands (High Risk)
1. Migrate `list`, `switch`, `show`, `validate` to `commands.py`
2. Apply new patterns and test extensively
3. Migrate `backup`, `restore`, `diff`, `import`, `edit`
4. Full integration testing

### Phase 4: Integration and Cleanup
1. Update main `cli.py` to use new modules
2. Remove duplicated code
3. Update imports and dependencies
4. Full test suite validation

## Open Questions

### Architectural Questions
- Should we use composition over inheritance for command base classes?
- How should we handle command-specific configuration within the base class?
- Should we create separate error types for different command categories?

### Implementation Questions
- Should we use dataclasses for command configuration?
- How should we handle async operations in the new architecture?
- Should we implement command middleware for cross-cutting concerns?

### Future Considerations
- Should we design for plugin architecture where external commands can be registered?
- How will this architecture support CLI extensions and custom commands?
- Should we consider command grouping and organization in the new structure?