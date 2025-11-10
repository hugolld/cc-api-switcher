"""Command-line interface for CC API switcher.

This module serves as the entry point for the CLI and imports from the modular
CLI package structure. The actual command implementations are now in:
- cli/commands.py - Core commands (list, switch, show, validate, backup, restore, diff, import, edit)
- cli/config_commands.py - Configuration commands (init, config, profile-dir, migrate)
- cli/app.py - Main typer app initialization
"""

from .cli import app


def main() -> None:
    """Entry point for the CLI application."""
    app()


if __name__ == "__main__":
    main()