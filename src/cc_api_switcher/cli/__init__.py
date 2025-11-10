"""CLI package for CC API Switcher.

This package provides a modular command-line interface with shared infrastructure
for consistent behavior across all commands.
"""

from .app import app

__all__ = ["app"]