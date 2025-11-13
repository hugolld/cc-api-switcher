## Context
The current test suite has a critical gap: almost all CLI tests use the `--dir` flag, leaving the default global workflow (no `--dir`) untested. This is the primary workflow users encounter, yet it's poorly covered. CODE_REVIEW.md identified 5 critical issues, all of which stem from inadequate global workflow testing.

### Current Testing Problems
1. **Only 3 global mode tests** exist in test_cli.py out of ~30 CLI tests
2. **Critical commands untested**: import, edit, diff in global mode
3. **No integration testing** between GlobalConfig and CLI commands
4. **Missing secret masking tests** for diff output
5. **No config-driven path testing** for backup/restore workflows

### Current Coverage Analysis
```python
# Current: All tests use --dir flag (8 occurrences)
result = runner.invoke(app, ["list", "--dir", str(tmp_path)])

# Missing: Tests without --dir (global mode)
result = runner.invoke(app, ["list"])  # ❌ Not tested
```

## Goals / Non-Goals
- **Goals**: Comprehensive global workflow coverage, catch critical bugs before release, ensure all 13 CLI commands work in global mode, test hierarchical profile discovery
- **Non-Goals**: Test external dependencies, test user environment setup, modify existing production code

## Decisions

### Decision: Create pytest fixtures for GlobalConfig testing
- **What**: Add `global_config_fixture`, `temp_global_config`, and `mock_profile_store` fixtures in `conftest.py`
- **Why**: Eliminates boilerplate, ensures consistent test environment, prevents test pollution
- **Implementation**: Use temporary directories with proper cleanup, mock file system operations

### Decision: Test every CLI command in both modes
- **What**: For each of the 13 CLI commands, create tests for both `--dir` mode and global mode
- **Why**: Ensures backward compatibility and proper global workflow functionality
- **Implementation**: Parameterized tests where possible, explicit test cases for global-specific behavior

### Decision: Focus integration testing on GlobalConfig interactions
- **What**: Test config-driven path resolution, hierarchical profile discovery, environment variable overrides
- **Why**: These are the core features that make global mode different from explicit directory mode
- **Implementation**: Mock XDG directories, test environment variable precedence, verify profile search order

### Decision: Security testing integration
- **What**: Add diff command tests with secret masking verification
- **Why**: Addresses Critical Issue 4 and ensures security consistency
- **Implementation**: Test both masked and `--show-secrets` modes, verify masking format consistency

## Risks / Trade-offs
- **Risk**: Test suite execution time may increase significantly
  - **Mitigation**: Use efficient fixtures, run tests in parallel, optimize setup/teardown
- **Risk**: Complex test setup may introduce brittleness
  - **Mitigation**: Well-designed fixtures, clear test isolation, comprehensive mocking
- **Trade-off**: More complex test code in exchange for significantly better coverage and bug detection

## Migration Plan

### Phase 1: Foundation
1. Create pytest fixtures in `conftest.py`
2. Add GlobalConfig test utilities
3. Create temporary environment setup helpers

### Phase 2: Critical Commands
1. Test import/edit commands in global mode (fixes Critical Issue 1)
2. Test backup/restore with GlobalConfig integration (fixes Critical Issue 2)
3. Test diff command with secret masking (fixes Critical Issue 4)

### Phase 3: Comprehensive Coverage
1. Test all remaining commands in global mode
2. Test hierarchical profile discovery
3. Test environment variable precedence
4. Test error handling and edge cases

### Phase 4: Integration
1. End-to-end workflow testing
2. Performance testing for global mode
3. Documentation and test maintenance guidelines

## Open Questions
- Should we add tests for migration utilities in global mode?
- Should we test interaction with actual XDG directory structures on different platforms?
- Should we add performance benchmarks for global profile discovery vs explicit directory mode?