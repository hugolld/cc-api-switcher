# Change: Refactor CLI Architecture into Modular Components

## Why
The current `cli.py` module is 976 lines with 13 commands across 2 groups, making it difficult to maintain, test, and extend. Repeated patterns for GlobalConfig initialization, ProfileStore creation, and error handling create code duplication and increase the likelihood of bugs. This complexity contributed to the 5 critical issues identified in CODE_REVIEW.md.

## What Changes
- Decompose the 976-line `cli.py` into cohesive, focused modules based on functional separation
- Create shared helpers for common patterns: store/target resolution, error handling, and global mode defaults
- Introduce a base command class that automatically inherits global-mode defaults and security policies
- Separate Commands (9 commands) from Configuration (4 commands) into distinct modules
- Create a CLI framework that ensures future commands automatically follow security best practices

## Impact
- **Affected specs**: architecture (new capability for modular CLI design), cli-commands (modified command structure)
- **Affected code**: `src/cc_api_switcher/cli.py` (refactored into multiple modules)
- **Breaking change**: No - maintains same CLI interface, improves internal structure
- **Maintainability improvement**: Significantly reduces code duplication, improves testability, enables easier command addition

## Expected Benefits
- Reduced module size from 976 lines to ~200-300 lines per module
- Elimination of repeated GlobalConfig/ProfileStore patterns
- Consistent error handling across all commands
- Built-in security policies for all new commands
- Easier testing and maintenance of individual command groups