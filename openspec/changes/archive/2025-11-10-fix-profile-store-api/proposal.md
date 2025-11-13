# fix-profile-store-api Proposal

## Summary
Fix critical crashes in `cc-api-switch import` and `cc-api-switch edit` commands when running in global mode (without `--dir` flag) by implementing a ProfileStore API that abstracts profile path management and eliminates direct access to internal attributes.

## Why
The current ProfileStore implementation exposes internal attributes (profiles_dir) that CLI commands directly access, creating a critical failure point in global mode. When users run commands without the --dir flag (the intended primary workflow), ProfileStore sets profiles_dir to None, but CLI import/edit commands crash with AttributeError when dereferencing this None value. This breaks core functionality and makes the tool essentially unusable for users relying on the global configuration system. A proper ProfileStore API would encapsulate path resolution logic and work consistently in both explicit and global modes.

## What Changes
- Add ProfileStore API methods: get_profile_path(), profile_exists(), save_profile_to_location() that work in both explicit and global modes
- Update CLI import/edit commands to use new API methods instead of direct profiles_dir access
- Implement proper path resolution logic that respects global configuration and hierarchical discovery
- Add comprehensive regression tests for import/edit commands in global mode
- Maintain full backward compatibility with existing explicit directory mode

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