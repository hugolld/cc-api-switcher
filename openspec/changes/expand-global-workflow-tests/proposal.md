# Change: Expand Global Workflow Test Coverage

## Why
Current CLI tests predominantly use the `--dir` flag, leaving the default global workflow (no `--dir`) largely untested. This creates a significant coverage gap where critical bugs in global mode could go undetected, as evidenced by multiple critical issues in CODE_REVIEW.md that would have been caught with proper global workflow testing.

## What Changes
- Expand CLI test suite to comprehensively test the default global workflow without `--dir` flag
- Add pytest fixtures for GlobalConfig and temporary configuration environments
- Add tests for import/edit commands in global mode (currently crash due to dereferencing None profiles_dir)
- Add tests for backup/restore commands respecting GlobalConfig default paths and settings
- Add tests for diff command with secret masking in global mode
- Add tests for config-driven path resolution and hierarchical profile discovery
- Ensure all 13 CLI commands work correctly in global mode

## Impact
- **Affected specs**: testing (new capability for comprehensive CLI testing)
- **Affected code**: `tests/test_cli.py` (significant expansion), `tests/conftest.py` (new fixtures)
- **Breaking change**: No - adds tests only
- **Quality improvement**: Catches critical bugs before they reach users, ensures global workflow reliability