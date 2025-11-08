# Security Requirements for API Key Handling

## ADDED Requirements

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