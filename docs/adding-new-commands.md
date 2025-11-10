# Guide: Adding New Commands to CC API Switcher

This guide provides patterns and best practices for adding new commands to the modular CLI architecture.

## Quick Start: Using the Command Decorator

The simplest way to add a new command is using the `@command` decorator:

```python
from cc_api_switcher.cli.base import command

@command(
    name="my-command",
    help_text="Description of what this command does",
    panel="Custom Commands",
    requires_profile=True
)
def my_command_function(command: BaseCommand, profile_name: str) -> None:
    """My custom command implementation."""
    # Check if profile exists
    command.ensure_profile_exists(profile_name)

    # Your command logic here
    command.console.print(f"Processing profile: {profile_name}")
```

## Command Organization Patterns

### 1. Core Commands (commands.py)
For functionality that manipulates profiles or settings:

```python
def example_core_command(
    directory: Optional[Path] = typer.Option(None, "--dir", help="Profile directory"),
    # Add other parameters as needed
) -> None:
    """Example core command implementation."""
    # Resolve infrastructure
    store, global_config = resolve_store_and_config(directory)
    console = Console()

    try:
        # Your command logic
        pass
    except Exception as e:
        handle_cli_error(e, console)
```

### 2. Configuration Commands (config_commands.py)
For setup and management commands:

```python
def example_config_command(
    # Add parameters
) -> None:
    """Example configuration command implementation."""
    # Similar pattern with appropriate error handling
    pass
```

### 3. Custom Command Groups
Create new modules for specialized functionality:

```python
# src/cc_api_switcher/cli/custom_commands.py
from typing import Optional
from pathlib import Path
import typer
from rich.console import Console

from ..config import ProfileStore
from ..global_config import GlobalConfig
from .base import BaseCommand, with_error_handling
from .helpers import resolve_store_and_config, handle_cli_error

@with_error_handling
def custom_command(
    directory: Optional[Path] = typer.Option(None, "--dir", help="Profile directory"),
) -> None:
    """Custom command implementation."""
    store, global_config = resolve_store_and_config(directory)
    console = Console()

    # Command implementation
    console.print("Custom command executed successfully")
```

## Error Handling Patterns

### Using BaseCommand
```python
def my_command(command: BaseCommand) -> None:
    try:
        # Your logic
        pass
    except ProfileNotFoundError as e:
        command.handle_error(e)
```

### Using Decorator
```python
@with_error_handling
def my_command() -> None:
    # Automatic error handling
    pass
```

### Manual Error Handling
```python
def my_command() -> None:
    try:
        # Your logic
        pass
    except Exception as e:
        console = Console()
        handle_cli_error(e, console)
```

## Security Considerations

### Automatic Security Policies
All commands automatically get:
- Secret masking for sensitive data
- Input validation
- Permission checks

### Custom Security
```python
def secure_command(command: BaseCommand) -> None:
    # Additional security checks
    if not command._validate_user_input():
        command.console.print("[red]Invalid input[/red]")
        raise typer.Exit(1)
```

## Global Mode Support

### Respecting Global Configuration
```python
def my_command(directory: Optional[Path] = None) -> None:
    store, global_config = resolve_store_and_config(directory)

    if global_config:
        # Use global config defaults
        target_path = global_config.get_default_target_path()
    else:
        # Use explicit directory
        target_path = directory / "settings.json"
```

### Testing Global Mode
```python
def test_my_command_global_mode():
    with tempfile.TemporaryDirectory() as temp_dir:
        os.environ['XDG_CONFIG_HOME'] = temp_dir
        # Test command in global mode
```

## Testing Patterns

### Unit Testing Commands
```python
def test_my_command():
    """Test my command functionality."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Setup test environment
        store = ProfileStore(Path(temp_dir))

        # Test command
        # ... test implementation
```

### Testing Error Conditions
```python
def test_my_command_error_handling():
    """Test error handling in my command."""
    with pytest.raises(ProfileNotFoundError):
        # Trigger error condition
        pass
```

## Registering Commands

### Manual Registration
```python
# In app.py
from .custom_commands import custom_command

app.command("custom", rich_help_panel="Custom")(custom_command)
```

### Factory Registration
```python
# Using CommandFactory
from .base import CommandFactory

custom_cmd = CommandFactory.create_command(
    func=custom_command_func,
    name="custom",
    help_text="Custom command",
    panel="Custom"
)

CommandFactory.register_with_app(app, custom_cmd)
```

## Best Practices

### 1. Use Helper Functions
```python
from .helpers import (
    resolve_store_and_config,
    handle_cli_error,
    format_profile_for_display,
    create_profile_table
)
```

### 2. Consistent Parameter Patterns
```python
def standard_command(
    directory: Optional[Path] = typer.Option(None, "--dir", help="Profile directory"),
    verbose: bool = typer.Option(False, "--verbose", help="Verbose output")
) -> None:
    """Standard command with common parameters."""
    pass
```

### 3. Rich Output
```python
def rich_command(command: BaseCommand) -> None:
    # Use rich formatting
    command.console.print("[green]Success![/green]")

    # Use tables for structured data
    table = create_profile_table()
    command.console.print(table)
```

### 4. Input Validation
```python
def validated_command(profile_name: str) -> None:
    # Validate profile name
    from .helpers import validate_profile_name
    validated_name = validate_profile_name(profile_name)

    # Continue with validated input
```

## Plugin Architecture (Future)

The command factory pattern supports future plugin development:

```python
# Potential plugin interface
class CommandPlugin:
    def get_commands(self) -> List[Callable]:
        """Return list of commands provided by this plugin."""
        pass

    def get_metadata(self) -> dict:
        """Return plugin metadata."""
        pass
```

## Migration from Legacy Commands

If converting legacy commands:

1. **Extract Logic**: Move core logic to function
2. **Add Error Handling**: Use BaseCommand or decorators
3. **Use Helpers**: Replace repeated patterns with helper functions
4. **Add Tests**: Ensure comprehensive test coverage
5. **Update Documentation**: Update help text and documentation

## Example: Complete Command Implementation

```python
# src/cc_api_switcher/cli/commands.py

@with_error_handling
def check_profile(
    profile_name: str = typer.Argument(..., help="Profile name to check"),
    directory: Optional[Path] = typer.Option(None, "--dir", help="Profile directory"),
    verbose: bool = typer.Option(False, "--verbose", help="Verbose output")
) -> None:
    """Check a profile's configuration and connectivity."""
    store, global_config = resolve_store_and_config(directory)
    console = Console()

    # Validate profile exists
    command = BaseCommand(directory)
    command.ensure_profile_exists(profile_name)

    # Get profile
    profile = store.get_profile(profile_name)

    if verbose:
        console.print(f"[dim]Checking profile: {profile_name}[/dim]")
        console.print(f"[dim]Provider: {profile.provider}[/dim]")

    # Perform check logic
    console.print(f"[green]✓[/green] Profile '{profile_name}' is valid")
```

This guide provides the patterns and examples needed to successfully add new commands while maintaining consistency with the modular CLI architecture.