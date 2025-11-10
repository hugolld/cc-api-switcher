# fix-profile-store-api Proposal

## Summary
Fix critical crashes in `cc-api-switch import` and `cc-api-switch edit` commands when running in global mode (without `--dir` flag) by implementing a ProfileStore API that abstracts profile path management and eliminates direct access to internal attributes.

## Problem Statement
The current implementation has a critical bug where CLI import/edit commands crash in global mode because they directly dereference `store.profiles_dir`, which is `None` when no explicit directory is provided. This breaks the primary workflow for users who rely on the global configuration system.

## Root Cause Analysis
- **Location**: `src/cc_api_switcher/cli.py:579` and `src/cc_api_switcher/cli.py:639`
- **Issue**: ProfileStore sets `self.profiles_dir = None` in global mode but CLI commands directly access this attribute
- **Impact**: Core functionality unusable in intended global mode workflow
- **Gap**: No ProfileStore API methods for safe profile path resolution

## Solution Overview
1. **Add ProfileStore API methods** for profile path operations that work in both explicit and global modes
2. **Update CLI commands** to use the new API instead of direct attribute access
3. **Add regression tests** to ensure global mode works without `--dir` flag
4. **Maintain backward compatibility** with existing explicit directory mode

## Change Relationships
This change focuses on the profile-management capability and addresses critical reliability issues in the ProfileStore API.

## Implementation Strategy
- Minimal, focused changes to fix the immediate crashing issue
- New API methods encapsulate path resolution logic
- Update only the affected CLI commands (import, edit)
- Add comprehensive test coverage for global mode scenarios