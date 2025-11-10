"""Base classes and shared functionality for CLI commands."""

from pathlib import Path
from typing import Optional, Tuple, Any, Callable
from typing_extensions import ParamSpec

import typer
from rich.console import Console
from rich.panel import Panel

from ..config import ProfileStore
from ..global_config import GlobalConfig, GlobalConfigError
from ..exceptions import (
    CcApiSwitcherError,
    ProfileNotFoundError,
    InvalidProfileError,
    BackupError,
)
from .helpers import resolve_store_and_config, handle_cli_error, apply_security_policies

P = ParamSpec('P')


class BaseCommand:
    """Base class for CLI commands providing shared functionality.

    This class automatically handles:
    - GlobalConfig and ProfileStore resolution
    - Consistent error handling
    - Security policy enforcement
    - Console output management
    """

    def __init__(self, directory: Optional[Path] = None):
        """Initialize the base command.

        Args:
            directory: Optional explicit directory override for profile store
        """
        self.directory = directory
        self.store: Optional[ProfileStore] = None
        self.global_config: Optional[GlobalConfig] = None
        self.console = Console()

        # Resolve store and config on initialization
        self._resolve_infrastructure()

        # Apply security policies
        apply_security_policies(self)

    def _resolve_infrastructure(self) -> None:
        """Resolve ProfileStore and GlobalConfig based on directory parameter."""
        try:
            self.store, self.global_config = resolve_store_and_config(self.directory)
        except GlobalConfigError as e:
            self.handle_error(e, exit_code=1)

    def handle_error(self, error: Exception, exit_code: int = 1) -> None:
        """Handle an error consistently across all commands.

        Args:
            error: The exception that occurred
            exit_code: Exit code to use (default: 1)
        """
        handle_cli_error(error, self.console, exit_code)

    def get_target_path(self, target: Optional[Path] = None) -> Path:
        """Get the target path for settings file operations.

        Args:
            target: Optional explicit target path override

        Returns:
            Path to the target settings file
        """
        if target:
            return target

        if self.global_config:
            return self.global_config.get_default_target_path()

        # Fallback to default location
        return Path.home() / ".claude" / "settings.json"

    def ensure_profile_exists(self, name: str) -> None:
        """Ensure a profile exists, raise appropriate error if not.

        Args:
            name: Profile name to check

        Raises:
            ProfileNotFoundError: If profile doesn't exist
        """
        if not self.store:
            self.handle_error(InvalidProfileError("Profile store not initialized"))
            return

        try:
            self.store.get_profile(name)
        except ProfileNotFoundError:
            self.handle_error(ProfileNotFoundError(f"Profile '{name}' not found"))

    def confirm_action(self, message: str, default: bool = False) -> bool:
        """Prompt user for confirmation.

        Args:
            message: Confirmation message to display
            default: Default value if user doesn't respond

        Returns:
            True if user confirms, False otherwise
        """
        from rich.prompt import Confirm
        return Confirm.ask(message, default=default)

    def success(self, message: str) -> None:
        """Display a success message.

        Args:
            message: Success message to display
        """
        self.console.print(f"[bold green]✓[/bold green] {message}")

    def error(self, message: str, title: str = "Error") -> None:
        """Display an error message.

        Args:
            message: Error message to display
            title: Title for the error panel
        """
        from rich.panel import Panel
        self.console.print(
            Panel(f"[red]{message}[/red]", title=title, border_style="red")
        )

    def info(self, message: str) -> None:
        """Display an info message.

        Args:
            message: Info message to display
        """
        self.console.print(f"[dim]{message}[/dim]")

    def warning(self, message: str) -> None:
        """Display a warning message.

        Args:
            message: Warning message to display
        """
        self.console.print(f"[yellow]{message}[/yellow]")


