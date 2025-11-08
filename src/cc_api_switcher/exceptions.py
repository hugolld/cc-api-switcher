"""Custom exceptions for the CC API switcher."""


class CcApiSwitcherError(Exception):
    """Base exception for CC API switcher."""

    pass


class ProfileNotFoundError(CcApiSwitcherError):
    """Raised when a profile is not found."""

    pass


class InvalidProfileError(CcApiSwitcherError):
    """Raised when a profile is invalid."""

    pass


class BackupError(CcApiSwitcherError):
    """Raised when backup/restore fails."""

    pass


class ValidationError(CcApiSwitcherError):
    """Raised when profile validation fails."""

    pass
