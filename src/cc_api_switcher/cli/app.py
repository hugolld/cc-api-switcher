"""Main typer app initialization and command registration."""

import typer
from rich.console import Console

# Import command functions directly
from .config_commands import (
    init_config,
    manage_config,
    profile_directory,
    migrate_profiles,
)
from .commands import (
    list_profiles,
    switch_profile,
    show_current,
    validate_profile,
    create_backup,
    restore_from_backup,
    diff_profiles,
    import_profile,
    edit_profile,
)

# Create the main typer app
app = typer.Typer(
    name="cc-api-switch",
    help="Switch between API provider settings for Claude Code",
    rich_markup_mode="rich",
    no_args_is_help=True,
)

# Global console instance for consistent output
console = Console()

# Register configuration commands
app.command("init", rich_help_panel="Configuration")(init_config)
app.command("config", rich_help_panel="Configuration")(manage_config)
app.command("profile-dir", rich_help_panel="Configuration")(profile_directory)
app.command("migrate", rich_help_panel="Configuration")(migrate_profiles)

# Register core commands
app.command("list", rich_help_panel="Commands")(list_profiles)
app.command("switch", rich_help_panel="Commands")(switch_profile)
app.command("show", rich_help_panel="Commands")(show_current)
app.command("validate", rich_help_panel="Commands")(validate_profile)
app.command("backup", rich_help_panel="Commands")(create_backup)
app.command("restore", rich_help_panel="Commands")(restore_from_backup)
app.command("diff", rich_help_panel="Commands")(diff_profiles)
app.command("import", rich_help_panel="Commands")(import_profile)
app.command("edit", rich_help_panel="Commands")(edit_profile)


def get_app() -> typer.Typer:
    """Get the main typer app instance.

    Returns:
        The configured typer application
    """
    return app


def get_console() -> Console:
    """Get the global console instance.

    Returns:
        The console instance for CLI output
    """
    return console