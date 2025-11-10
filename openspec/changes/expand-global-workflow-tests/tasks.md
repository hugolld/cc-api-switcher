## 1. Foundation Setup
- [x] 1.1 Create `tests/conftest.py` with GlobalConfig fixtures
- [x] 1.2 Add `global_config_fixture` for temporary GlobalConfig instances
- [x] 1.3 Add `temp_global_profiles` fixture for isolated profile environments
- [x] 1.4 Add `mock_profile_store` fixture for consistent ProfileStore mocking
- [x] 1.5 Add utility functions for temporary environment setup and cleanup

## 2. Critical Commands Testing (Addresses CODE_REVIEW.md Issues)
- [x] 2.1 Test import command in global mode (fixes Critical Issue 1)
- [x] 2.2 Test edit command in global mode (fixes Critical Issue 1)
- [x] 2.3 Test backup command with GlobalConfig integration (fixes Critical Issue 2)
- [x] 2.4 Test restore command with GlobalConfig defaults (fixes Critical Issue 2)
- [x] 2.5 Test diff command with secret masking (fixes Critical Issue 4)
- [x] 2.6 Test backup retention count configuration (fixes Critical Issue 3)

## 3. Comprehensive CLI Coverage
- [x] 3.1 Test list command in global mode
- [x] 3.2 Test show command in global mode
- [x] 3.3 Test switch command in global mode
- [x] 3.4 Test validate command in global mode
- [x] 3.5 Test backup command full global workflow
- [x] 3.6 Test restore command full global workflow
- [x] 3.7 Test diff command full global workflow
- [x] 3.8 Test import command full global workflow
- [x] 3.9 Test edit command full global workflow
- [x] 3.10 Test config command group in global mode
- [x] 3.11 Test profile-dir command in global mode
- [x] 3.12 Test migrate command in global mode

## 4. Config-Driven Path Testing
- [x] 4.1 Test hierarchical profile discovery precedence
- [x] 4.2 Test environment variable overrides (CC_API_SWITCHER_PROFILE_DIR)
- [x] 4.3 Test XDG config directory compliance
- [x] 4.4 Test default target path resolution from GlobalConfig
- [x] 4.5 Test backup directory configuration and creation
- [x] 4.6 Test config persistence and loading

## 5. Security and Secret Masking Tests
- [x] 5.1 Test diff command masks ANTHROPIC_AUTH_TOKEN by default
- [x] 5.2 Test diff command masks ANTHROPIC_BASE_URL by default
- [x] 5.3 Test --show-secrets flag displays unmasked values
- [x] 5.4 Test masking format consistency with mask_token function
- [x] 5.5 Test list command displays masked values appropriately
- [x] 5.6 Test show command displays masked values appropriately

## 6. Error Handling and Edge Cases
- [x] 6.1 Test missing global configuration auto-initialization
- [x] 6.2 Test GlobalConfig initialization error handling
- [x] 6.3 Test permission errors in global directories
- [x] 6.4 Test profile not found in global mode
- [x] 6.5 Test invalid profile files in global directories
- [x] 6.6 Test concurrent access to global configuration

## 7. Integration and End-to-End Testing
- [x] 7.1 Test complete global workflow: init → import → switch → show
- [x] 7.2 Test backup/restore cycle with GlobalConfig settings
- [x] 7.3 Test migration from local to global configuration
- [x] 7.4 Test profile discovery across multiple locations
- [x] 7.5 Test configuration changes persist across command invocations

## 8. Performance and Reliability
- [x] 8.1 Test profile discovery performance with many profiles
- [x] 8.2 Test configuration loading performance
- [x] 8.3 Test memory usage in global mode
- [x] 8.4 Test cleanup and resource management
- [x] 8.5 Test thread safety of GlobalConfig operations

## 9. Validation and Quality Assurance
- [x] 9.1 Run `openspec validate expand-global-workflow-tests --strict`
- [x] 9.2 Execute full test suite and ensure all new tests pass
- [x] 9.3 Verify test coverage increases significantly (target: >90% CLI coverage)
- [x] 9.4 Run tests on different platforms (Linux, macOS, Windows)
- [x] 9.5 Test with different Python versions (3.8+)
- [x] 9.6 Performance test execution time remains reasonable

## 10. Documentation and Maintenance
- [x] 10.1 Update test documentation in CLAUDE.md
- [x] 10.2 Add guidelines for writing global mode tests
- [x] 10.3 Document pytest fixtures usage patterns
- [x] 10.4 Update CODE_REVIEW.md to mark Critical Issue 5 as resolved
- [x] 10.5 Add continuous integration configuration for new tests