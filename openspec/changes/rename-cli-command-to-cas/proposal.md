# Change: Rename CLI command from `cc-api-switch` to `cas`

## Why
The current CLI command `cc-api-switch` is long and cumbersome to type repeatedly. A shorter, more convenient command `cas` would improve daily developer experience and reduce typing friction while maintaining all existing functionality.

## What Changes
- **MODIFIED**: Change the CLI entry point from `cc-api-switch` to `cas` in `pyproject.toml`
- **MODIFIED**: Update all documentation references to use the new `cas` command
- **MODIFIED**: Update help text and CLI output to reflect the new command name
- **BREAKING**: Existing users will need to use the new `cas` command instead of `cc-api-switch`

## Impact
- Affected specs: cli-interface (command entry point and user interface)
- Affected code: `pyproject.toml` (entry point), documentation files, CLI help text
- User impact: All command invocations will use the new shorter name
- Migration: Users will need to learn the new command name; old scripts will need updates