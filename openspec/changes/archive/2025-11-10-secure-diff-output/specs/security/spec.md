## ADDED Requirements

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