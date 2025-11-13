## 1. Implementation
- [x] 1.1 Import `mask_token` function in cli.py
- [x] 1.2 Add `show_secrets` parameter to `diff_profiles` function
- [x] 1.3 Implement masking logic for environment-only mode
- [x] 1.4 Implement masking logic for full JSON diff mode
- [x] 1.5 Add help text and security warning for `--show-secrets` flag

## 2. Testing
- [x] 2.1 Add test for masked diff output in environment-only mode
- [x] 2.2 Add test for masked diff output in full JSON mode
- [x] 2.3 Add test for `--show-secrets` flag showing unmasked values
- [x] 2.4 Add test for consistent masking format with existing `mask_token` function
- [x] 2.5 Add test for edge cases (short tokens, empty values)

## 3. Validation
- [x] 3.1 Run `openspec validate secure-diff-output --strict`
- [x] 3.2 Run existing test suite to ensure no regressions
- [x] 3.3 Manual testing of diff command with various profile types
- [x] 3.4 Verify masking consistency with other CLI commands

## 4. Documentation
- [x] 4.1 Update CLI help text for `diff` command
- [x] 4.2 Add security note to `diff` command help
- [x] 4.3 Update CODE_REVIEW.md to mark Critical Issue 4 as resolved
- [x] 4.4 Verify all documentation reflects new secure behavior