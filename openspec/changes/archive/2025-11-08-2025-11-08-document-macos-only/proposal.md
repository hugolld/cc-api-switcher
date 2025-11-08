# Document macOS-Only Support

## Problem Statement
The current cc-api-switcher documentation presents the tool as platform-agnostic, but in practice it is only being used and tested on macOS. This creates a misleading user experience where users on other platforms (Windows, Linux) may expect the tool to work out of the box, when in reality it has only been validated on macOS.

## Why
- **Transparency**: Users should have clear expectations about platform support before investing time in installation and setup
- **Support Clarity**: Documentation should accurately reflect the current state of testing and support to avoid user frustration
- **Future Development**: Clear platform documentation provides a foundation for potential cross-platform expansion
- **Troubleshooting**: Platform-specific issues are easier to diagnose when platform expectations are clearly stated

## What Changes
1. **README.md Updates**: Add platform compatibility section and macOS-specific installation notes
2. **Project Documentation**: Update project.md to reflect current macOS-only reality
3. **Installation Instructions**: Add macOS prerequisites and notes
4. **Troubleshooting**: Add platform-specific troubleshooting guidance

## Scope
- **In Scope**: Documentation updates only - no code changes required
- **Out of Scope**: Adding Windows/Linux support, cross-platform testing infrastructure
- **Edge Cases**: Virtual machines, containerized environments, or alternative shells