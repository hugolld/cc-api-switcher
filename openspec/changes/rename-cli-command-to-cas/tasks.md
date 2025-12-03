## 1. Update Package Configuration
- [x] 1.1 Modify `pyproject.toml` entry point from `cc-api-switch` to `cas`
- [x] 1.2 Verify package name remains `cc-api-switch` (only entry point changes)
- [x] 1.3 Test that `uv build` creates package with correct entry point

## 2. Update Documentation References
- [x] 2.1 Update `README.md` to use `cas` command in all examples
- [x] 2.2 Update `CLAUDE.md` to reference `cas` instead of `cc-api-switch`
- [x] 2.3 Update installation instructions to show resulting `cas` command
- [x] 2.4 Update usage examples throughout documentation
- [x] 2.5 Update troubleshooting sections to reference `cas` command

## 3. Update CLI Help and Output
- [x] 3.1 Verify CLI app name and help text display appropriately
- [x] 3.2 Ensure error messages reference correct command name where applicable
- [x] 3.3 Test that all subcommands work with new entry point

## 4. Update Development Documentation
- [x] 4.1 Update development commands in `CLAUDE.md` to use `cas` for testing
- [x] 4.2 Update testing instructions to reference `cas` command
- [x] 4.3 Update any internal documentation with command examples

## 5. Testing and Validation
- [x] 5.1 Install package locally and verify `cas` command is available
- [x] 5.2 Test all major subcommands (`cas list`, `cas switch`, `cas show`, etc.)
- [x] 5.3 Verify help output: `cas --help` and `cas <subcommand> --help`
- [x] 5.4 Test error scenarios to ensure proper command name in messages
- [x] 5.5 Run existing test suite to ensure no regressions

## 6. Migration Notes
- [x] 6.1 Add migration note to README about command name change
- [x] 6.2 Document that old `cc-api-switch` command will no longer be available
- [x] 6.3 Ensure users understand impact on existing scripts and automation

## 7. Final Verification
- [x] 7.1 Perform fresh install in clean environment to verify `cas` command creation
- [x] 7.2 Verify package can be uninstalled and reinstalled successfully
- [x] 7.3 Confirm all functionality works identically to previous version
- [x] 7.4 Validate that no references to old command remain in user-facing documentation