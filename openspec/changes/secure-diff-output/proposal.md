# Change: Secure Diff Output to Prevent Secret Leakage

## Why
The `cc-api-switch diff` command currently prints raw API tokens and base URLs in terminal output, creating a security vulnerability where sensitive credentials can be exposed in terminal logs, shared screenshots, or command histories. This contradicts the project's security posture since other commands properly mask sensitive information.

## What Changes
- Modify the `diff` command to mask `ANTHROPIC_AUTH_TOKEN` and `ANTHROPIC_BASE_URL` values by default using the existing `mask_token` function
- Add an optional `--show-secrets` flag to bypass masking for debugging purposes
- Apply consistent masking rules for both environment-only and full JSON diff modes
- Ensure the masking behavior matches other commands in the CLI

## Impact
- **Affected specs**: security (adds new requirements for diff output security)
- **Affected code**: `src/cc_api_switcher/cli.py:481-569` (diff command implementation)
- **Breaking change**: No - default behavior becomes more secure, with opt-out for debugging
- **Security improvement**: Prevents accidental credential exposure in terminal output