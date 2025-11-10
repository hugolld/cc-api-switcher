"""Configuration CLI commands (init, config, profile-dir, migrate)."""

import os
from pathlib import Path
from typing import Optional

import typer
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table

from .base import BaseCommand
from ..global_config import GlobalConfig
from ..migration import ProfileMigration


def init_config() -> None:
    """Initialize global configuration and directories."""
    command = BaseCommand()

    try:
        global_config = GlobalConfig()

        # Check if already initialized
        if global_config.config_file.exists():
            if not command.confirm_action(
                "[yellow]Global configuration already exists. Reinitialize?[/yellow]"
            ):
                command.info("Initialization cancelled.")
                return

        # Initialize configuration
        global_config.initialize_config()

        command.console.print(
            Panel(
                f"[bold green]✓[/bold green] Global configuration initialized\n\n"
                f"[dim]Config file:[/dim] {global_config.config_file}\n"
                f"[dim]Profiles dir:[/dim] {global_config.global_profiles_dir}\n"
                f"[dim]Config dir:[/dim] {global_config.config_dir}",
                title="Global Configuration",
                border_style="green",
            )
        )

        command.info(
            "You can now place API profiles in the global profiles directory "
            "and use '[cyan]cc-api-switch list[/cyan]' from anywhere."
        )

    except Exception as e:
        command.error(str(e), "Initialization Failed")
        raise typer.Exit(1)


def manage_config(
    action: str = typer.Argument(..., help="Action: show, set, get"),
    key: Optional[str] = typer.Argument(None, help="Configuration key"),
    value: Optional[str] = typer.Argument(None, help="Configuration value"),
) -> None:
    """Manage global configuration settings."""
    command = BaseCommand()

    try:
        global_config = GlobalConfig()

        if not global_config.config_file.exists():
            command.console.print(
                Panel(
                    "[red]Global configuration not found[/red]\n"
                    "[dim]Run '[cyan]cc-api-switch init[/cyan]' to create it.[/dim]",
                    title="Configuration Not Found",
                    border_style="red",
                )
            )
            raise typer.Exit(1)

        if action == "show":
            # Show all configuration
            table = Table(title="Global Configuration")
            table.add_column("Setting", style="cyan")
            table.add_column("Value", style="magenta")

            config_data = global_config.get_all_config()
            for k, v in config_data.items():
                table.add_row(k, str(v))

            command.console.print(table)

            # Show current profile search directories
            command.console.print("\n[bold]Profile Search Order:[/bold]")
            profile_dirs = global_config.get_profile_directories()
            for i, directory in enumerate(profile_dirs, 1):
                if i == 1 and os.environ.get("CC_API_SWITCHER_PROFILE_DIR"):
                    source = " (environment variable)"
                elif i == 1 and global_config.get_config_value("default_profile_dir"):
                    source = " (global default)"
                elif i == len(profile_dirs):
                    source = " (current directory)"
                else:
                    source = ""

                exists = directory.exists()
                status = "✓" if exists else "✗"
                command.console.print(f"{i}. {directory}{source} {status}")

        elif action == "get":
            if not key:
                command.error("Key is required for 'get' action")
                raise typer.Exit(1)

            value = global_config.get_config_value(key)
            if value is not None:
                command.console.print(f"{key}: {value}")
            else:
                command.error(f"Configuration key '{key}' not found")
                raise typer.Exit(1)

        elif action == "set":
            if not key or value is None:
                command.error("Key and value are required for 'set' action")
                raise typer.Exit(1)

            global_config.set_config_value(key, value)
            command.success(f"Set {key} = {value}")

        else:
            command.error(f"Unknown action: {action}")
            command.info("Valid actions: show, get, set")
            raise typer.Exit(1)

    except Exception as e:
        command.handle_error(e)


def profile_directory() -> None:
    """Show current profile directory search order."""
    command = BaseCommand()

    try:
        global_config = GlobalConfig()

        command.console.print("[bold]Profile Directory Search Order:[/bold]\n")

        profile_dirs = global_config.get_profile_directories()
        for i, directory in enumerate(profile_dirs, 1):
            # Determine source
            if i == 1 and os.environ.get("CC_API_SWITCHER_PROFILE_DIR"):
                source = " (environment variable)"
                exists = directory.exists()
            elif i == 1 and (
                global_config.get_config_value("default_profile_dir") or
                directory == global_config.global_profiles_dir
            ):
                source = " (global default)"
                exists = directory.exists()
            elif i == len(profile_dirs):
                source = " (current directory)"
                exists = directory.exists()
            else:
                source = ""
                exists = directory.exists()

            status = "✓" if exists else "✗"
            command.console.print(f"{i}. {directory}{source} {status}")

    except Exception as e:
        command.handle_error(e)


def migrate_profiles(
    source_dir: Optional[Path] = typer.Option(
        None,
        "--source",
        "-s",
        help="Source directory containing profiles (auto-discover if not specified)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force overwrite existing profiles",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-n",
        help="Show what would be migrated without doing it",
    ),
    cleanup: bool = typer.Option(
        False,
        "--cleanup",
        "-c",
        help="Remove original profile files after successful migration",
    ),
) -> None:
    """Migrate existing profiles to global configuration."""
    command = BaseCommand()

    try:
        global_config = GlobalConfig()
        migration = ProfileMigration(global_config)

        # Auto-discover source if not specified
        if not source_dir:
            source_dir = migration.auto_discover_source()
            if not source_dir:
                command.warning("No source directory with profiles found.")
                command.info("Specify --source to provide a directory.")
                return

        # Show what will be migrated
        command.console.print(f"[bold]Source directory:[/bold] {source_dir}")
        command.console.print(f"[bold]Target directory:[/bold] {global_config.global_profiles_dir}")

        if not dry_run and not force:
            migration.show_migration_preview(source_dir, global_config.global_profiles_dir)
            if not command.confirm_action("\n[bold]Proceed with migration?[/bold]"):
                command.info("Migration cancelled.")
                return

        # Perform migration
        results = migration.migrate_from_directory(
            source_dir,
            global_config.global_profiles_dir,
            force=force,
            dry_run=dry_run
        )

        if dry_run:
            command.warning("Dry run mode - no files were copied.")
        else:
            command.success(f"Migration completed. {results['migrated']} profiles copied.")
            if results['skipped'] > 0:
                command.warning(f"{results['skipped']} profiles skipped (already exist).")

        # Cleanup original files if requested
        if cleanup and not dry_run and results['migrated'] > 0:
            command.console.print("\n[bold red]Delete original profile files?[/bold red]")
            command.console.print("[dim](This cannot be undone)[/dim]")

            if command.confirm_action("Delete original files?", default=False):
                deleted = migration.cleanup_local_profiles(source_dir)
                command.success(f"Deleted {deleted} original profile files.")

    except Exception as e:
        command.handle_error(e)


def register_config_commands(app: typer.Typer) -> None:
    """Register configuration commands with the typer app.

    Args:
        app: The typer application to register commands with
    """
    app.command("init", rich_help_panel="Configuration")(init_config)
    app.command("config", rich_help_panel="Configuration")(manage_config)
    app.command("profile-dir", rich_help_panel="Configuration")(profile_directory)
    app.command("migrate", rich_help_panel="Configuration")(migrate_profiles)