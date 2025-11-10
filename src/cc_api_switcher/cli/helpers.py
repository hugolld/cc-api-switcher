"""Common helper functions for CLI commands."""

import errno
import os
import re
import sys
from functools import lru_cache
from pathlib import Path
from typing import Optional, Tuple, Any, Union

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table

from ..config import ProfileStore, SettingsProfile, mask_token
from ..global_config import GlobalConfig, GlobalConfigError
from ..exceptions import (
    CcApiSwitcherError,
    ProfileNotFoundError,
    InvalidProfileError,
    BackupError,
    ValidationError,
)


def resolve_store_and_config(directory: Optional[Path] = None) -> Tuple[ProfileStore, Optional[GlobalConfig]]:
    """Resolve ProfileStore and GlobalConfig based on directory parameter.

    This function implements the common pattern used across CLI commands:
    - If directory is provided: use explicit directory mode (legacy)
    - If directory is None: use global configuration mode

    Args:
        directory: Optional explicit directory for profile store

    Returns:
        Tuple of (ProfileStore, Optional[GlobalConfig])

    Raises:
        GlobalConfigError: If global configuration fails to initialize
        ValidationError: If profile store initialization fails
    """
    if directory:
        # Backwards compatibility: explicit directory mode
        store = ProfileStore(directory)
        return store, None
    else:
        # Global mode: use GlobalConfig
        try:
            global_config = GlobalConfig()
            store = ProfileStore(global_config=global_config)
            return store, global_config
        except GlobalConfigError as e:
            raise GlobalConfigError(f"Configuration error: {e}. Run 'cc-api-switch init' to set up configuration")


def resolve_target_path(
    target: Optional[Path] = None,
    global_config: Optional[GlobalConfig] = None
) -> Path:
    """Resolve target path for settings file operations.

    Args:
        target: Optional explicit target path override
        global_config: Optional global configuration for defaults

    Returns:
        Path to the target settings file
    """
    if target:
        return target

    if global_config:
        return global_config.get_default_target_path()

    # Fallback to default location
    return Path.home() / ".claude" / "settings.json"


def handle_cli_error(error: Exception, console: Console, exit_code: int = 1) -> None:
    """Handle CLI errors with consistent presentation and exit.

    Args:
        error: The exception that occurred
        console: Console instance for output
        exit_code: Exit code to use (default: 1)
    """
    if isinstance(error, ProfileNotFoundError):
        console.print(f"[red]Profile not found: {error}[/red]")
        console.print("[dim]Use 'cc-api-switch list' to see available profiles[/dim]")
        raise typer.Exit(exit_code)

    elif isinstance(error, InvalidProfileError):
        console.print(f"[red]Invalid profile: {error}[/red]")
        raise typer.Exit(exit_code)

    elif isinstance(error, BackupError):
        console.print(f"[red]Backup failed: {error}[/red]")
        raise typer.Exit(exit_code)

    elif isinstance(error, ValidationError):
        console.print(f"[red]Validation error: {error}[/red]")
        raise typer.Exit(exit_code)

    elif isinstance(error, GlobalConfigError):
        console.print(f"[red]Configuration error: {error}[/red]")
        console.print("[dim]Run 'cc-api-switch init' to set up configuration[/dim]")
        console.print("[dim]Or use --dir parameter to specify profile directory explicitly[/dim]")
        raise typer.Exit(exit_code)

    elif isinstance(error, (PermissionError, OSError)) and hasattr(error, 'errno') and error.errno == errno.EACCES:
        console.print(f"[red]Permission denied: {error}[/red]")
        raise typer.Exit(exit_code)

    else:
        console.print(
            Panel(f"[red]Unexpected error: {str(error)}[/red]",
                  title="Error", border_style="red")
        )
        raise typer.Exit(exit_code)


def apply_security_policies(command_instance: Any) -> None:
    """Apply security policies to a command instance.

    This function ensures consistent security behavior across all commands.

    Args:
        command_instance: Command instance to apply policies to
    """
    # Ensure console is available
    if not hasattr(command_instance, 'console'):
        command_instance.console = Console()

    # Add any additional security policy enforcement here
    # For example: ensuring secret masking, input validation, etc.


