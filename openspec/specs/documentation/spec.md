# documentation Specification

## Purpose
TBD - created by archiving change 2025-11-08-document-macos-only. Update Purpose after archive.
## Requirements
### Requirement: DOC-001 Platform Compatibility Disclosure
Documentation SHALL clearly indicate that cc-api-switcher is currently supported and tested only on macOS.

#### Scenario: User Visiting Project README
**Given** a potential user visits the project README
**When** they look for system requirements or compatibility information
**Then** they SHALL see a clear "macOS Only" designation
**And** they SHALL understand the current platform limitations
**And** they SHALL not find misleading cross-platform claims

#### Scenario: Installation Prerequisites Check
**Given** a user is reviewing installation instructions
**When** they check system requirements
**Then** they SHALL see macOS-specific prerequisites clearly listed
**And** they SHALL understand that only macOS is currently supported

### Requirement: DOC-002 Installation Instructions Platform Specificity
Installation documentation SHALL include macOS-specific setup instructions and prerequisites.

#### Scenario: Fresh Installation on macOS
**Given** a macOS user is installing cc-api-switcher
**When** they follow the installation instructions
**Then** they SHALL see macOS-specific setup guidance
**And** they SHALL get information about uv tool installation on macOS
**And** they SHALL understand shell compatibility (zsh/bash)

#### Scenario: Package Manager Instructions
**Given** a user is following installation steps
**When** they reach the uv tool installation section
**Then** they SHALL see macOS-compatible package manager guidance
**And** they SHALL understand Homebrew or direct installation options

### Requirement: DOC-003 Troubleshooting Platform Guidance
Troubleshooting documentation SHALL include macOS-specific guidance and known platform issues.

#### Scenario: Common macOS Setup Issues
**Given** a macOS user encounters problems
**When** they consult the troubleshooting section
**Then** they SHALL see macOS-specific solutions
**And** they SHALL find guidance for common macOS path issues
**And** they SHALL get Claude Code macOS availability information

#### Scenario: Permission and Path Issues
**Given** a user experiences permission or path-related errors
**When** they look for troubleshooting help
**Then** they SHALL find macOS-specific permission guidance
**And** they SHALL understand Home Directory structure on macOS
**And** they SHALL get shell environment configuration help

### Requirement: DOC-004 Project Documentation Accuracy
Internal project documentation SHALL accurately reflect the current macOS-only status.

#### Scenario: Developer Reading Project Context
**Given** a developer reviews the project documentation
**When** they check platform constraints in project.md
**Then** they SHALL see accurate macOS-only information
**And** they SHALL understand the rationale for current platform limitations
**And** they SHALL not find outdated cross-platform claims

#### Scenario: Future Platform Planning
**Given** someone is considering cross-platform expansion
**When** they review the project constraints
**Then** they SHALL see clear documentation of current limitations
**And** they SHALL understand what would be needed for cross-platform support
**And** they SHALL have accurate baseline information for planning

