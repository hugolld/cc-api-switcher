# Project Context

## Purpose
CC API Switcher is a Python CLI tool for managing and switching between different API provider configurations for Claude Code. The project aims to provide developers with a secure, reliable way to manage multiple Claude API provider settings (DeepSeek, GLM, MiniMax, Qwen) with automatic backup, validation, and atomic switching operations.

### Key Goals
- **Security**: Secure handling of API tokens with masking and file permissions
- **Reliability**: Atomic file operations with automatic backup and restore
- **Usability**: Rich CLI interface with clear error messages and validation
- **Extensibility**: Support for multiple API providers with auto-detection
- **Developer Experience**: Comprehensive testing and type safety

## Tech Stack

### Core Technologies
- **Python 3.8+**: Primary language with broad compatibility
- **Typer**: Modern CLI framework with rich type hints and auto-completion
- **Pydantic**: Data validation and serialization with strong typing
- **Rich**: Beautiful terminal output with tables, colors, and progress indicators

### Development Tools
- **UV**: Fast Python package manager and build tool
- **pytest**: Testing framework with coverage reporting
- **ruff**: High-performance Python linter and formatter
- **mypy**: Static type checking
- **hatchling**: Build backend

### Key Dependencies
- `typer[all]>=0.9.0`: CLI framework with rich features
- `pydantic>=2.0.0`: Data validation and settings management
- `rich>=13.0.0`: Terminal formatting and display

## Project Conventions

### Code Style
- **Line Length**: 88 characters (ruff default)
- **Formatting**: ruff format for consistent code style
- **Linting**: ruff check with rules E, F, W, UP, B, I, N, C90
- **Ignored Rules**: E501 (line length), B904 (raise in except), B008 (function calls in defaults), C901 (complex function)
- **Type Hints**: Optional but encouraged, especially for public APIs
- **Documentation**: Comprehensive docstrings for all public functions

### Architecture Patterns

#### Layered Architecture
```
cli.py (CLI layer) → core.py (business logic) → config.py (data models) → exceptions.py (error handling)
```

#### Key Patterns
- **Repository Pattern**: `ProfileStore` manages profile file operations
- **Strategy Pattern**: Provider detection based on URL patterns
- **Command Pattern**: CLI commands mapped to core operations
- **Decorator Pattern**: Rich formatting and error handling

#### Core Components
- **cli.py**: Typer-based CLI with 8 main commands (list, switch, show, validate, backup, restore, diff, import, edit)
- **config.py**: Pydantic models for profile validation and provider detection
- **core.py**: Business logic for atomic switching and backup operations
- **exceptions.py**: Custom exception hierarchy with 5 specific exception types

### Testing Strategy

#### Test Architecture
- **Framework**: pytest with fixtures and parameterized tests
- **Coverage**: Target 90%+ coverage with HTML reports
- **Test Types**:
  - Unit tests for individual components
  - Integration tests for CLI workflows
  - Error handling tests for all exception paths
  - File operation tests with temp directories

#### Test Organization
- **test_cli.py**: 13 tests for CLI commands using CliRunner
- **test_config.py**: 17 tests for profile validation and data models
- **test_core.py**: 12 tests for core switching and backup logic
- **Total**: 42 comprehensive test functions

#### Testing Patterns
- Use `tmp_path` fixture for isolated file operations
- Mock external dependencies with `pytest-mock`
- Test all error conditions and edge cases
- Use parameterized tests for multiple input scenarios

### Git Workflow
- **Not Git-initialized**: Currently not under version control
- **Recommended Strategy**: Feature-branch workflow with main trunk
- **Commit Convention**: Conventional Commits format (feat:, fix:, docs:, etc.)
- **Branch Naming**: feature/description, fix/description, docs/description
- **PR Process**: Code review required with automated test passing

## Domain Context

### API Provider Landscape
The tool operates in the Claude API ecosystem where multiple providers offer Anthropic-compatible APIs:

#### Supported Providers
- **DeepSeek**: `api.deepseek.com` - Chinese AI provider with competitive pricing
- **GLM**: `open.bigmodel.cn` - Zhipu AI's large language model platform
- **MiniMax**: `api.minimaxi.com` - Chinese AI company with multiple model offerings
- **Qwen**: `dashscope.aliyuncs.com` - Alibaba Cloud's Tongyi Qianwen models

#### Claude Code Configuration
- **Target File**: `~/.claude/settings.json` (configurable)
- **Required Fields**: `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN`
- **Optional Fields**: Model settings, timeouts, plugins, status line configuration

### Security Considerations
- **API Tokens**: Highly sensitive credentials requiring secure handling
- **File Permissions**: Settings files set to 0o600 (owner read/write only)
- **Token Masking**: Display only first/last 4 characters in output
- **Path Validation**: Prevent directory traversal attacks
- **Backup Security**: Encrypted storage of configuration history

## Important Constraints

### Technical Constraints
- **Python Version**: Minimum 3.8, maximum tested on 3.12
- **Platform**: macOS-only (currently) - designed and tested exclusively on macOS 12.0+
- **File System**: Requires read/write access to user home directory (`~/.claude/`, `~/.config/`)
- **Dependencies**: Minimal external dependencies for security

### Platform Constraints
- **Claude Code Availability**: Claude Code is primarily available and developed for macOS
- **Testing Environment**: All current testing and validation performed on macOS systems
- **Path Assumptions**: Tool assumes macOS filesystem structure and shell environment
- **Future Expansion**: Cross-platform support may be considered but not currently planned

### Security Constraints
- **No Network Calls**: Tool never makes HTTP requests to API providers
- **Token Protection**: API tokens never logged or exposed in error messages
- **Atomic Operations**: File operations must be atomic to prevent corruption
- **Path Isolation**: All file operations restricted to safe directories

### Performance Constraints
- **Fast Startup**: CLI commands should complete in <500ms for local operations
- **Memory Usage**: Minimal memory footprint for large profile collections
- **Backup Limits**: Maximum 10 automatic backups with automatic cleanup
- **File Size**: Profile files should be <1MB for practical usage

### Usability Constraints
- **CLI-First**: Design optimized for terminal usage, not GUI
- **Error Clarity**: All error messages must provide actionable guidance
- **Backward Compatibility**: Must support existing Claude Code settings format
- **Graceful Degradation**: Function with missing optional configuration

## External Dependencies

### Runtime Dependencies
- **typer[all]**: CLI framework - BSD-3-Clause license
- **pydantic**: Data validation - MIT license
- **rich**: Terminal formatting - MIT license

### Development Dependencies
- **pytest**: Testing framework - MIT license
- **pytest-cov**: Coverage reporting - MIT license
- **pytest-mock**: Mocking utilities - MIT license
- **ruff**: Linting and formatting - MIT license
- **mypy**: Type checking - MIT license
- **hatchling**: Build backend - MIT license

### External Systems
- **Claude Code**: Target application for settings management
- **API Providers**: External services (DeepSeek, GLM, MiniMax, Qwen) - tool does not directly communicate with them
- **File System**: Local filesystem for profile storage and backup management
- **Shell Environment**: Environment variable access for configuration discovery