class CommandContext:
    """Context object for command execution providing shared state."""

    def __init__(
        self,
        directory: Optional[Path] = None,
        global_config: Optional[GlobalConfig] = None,
        store: Optional[ProfileStore] = None,
        console: Optional[Console] = None
    ):
        """Initialize command context.

        Args:
            directory: Optional directory override
            global_config: Optional global configuration
            store: Optional profile store
            console: Optional console instance
        """
        self.directory = directory
        self.global_config = global_config
        self.store = store
        self.console = console or Console()

    def get_or_resolve_store_and_config(self) -> Tuple[ProfileStore, Optional[GlobalConfig]]:
        """Get or resolve store and config from context.

        Returns:
            Tuple of (ProfileStore, Optional[GlobalConfig])
        """
        if self.store and (self.global_config is not None or self.directory is not None):
            return self.store, self.global_config

        return resolve_store_and_config(self.directory)


def with_error_handling(func: Callable[P, Any]) -> Callable[P, Any]:
    """Decorator for automatic error handling in command functions.

    Args:
        func: Function to wrap with error handling

    Returns:
        Wrapped function that handles exceptions consistently
    """
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except CcApiSwitcherError as e:
            console = Console()
            handle_cli_error(e, console, exit_code=1)
        except Exception as e:
            console = Console()
            console.print(
                Panel(f"[red]Unexpected error: {str(e)}[/red]",
                      title="Unexpected Error", border_style="red")
            )
            raise typer.Exit(1)

    return wrapper


class CommandFactory:
    """Factory for creating commands with automatic configuration and security policies.

    This factory provides a way to create new commands that automatically inherit
    the BaseCommand functionality, security policies, and error handling patterns.
    """

    @staticmethod
    def create_command(
        func: Callable[P.args, Any],
        name: Optional[str] = None,
        help_text: Optional[str] = None,
        panel: Optional[str] = None,
        requires_profile: bool = False,
        allow_global_mode: bool = True
    ) -> Callable[P.args, Any]:
        """Create a new command with automatic configuration.

        Args:
            func: The function to wrap as a command
            name: Optional command name (defaults to function name)
            help_text: Optional help text for the command
            panel: Optional help panel for organization
            requires_profile: Whether command requires a profile to exist
            allow_global_mode: Whether command works in global mode

        Returns:
            Wrapped function with all command infrastructure
        """
        @with_error_handling
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
            # Extract directory from kwargs if present
            directory = kwargs.get('directory')

            # Create command instance
            command = BaseCommand(directory)

            # Validate profile requirements
            if requires_profile:
                # This will be implemented by specific commands
                pass

            # Call the original function with command context
            return func(command, *args, **kwargs)

        # Set metadata for typer command registration
        wrapper.__name__ = name or func.__name__
        if help_text:
            wrapper.__doc__ = help_text

        # Store command metadata for potential plugin system
        wrapper._command_metadata = {
            'name': name or func.__name__,
            'help_text': help_text,
            'panel': panel,
            'requires_profile': requires_profile,
            'allow_global_mode': allow_global_mode,
            'original_function': func
        }

        return wrapper

    @staticmethod
    def register_with_app(app: typer.Typer, command_func: Callable) -> None:
        """Register a command created by the factory with a typer app.

        Args:
            app: The typer app to register the command with
            command_func: The command function created by create_command
        """
        metadata = getattr(command_func, '_command_metadata', {})

        # Register with typer using metadata
        app.command(
            name=metadata.get('name'),
            rich_help_panel=metadata.get('panel')
        )(command_func)


def command(
    name: Optional[str] = None,
    help_text: Optional[str] = None,
    panel: Optional[str] = None,
    requires_profile: bool = False,
    allow_global_mode: bool = True
) -> Callable:
    """Decorator for creating commands with automatic infrastructure.

    This decorator provides a simple way to create new commands that automatically
    get BaseCommand functionality, error handling, and security policies.

    Args:
        name: Optional command name
        help_text: Optional help text
        panel: Optional help panel for organization
        requires_profile: Whether command requires an existing profile
        allow_global_mode: Whether command works in global configuration mode

    Returns:
        Decorator function

    Example:
        @command(name="my-command", help_text="My custom command", panel="Custom")
        def my_command_func(command: BaseCommand, profile_name: str):
            command.console.print(f"Processing profile: {profile_name}")
    """
    def decorator(func: Callable) -> Callable:
        return CommandFactory.create_command(
            func=func,
            name=name,
            help_text=help_text,
            panel=panel,
            requires_profile=requires_profile,
            allow_global_mode=allow_global_mode
        )

    return decorator