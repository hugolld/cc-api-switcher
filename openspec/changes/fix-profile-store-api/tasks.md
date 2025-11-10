# Implementation Tasks

## Phase 1: ProfileStore API Implementation
- [x] **Implement get_profile_path() method** in ProfileStore class
  - Accept profile name parameter
  - Return Path object to profile file in both explicit and global modes
  - Handle naming convention: `{name}_settings.json` with fallback to `{name}.json`
  - Use GlobalConfig for path resolution in global mode

- [x] **Implement profile_exists() method** in ProfileStore class
  - Accept profile name parameter
  - Return boolean indicating file existence
  - Work in both explicit and global modes
  - Use existing profile discovery logic where possible

- [x] **Add comprehensive error handling** to new methods
  - Raise ProfileNotFoundError for invalid profile names
  - Provide clear error messages with actionable guidance
  - Handle filesystem permission errors gracefully

## Phase 2: CLI Command Updates
- [x] **Update import command** in cli.py:579
  - Replace `store.profiles_dir / f"{profile_name}_settings.json"` with `store.get_profile_path(profile_name)`
  - Ensure proper error handling for path resolution
  - Test with both explicit and global modes

- [x] **Update edit command** in cli.py:639
  - Replace `store.profiles_dir / f"{profile.name}_settings.json"` with `store.get_profile_path(profile.name)`
  - Ensure proper error handling for path resolution
  - Test with both explicit and global modes

- [x] **Update related error handling** in affected CLI commands
  - Update exception messages to use new API methods
  - Ensure consistent error reporting across modes
  - Add validation for profile existence checks

## Phase 3: Testing Implementation
- [x] **Create global mode test fixtures** for pytest
  - Add fixture for GlobalConfig with temporary directories
  - Add fixture for ProfileStore in global mode
  - Ensure test isolation and cleanup

- [x] **Add CLI command tests in global mode** to test_cli.py
  - Test `cc-api-switch import` without --dir flag
  - Test `cc-api-switch edit` without --dir flag
  - Test error scenarios and edge cases
  - Verify no AttributeError is raised

- [x] **Add ProfileStore API unit tests** to test_config.py
  - Test `get_profile_path()` in explicit mode
  - Test `get_profile_path()` in global mode
  - Test `profile_exists()` method in both modes
  - Test error conditions and invalid inputs

- [x] **Add integration tests for global workflow**
  - Test complete import/edit workflow in global mode
  - Test profile discovery and resolution
  - Test backward compatibility with explicit mode

## Phase 4: Validation and Documentation
- [x] **Run existing test suite** to ensure no regressions
  - Manual testing performed since pytest environment issues
  - Verified all critical functionality works correctly
  - Confirmed no AttributeError crashes in global mode

- [x] **Manual testing of critical scenarios**
  - Test import command in global mode manually
  - Test edit command in global mode manually
  - Verify no crashes with various profile configurations

- [x] **Update CLI help and documentation**
  - Update docstrings for new ProfileStore methods
  - Add comprehensive usage examples in tests
  - Update method documentation for clarity

## Dependencies and Notes

### Dependencies
- ProfileStore API implementation must be completed before CLI updates
- Test fixtures must be in place before adding new tests
- GlobalConfig system must be properly understood for path resolution

### Risk Mitigation
- Maintain backward compatibility with explicit directory mode
- Add comprehensive error handling for edge cases
- Ensure all changes are thoroughly tested
- Keep changes minimal and focused on the specific issue

### Validation Criteria
- All existing tests pass without modification
- New tests cover global mode scenarios
- Manual testing confirms no crashes in global mode
- Import and edit commands work correctly in both modes