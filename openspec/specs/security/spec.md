# Security Specification

## Purpose
This specification defines security requirements for handling API keys and authentication tokens in the CC API Switcher project to prevent credential exposure and maintain security best practices.
## Requirements
### Requirement: SEC-001 API Key Placeholder Standardization
All example API keys in documentation and configuration files SHALL use secure placeholder tokens instead of real credentials.

#### Scenario: Provider API Configuration Examples
**Given** a developer needs to configure an API provider
**When** they reference example configuration files
**Then** they should see safe placeholder tokens like `sk-[provider]-example-placeholder`
**And** they should understand these are examples, not real credentials

#### Scenario: README Documentation Examples
**Given** a user reading the project README
**When** they see API configuration examples
**Then** all API keys should be clearly marked as placeholders
**And** the format should be consistent across all examples

### Requirement: SEC-002 Real Credential Prevention
The codebase SHALL NOT contain any real API keys or authentication tokens.

#### Scenario: Security Scanning
**Given** the codebase is scanned for security vulnerabilities
**When** searching for patterns like `sk-` followed by alphanumeric characters
**Then** only placeholder tokens should be found
**And** no real authentication credentials should exist

### Requirement: SEC-003 Secure Documentation Practices
Documentation SHALL clearly distinguish between example configurations and real usage instructions.

#### Scenario: User Onboarding
**Given** a new user setting up the tool
**When** following documentation examples
**Then** they should understand they need to use their own API keys
**And** they should know where to obtain real credentials from providers

### Requirement: SEC-004 Configuration Examples Security
All configuration examples SHALL use secure placeholder tokens.

#### Scenario: Profile Configuration Template
**Given** a user creating a new profile configuration
**When** they look at example JSON configurations
**Then** they should see placeholder tokens like:
```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
    "ANTHROPIC_AUTH_TOKEN": "sk-deepseek-example-placeholder",
    "API_TIMEOUT_MS": "600000",
    "ANTHROPIC_MODEL": "deepseek-chat"
  }
}
```

#### Scenario: Provider API Examples
**Given** a developer setting up provider-specific functions
**When** they reference shell configuration examples
**Then** they should see placeholder tokens like:
```bash
export ANTHROPIC_AUTH_TOKEN=sk-kimi-example-placeholder
export ANTHROPIC_BASE_URL=https://api.kimi.com/coding/
```

### Requirement: SEC-005 Secure Diff Output
The `diff` command SHALL mask sensitive values by default to prevent credential exposure in terminal output.

#### Scenario: Environment variables diff masking
**Given** two profiles with different `ANTHROPIC_AUTH_TOKEN` and `ANTHROPIC_BASE_URL` values
**When** a user runs `cc-api-switch diff profile1 profile2`
**THEN** the output SHALL show masked tokens (e.g., `sk-abcd****efgh`) instead of raw values
**AND** base URLs SHALL be partially masked to prevent full credential exposure

#### Scenario: Full JSON diff masking
**Given** two profiles with different configurations including sensitive data
**When** a user runs `cc-api-switch diff profile1 profile2 --all`
**THEN** the JSON diff output SHALL mask `ANTHROPIC_AUTH_TOKEN` and `ANTHROPIC_BASE_URL` values
**AND** all other non-sensitive fields SHALL be displayed normally

#### Scenario: Debugging with explicit flag
**Given** a developer needs to debug profile differences with actual values
**When** they run `cc-api-switch diff profile1 profile2 --show-secrets`
**THEN** the output SHALL display raw, unmasked sensitive values
**AND** a clear warning SHALL be displayed about insecure output

### Requirement: SEC-006 Consistent Token Masking
All CLI commands SHALL use consistent masking behavior for sensitive values.

#### Scenario: Consistent masking across commands
**Given** the `mask_token` function exists in `config.py`
**When** any CLI command displays potentially sensitive values
**THEN** the same masking algorithm SHALL be applied
**AND** users SHALL see consistent masked formats across `list`, `diff`, and other commands

#### Scenario: Masking format validation
**Given** the `mask_token` function with established behavior
**When** applied to API tokens of various lengths
**THEN** tokens SHALL be masked consistently: first 4 chars + asterisks + last 4 chars
**AND** tokens shorter than 8 characters SHALL be fully masked
**AND** the format SHALL match the existing implementation in other commands

