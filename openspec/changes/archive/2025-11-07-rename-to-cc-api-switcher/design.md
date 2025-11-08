# Design: Project Rename from settings-switcher to cc-api-switcher

## Context
The project has historically been called "settings-switcher" internally but is publicly known as "cc-api-switcher" (CC API Switcher). This creates naming inconsistency where the CLI command `cc-api-switch` doesn't match the internal module `settings_switcher`. The rename will align internal structure with the public identity.

## Goals / Non-Goals
- **Goals**: Consistent naming throughout the project, clearer module identity, better alignment between CLI and internal structure
- **Non-Goals**: Changing the CLI command name itself, changing external API behavior, breaking existing user workflows

## Decisions

### Module Structure
- **Decision**: Rename `src/settings_switcher/` → `src/cc_api_switcher/`
- **Rationale**: Aligns internal directory structure with project name and CLI command
- **Alternatives considered**:
  - Keep old structure (rejected due to inconsistency)
  - Use hyphenated directory (rejected due to Python import restrictions)

### Class Naming
- **Decision**: `SettingsSwitcher` → `CcApiSwitcher`, `SettingsSwitcherError` → `CcApiSwitcherError`
- **Rationale**: Remove "settings" terminology which is too generic, use project-specific naming
- **Alternatives considered**:
  - Keep old class names (rejected due to inconsistency)
  - Use `ApiSwitcher` alone (rejected - less specific to project)

### CLI Command
- **Decision**: Keep CLI command `cc-api-switch` unchanged
- **Rationale**: Maintains backward compatibility for users, CLI command is already correct
- **Impact**: Only entry point reference in pyproject.toml remains the same

## Migration Plan

### Phase 1: Structural Changes
1. Rename module directory
2. Update package configuration
3. Rename core classes and exceptions

### Phase 2: Import Updates
1. Update all import statements
2. Update documentation
3. Update test files

### Phase 3: Validation
1. Run comprehensive test suite
2. Verify package build and installation
3. Test CLI functionality

## Risks / Trade-offs

### Breaking Changes
- **Risk**: External code importing the module will need update imports
- **Mitigation**: Clear documentation of the change, this is primarily an internal tool

### Development Complexity
- **Risk**: Large number of files to update simultaneously
- **Mitigation**: Systematic approach with comprehensive testing at each step

### Path Dependencies
- **Risk**: Absolute file paths or cached references might break
- **Mitigation**: Clean build environment, refresh all dependencies

## Open Questions
- Should we provide any backward compatibility shims? (Decision: No, keep it clean)
- Impact on existing installations and how to handle them?