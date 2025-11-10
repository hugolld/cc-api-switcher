## Context
The `diff` command in `cli.py:481-569` currently displays raw sensitive values when comparing profiles. This creates a security vulnerability where API tokens and base URLs can be exposed in terminal output. The codebase already has a `mask_token` function in `config.py:295-311` that is used by other commands, but the diff command doesn't utilize it.

### Current Vulnerable Implementation
```python
# Lines 530-535 in cli.py - vulnerable code
if key in ("ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL"):
    lines1.append(f"{key} = {val1}")  # ❌ Raw token exposure
    lines2.append(f"{key} = {val2}")  # ❌ Raw token exposure
```

## Goals / Non-Goals
- **Goals**: Prevent secret leakage in diff output, maintain debugging capability, ensure consistent security posture across all CLI commands
- **Non-Goals**: Change the underlying diff algorithm, modify other commands, break existing workflows

## Decisions

### Decision: Mask sensitive fields by default
- **What**: Apply `mask_token()` to `ANTHROPIC_AUTH_TOKEN` and `ANTHROPIC_BASE_URL` in diff output
- **Why**: Aligns with existing security practices in other commands, prevents credential exposure
- **Implementation**: Import `mask_token` from `config.py` and apply before adding to diff lines

### Decision: Add `--show-secrets` opt-out flag
- **What**: Add `show_secrets: bool = typer.Option(False, "--show-secrets", help="Show raw tokens and URLs (insecure)")` parameter
- **Why**: Provides debugging capability when needed, makes security feature explicit
- **Implementation**: Only apply masking when `show_secrets` is False (default)

### Decision: Extend masking to full JSON mode
- **What**: Apply masking in both `--env-only` mode and full JSON diff mode
- **Why**: Prevents secrets from leaking in any diff output format
- **Implementation**: Mask values in JSON representation before creating diff lines

## Risks / Trade-offs
- **Risk**: Users might accidentally use `--show-secrets` in production environments
  - **Mitigation**: Clear help text warning about insecurity, consider adding confirmation prompt
- **Risk**: Masked output might make debugging more difficult
  - **Mitigation**: Provide `--show-secrets` flag with clear documentation
- **Trade-off**: Slightly more complex code in exchange for significantly better security

## Migration Plan
1. Import `mask_token` function from `config.py`
2. Add `show_secrets` parameter to `diff_profiles` function
3. Apply conditional masking in environment-only mode (lines 530-535)
4. Apply conditional masking in full JSON mode (lines 539-540)
5. Add comprehensive tests for both masked and unmasked scenarios
6. Update help text and documentation

## Open Questions
- Should we also mask other potentially sensitive fields (e.g., custom API keys with different names)?
- Should we add a configuration option to permanently disable masking for development environments?
- Should we consider the masking pattern for base URLs (currently `mask_token` is designed for API keys)?