## ADDED Requirements

### Requirement: Kimi Provider Auto-Detection
The system SHALL automatically detect Kimi (Moonshot AI) as the provider when profiles contain `api.kimi.com` in the ANTHROPIC_BASE_URL.

#### Scenario: Auto-detect Kimi provider
- **WHEN** a profile contains `ANTHROPIC_BASE_URL` with `api.kimi.com`
- **THEN** the system identifies the provider as "kimi"
- **AND** displays this provider name in CLI output and tables

#### Scenario: Provider detection consistency
- **WHEN** loading or validating the Kimi profile
- **THEN** the provider detection matches the expected "kimi" identifier
- **AND** maintains consistency with existing provider detection patterns