@lru_cache(maxsize=1)
def get_editor_command() -> str:
    """Get the editor command for editing files (cached for performance).

    Returns:
        Editor command string
    """
    import shutil

    # Check common editors in order of preference
    editors = [
        os.environ.get('EDITOR'),  # User's preferred editor
        'code',                     # Visual Studio Code
        'nano',                     # Nano (simple and widely available)
        'vim',                      # Vim
        'vi',                       # Vi
    ]

    for editor in editors:
        if editor and shutil.which(editor):
            return editor

    # Fallback to nano on Unix-like systems
    if sys.platform != "win32" and shutil.which('nano'):
        return 'nano'

    # Fallback to notepad on Windows
    if sys.platform == "win32" and shutil.which('notepad'):
        return 'notepad'

    # Default fallback
    return 'nano'


def format_profile_for_display(
    profile: SettingsProfile,
    show_secrets: bool = False,
    source: Optional[str] = None
) -> dict:
    """Format a profile for display, applying security policies.

    Args:
        profile: Profile to format
        show_secrets: Whether to show unmasked secrets
        source: Optional source information

    Returns:
        Formatted profile dictionary
    """
    profile_dict = profile.to_dict()

    # Apply security: mask secrets unless explicitly requested
    if not show_secrets:
        if 'env' in profile_dict and 'ANTHROPIC_AUTH_TOKEN' in profile_dict['env']:
            profile_dict['env']['ANTHROPIC_AUTH_TOKEN'] = mask_token(
                profile_dict['env']['ANTHROPIC_AUTH_TOKEN']
            )

    # Add source information if provided
    if source:
        profile_dict['_source'] = source

    return profile_dict


@lru_cache(maxsize=1)
def create_profile_table() -> Table:
    """Create and return a cached Rich table for profile display.

    Returns:
        Configured Rich Table instance
    """
    table = Table(title="Available Profiles", show_header=True, header_style="bold cyan")
    table.add_column("Profile", style="green")
    table.add_column("Provider", style="blue")
    table.add_column("Source", style="magenta")
    table.add_column("Base URL", style="dim")
    table.add_column("Model", style="yellow")

    return table


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format (optimized with math operations).

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0B"

    # Use log10 for more efficient size calculation
    import math
    size_names = ["B", "KB", "MB", "GB"]

    # Calculate the power of 1024 using logarithm for efficiency
    i = min(int(math.log(size_bytes, 1024)), len(size_names) - 1)
    size = size_bytes / (1024 ** i)

    return f"{size:.1f}{size_names[i]}"


def ensure_directory_exists(directory: Path) -> None:
    """Ensure a directory exists, creating it if necessary.

    Args:
        directory: Directory path to ensure exists

    Raises:
        PermissionError: If directory cannot be created due to permissions
        OSError: If directory creation fails for other reasons
    """
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except PermissionError as e:
        raise PermissionError(errno.EACCES, f"Permission denied creating directory: {directory}")
    except OSError as e:
        raise OSError(f"Failed to create directory {directory}: {e}")


# Pre-compiled regex pattern for profile name validation
_INVALID_PROFILE_CHARS_PATTERN = re.compile(r'[\/\\:*?"<>|]')

def validate_profile_name(name: str) -> str:
    """Validate and normalize a profile name (optimized with regex).

    Args:
        name: Profile name to validate

    Returns:
        Normalized profile name

    Raises:
        ValidationError: If profile name is invalid
    """
    if not name or not name.strip():
        raise ValidationError("Profile name cannot be empty")

    # Remove whitespace and normalize
    normalized = name.strip()

    # Use pre-compiled regex for faster validation
    if _INVALID_PROFILE_CHARS_PATTERN.search(normalized):
        raise ValidationError("Profile name cannot contain: / \\ : * ? \" < > |")

    # Check length
    if len(normalized) > 50:
        raise ValidationError("Profile name cannot exceed 50 characters")

    return normalized


def get_user_confirmation(
    message: str,
    default: bool = False,
    console: Optional[Console] = None
) -> bool:
    """Get user confirmation with a yes/no prompt (optimized import handling).

    Args:
        message: Confirmation message
        default: Default value if user doesn't respond
        console: Optional console instance

    Returns:
        True if user confirms, False otherwise
    """
    if console is None:
        console = Console()

    return Confirm.ask(message, default=default)