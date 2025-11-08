"""Command-line interface for CC API switcher."""

import difflib
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table

from .config import ProfileStore, SettingsProfile, get_default_target_path
from .core import CcApiSwitcher
from .global_config import GlobalConfig
from .migration import ProfileMigration
from .exceptions import (
    BackupError,
    CcApiSwitcherError,
    InvalidProfileError,
    ProfileNotFoundError,
)

app = typer.Typer(
    name="cc-api-switch",
    help="Switch between API provider settings for Claude Code",
    rich_markup_mode="rich",
)

console = Console()


@app.command("list", rich_help_panel="Commands")
def list_profiles(
    directory: Optional[Path] = typer.Option(
        None,
        "--dir",
        "-d",
        help="Directory containing profile JSON files (overrides global search)",
    ),
) -> None:
    """List all available profiles."""
    try:
        if directory:
            # Backwards compatibility: explicit directory mode
            store = ProfileStore(directory)
            show_source = False
        else:
            # Global mode: hierarchical discovery
            global_config = GlobalConfig()
            store = ProfileStore(global_config=global_config)
            show_source = True

        profiles = store.list_profiles()

        if not profiles:
            console.print("[yellow]No profiles found.[/yellow]")
            if not directory:
                console.print("[dim]Use '[cyan]cc-api-switch init[/cyan]' to set up global configuration[/dim]")
            return

        table = Table(
            title="Available Profiles", show_header=True, header_style="bold cyan"
        )
        table.add_column("Profile", style="green")
        table.add_column("Provider", style="blue")
        if show_source:
            table.add_column("Source", style="magenta")
        table.add_column("Base URL", style="dim")
        table.add_column("Model", style="yellow")

        for profile in profiles:
            base_url = profile.env.get("ANTHROPIC_BASE_URL", "N/A")
            model = profile.env.get("ANTHROPIC_MODEL", "N/A")

            # Shorten URLs for display
            if len(base_url) > 50:
                base_url = base_url[:47] + "..."

            if show_source:
                profile_info = store.get_profile_info(profile.name)
                source = profile_info["source"] if profile_info else "unknown"
                # Color code sources
                source_colors = {
                    "global": "green",
                    "local": "yellow",
                    "env": "blue",
                    "custom": "cyan"
                }
                source_style = source_colors.get(source, "dim")
                source_display = f"[{source_style}]{source}[/{source_style}]"

                table.add_row(
                    profile.name,
                    profile.provider,
                    source_display,
                    base_url,
                    model,
                )
            else:
                table.add_row(
                    profile.name,
                    profile.provider,
                    base_url,
                    model,
                )

        console.print(table)

    except Exception as e:
        console.print(
            Panel(f"[red]Error:[/red] {str(e)}", title="Error", border_style="red")
        )
        raise typer.Exit(1)


@app.command("switch", rich_help_panel="Commands")
def switch_profile(
    name: str = typer.Argument(..., help="Name of profile to switch to"),
    target: Optional[Path] = typer.Option(
        None,
        "--target",
        "-t",
        help="Target path for settings file",
    ),
    directory: Optional[Path] = typer.Option(
        None,
        "--dir",
        "-d",
        help="Directory containing profile JSON files (overrides global search)",
    ),
    backup: bool = typer.Option(
        True,
        "--backup/--no-backup",
        help="Create backup before switching",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed output",
    ),
) -> None:
    """Switch to a profile."""
    try:
        # Initialize global configuration
        global_config = GlobalConfig()

        # Load profile
        if directory:
            # Backwards compatibility: explicit directory mode
            store = ProfileStore(directory)
        else:
            # Global mode: hierarchical discovery
            store = ProfileStore(global_config=global_config)

        try:
            profile = store.get_profile(name)
        except ProfileNotFoundError as e:
            console.print(
                Panel(
                    f"[red]Profile not found:[/red] {name}",
                    title="Error",
                    border_style="red",
                )
            )
            console.print(
                "[dim]Use '[cyan]cc-api-switch list[/cyan]' to see available profiles[/dim]"
            )
            if not directory:
                console.print("[dim]Use '[cyan]cc-api-switch init[/cyan]' to set up global configuration[/dim]")
            raise typer.Exit(1)

        # Use global config for default target if not specified
        if not target:
            target = global_config.get_default_target_path()

        # Show profile info
        switcher = CcApiSwitcher(target_path=target)
        profile_info = switcher.show_profile_info(profile)

        console.print(
            Panel(
                profile_info,
                title=f"Switching to [green]{name}[/green]",
                border_style="blue",
            )
        )

        # Confirm if running interactively
        if backup and sys.stdin.isatty():
            if not Confirm.ask("\n[bold]Create backup of current settings?[/bold]"):
                console.print("[yellow]Skipping backup[/yellow]")
                backup = False

        # Perform switch
        result_path = switcher.switch_to(profile, create_backup=backup)

        if verbose:
            console.print(f"[dim]Target:[/dim] {result_path}")

        console.print(
            f"\n[bold green]✓[/bold green] Switched to [bold cyan]{name}[/bold cyan]"
        )
        console.print(f"[dim]Profile provider:[/dim] {profile.provider}")

    except CcApiSwitcherError as e:
        console.print(
            Panel(
                f"[red]Error:[/red] {str(e)}", title="Switch Failed", border_style="red"
            )
        )
        raise typer.Exit(1)
    except Exception as e:
        console.print(
            Panel(
                f"[red]Unexpected error:[/red] {str(e)}",
                title="Error",
                border_style="red",
            )
        )
        raise typer.Exit(1)


@app.command("show", rich_help_panel="Commands")
def show_current(
    target: Optional[Path] = typer.Option(
        None,
        "--target",
        "-t",
        help="Target path for settings file",
    ),
) -> None:
    """Show the current active profile."""
    try:
        # Use global config for default target if not specified
        global_config = GlobalConfig()
        if not target:
            target = global_config.get_default_target_path()

        switcher = CcApiSwitcher(target_path=target)
        profile = switcher.get_current_profile()

        if not profile:
            console.print(f"[yellow]No settings file found at {target}[/yellow]")
            console.print("[dim]Use '[cyan]cc-api-switch switch[/cyan]' to activate a profile[/dim]")
            return

        profile_info = switcher.show_profile_info(profile)
        console.print(
            Panel(profile_info, title="Current Profile", border_style="green")
        )

    except Exception as e:
        console.print(
            Panel(f"[red]Error:[/red] {str(e)}", title="Error", border_style="red")
        )
        raise typer.Exit(1)


@app.command("validate", rich_help_panel="Commands")
def validate_profile(
    name: str = typer.Argument(..., help="Name of profile to validate"),
    directory: Optional[Path] = typer.Option(
        None,
        "--dir",
        "-d",
        help="Directory containing profile JSON files (overrides global search)",
    ),
) -> None:
    """Validate a profile's configuration."""
    try:
        if directory:
            # Backwards compatibility: explicit directory mode
            store = ProfileStore(directory)
        else:
            # Global mode: hierarchical discovery
            global_config = GlobalConfig()
            store = ProfileStore(global_config=global_config)

        try:
            profile = store.get_profile(name)
        except ProfileNotFoundError:
            console.print(f"[red]Profile '{name}' not found[/red]")
            raise typer.Exit(1)

        issues = profile.validate_profile()

        if not issues:
            console.print(
                f"[bold green]✓[/bold green] Profile '[cyan]{name}[/cyan]' is valid"
            )
        else:
            console.print(
                f"[bold yellow]![/bold yellow] Profile '[cyan]{name}[/cyan]' has [bold]{len(issues)}[/bold] issue(s):"
            )

            for issue in issues:
                console.print(f"  [red]•[/red] {issue}")

    except Exception as e:
        console.print(
            Panel(f"[red]Error:[/red] {str(e)}", title="Error", border_style="red")
        )
        raise typer.Exit(1)


@app.command("backup", rich_help_panel="Commands")
def create_backup(
    target: Optional[Path] = typer.Option(
        None,
        "--target",
        "-t",
        help="Target path for settings file",
    ),
) -> None:
    """Create a manual backup of current settings."""
    try:
        switcher = CcApiSwitcher(target_path=target)

        if not switcher.target_path.exists():
            console.print("[yellow]No settings file found to backup[/yellow]")
            return

        backup_path = switcher._create_backup()

        if backup_path:
            console.print(
                f"[bold green]✓[/bold green] Created backup: [cyan]{backup_path}[/cyan]"
            )
        else:
            console.print("[yellow]No backup created[/yellow]")

    except BackupError as e:
        console.print(
            Panel(
                f"[red]Backup failed:[/red] {str(e)}", title="Error", border_style="red"
            )
        )
        raise typer.Exit(1)
    except Exception as e:
        console.print(
            Panel(f"[red]Error:[/red] {str(e)}", title="Error", border_style="red")
        )
        raise typer.Exit(1)


@app.command("restore", rich_help_panel="Commands")
def restore_from_backup(
    backup_file: Optional[str] = typer.Argument(
        None,
        help="Backup file to restore (use 'list-backups' to see available)",
    ),
    target: Optional[Path] = typer.Option(
        None,
        "--target",
        "-t",
        help="Target path for settings file",
    ),
    list_backups: bool = typer.Option(
        False,
        "--list",
        help="List available backups instead of restoring",
    ),
) -> None:
    """Restore from a backup file."""
    try:
        switcher = CcApiSwitcher(target_path=target)
        backups = switcher.list_backups()

        if list_backups or not backup_file:
            if not backups:
                console.print("[yellow]No backups found[/yellow]")
                return

            table = Table(
                title="Available Backups", show_header=True, header_style="bold cyan"
            )
            table.add_column("Timestamp", style="green")
            table.add_column("File", style="blue")

            for backup in backups:
                # Extract timestamp from filename
                timestamp_str = backup.name.split(".backup.")[-1]
                try:
                    dt = datetime.fromtimestamp(backup.stat().st_mtime)
                    timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    timestamp = timestamp_str

                table.add_row(timestamp, str(backup.name))

            console.print(table)
            return

        if not backup_file:
            console.print("[red]No backup file specified[/red]")
            raise typer.Exit(1)

        # Find backup by name or timestamp
        backup_path = None
        for backup in backups:
            if backup_file in backup.name or backup_file == backup.name:
                backup_path = backup
                break

        if not backup_path:
            console.print(f"[red]Backup '{backup_file}' not found[/red]")
            console.print(
                "[dim]Use 'cc-api-switch restore --list' to see available backups[/dim]"
            )
            raise typer.Exit(1)

        # Confirm restore
        if sys.stdin.isatty():
            if not Confirm.ask(
                f"\n[bold]Restore from backup '{backup_path.name}'?[/bold]"
            ):
                console.print("[yellow]Restore cancelled[/yellow]")
                raise typer.Abort()

        switcher.restore_backup(backup_path)
        console.print(
            f"[bold green]✓[/bold green] Restored from backup: [cyan]{backup_path.name}[/cyan]"
        )

    except BackupError as e:
        console.print(
            Panel(
                f"[red]Restore failed:[/red] {str(e)}",
                title="Error",
                border_style="red",
            )
        )
        raise typer.Exit(1)
    except Exception as e:
        console.print(
            Panel(f"[red]Error:[/red] {str(e)}", title="Error", border_style="red")
        )
        raise typer.Exit(1)


@app.command("diff", rich_help_panel="Commands")
def diff_profiles(
    profile1: str = typer.Argument(..., help="First profile to compare"),
    profile2: str = typer.Argument(..., help="Second profile to compare"),
    directory: Optional[Path] = typer.Option(
        None,
        "--dir",
        "-d",
        help="Directory containing profile JSON files (overrides global search)",
    ),
    env_only: bool = typer.Option(
        True,
        "--env-only/--all",
        help="Compare only environment variables",
    ),
) -> None:
    """Compare two profiles."""
    try:
        if directory:
            # Backwards compatibility: explicit directory mode
            store = ProfileStore(directory)
        else:
            # Global mode: hierarchical discovery
            global_config = GlobalConfig()
            store = ProfileStore(global_config=global_config)

        try:
            p1 = store.get_profile(profile1)
            p2 = store.get_profile(profile2)
        except ProfileNotFoundError as e:
            console.print(f"[red]Profile not found: {e}[/red]")
            raise typer.Exit(1)

        # Get JSON representations
        json1 = p1.to_dict()
        json2 = p2.to_dict()

        if env_only:
            json1 = json1.get("env", {})
            json2 = json2.get("env", {})

        # Create diff
        lines1 = []
        lines2 = []

        if env_only:
            for key in set(json1.keys()) | set(json2.keys()):
                val1 = json1.get(key, "")
                val2 = json2.get(key, "")

                if key in ("ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL"):
                    lines1.append(f"{key} = {val1}")
                    lines2.append(f"{key} = {val2}")
                else:
                    lines1.append(f"{key} = {val1}")
                    lines2.append(f"{key} = {val2}")
        else:
            import json

            lines1 = json.dumps(json1, indent=2).split("\n")
            lines2 = json.dumps(json2, indent=2).split("\n")

        diff_lines = list(
            difflib.unified_diff(
                lines1,
                lines2,
                fromfile=f"{profile1}",
                tofile=f"{profile2}",
                lineterm="",
            )
        )

        if not diff_lines:
            console.print("[bold green]✓[/bold green] Profiles are identical")
            return

        # Display diff
        console.print(
            Panel(
                "\n".join(diff_lines[3:]),  # Skip diff headers
                title=f"Diff: {profile1} → {profile2}",
                border_style="blue",
            )
        )

    except Exception as e:
        console.print(
            Panel(f"[red]Error:[/red] {str(e)}", title="Error", border_style="red")
        )
        raise typer.Exit(1)


@app.command("import", rich_help_panel="Commands")
def import_profile(
    source: Path = typer.Argument(..., help="Source JSON file to import"),
    name: Optional[str] = typer.Option(
        None,
        "--name",
        "-n",
        help="Name for the imported profile",
    ),
    directory: Optional[Path] = typer.Option(
        None,
        "--dir",
        "-d",
        help="Directory to store profiles",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing profile",
    ),
) -> None:
    """Import a profile from a JSON file."""
    try:
        if directory:
            # Backwards compatibility: explicit directory mode
            store = ProfileStore(directory)
        else:
            # Global mode: hierarchical discovery
            global_config = GlobalConfig()
            store = ProfileStore(global_config=global_config)

        # Load and validate
        try:
            profile = SettingsProfile.from_file(source, name=name)
        except (FileNotFoundError, InvalidProfileError) as e:
            console.print(f"[red]Failed to import: {e}[/red]")
            raise typer.Exit(1)

        # Check if profile already exists
        profile_name = profile.name
        existing_profile_file = store.profiles_dir / f"{profile_name}_settings.json"

        if existing_profile_file.exists() and not force:
            console.print(f"[red]Profile '{profile_name}' already exists[/red]")
            console.print("[dim]Use --force to overwrite[/dim]")
            raise typer.Exit(1)

        # Validate profile
        issues = profile.validate_profile()

        if issues:
            console.print("[yellow]Warning: Profile has validation issues:[/yellow]")
            for issue in issues:
                console.print(f"  [red]•[/red] {issue}")

            if sys.stdin.isatty() and not Confirm.ask("\n[bold]Import anyway?[/bold]"):
                console.print("[yellow]Import cancelled[/yellow]")
                raise typer.Abort()

        # Save profile
        store.save_profile(profile)

        console.print(
            f"[bold green]✓[/bold green] Imported profile '[cyan]{profile_name}[/cyan]'"
        )
        console.print(f"[dim]Provider: {profile.provider}[/dim]")

    except Exception as e:
        console.print(
            Panel(f"[red]Error:[/red] {str(e)}", title="Error", border_style="red")
        )
        raise typer.Exit(1)


@app.command("edit", rich_help_panel="Commands")
def edit_profile(
    name: str = typer.Argument(..., help="Name of profile to edit"),
    directory: Optional[Path] = typer.Option(
        None,
        "--dir",
        "-d",
        help="Directory containing profile JSON files (overrides global search)",
    ),
) -> None:
    """Edit a profile using the default editor."""
    try:
        if directory:
            # Backwards compatibility: explicit directory mode
            store = ProfileStore(directory)
        else:
            # Global mode: hierarchical discovery
            global_config = GlobalConfig()
            store = ProfileStore(global_config=global_config)

        try:
            profile = store.get_profile(name)
        except ProfileNotFoundError:
            console.print(f"[red]Profile '{name}' not found[/red]")
            raise typer.Exit(1)

        profile_file = store.profiles_dir / f"{profile.name}_settings.json"

        # Use EDITOR environment variable or default to nano/vim
        import os

        editor = os.environ.get("EDITOR", "nano")
        os.system(f"{editor} {profile_file}")

        # Revalidate after edit
        try:
            updated_profile = SettingsProfile.from_file(profile_file, name=name)
            issues = updated_profile.validate_profile()

            if issues:
                console.print("\n[yellow]Validation issues found after edit:[/yellow]")
                for issue in issues:
                    console.print(f"  [red]•[/red] {issue}")
            else:
                console.print(
                    f"[bold green]✓[/bold green] Profile '[cyan]{name}[/cyan]' updated successfully"
                )

        except InvalidProfileError as e:
            console.print(f"\n[red]Invalid JSON after edit: {e}[/red]")

    except Exception as e:
        console.print(
            Panel(f"[red]Error:[/red] {str(e)}", title="Error", border_style="red")
        )
        raise typer.Exit(1)


# Global Configuration Commands
@app.command("init", rich_help_panel="Configuration")
def init_config() -> None:
    """Initialize global configuration and directories."""
    try:
        global_config = GlobalConfig()

        # Check if already initialized
        if global_config.config_file.exists():
            if not Confirm.ask(
                "[yellow]Global configuration already exists. Reinitialize?[/yellow]"
            ):
                console.print("[dim]Initialization cancelled.[/dim]")
                return

        # Initialize configuration
        global_config.initialize_config()

        console.print(
            Panel(
                f"[bold green]✓[/bold green] Global configuration initialized\n\n"
                f"[dim]Config file:[/dim] {global_config.config_file}\n"
                f"[dim]Profiles dir:[/dim] {global_config.global_profiles_dir}\n"
                f"[dim]Config dir:[/dim] {global_config.config_dir}",
                title="Global Configuration",
                border_style="green",
            )
        )

        console.print(
            "\n[dim]You can now place API profiles in the global profiles directory "
            "and use '[cyan]cc-api-switch list[/cyan]' from anywhere.[/dim]"
        )

    except Exception as e:
        console.print(
            Panel(f"[red]Error:[/red] {str(e)}", title="Initialization Failed", border_style="red")
        )
        raise typer.Exit(1)


@app.command("config", rich_help_panel="Configuration")
def manage_config(
    action: str = typer.Argument(..., help="Action: show, set, get"),
    key: Optional[str] = typer.Argument(None, help="Configuration key"),
    value: Optional[str] = typer.Argument(None, help="Configuration value"),
) -> None:
    """Manage global configuration settings."""
    try:
        global_config = GlobalConfig()

        if not global_config.config_file.exists():
            console.print(
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
            table = Table(title="Global Configuration", show_header=True, header_style="bold cyan")
            table.add_column("Setting", style="green")
            table.add_column("Value", style="blue")

            for key, value in global_config._config.items():
                table.add_row(key, str(value))

            console.print(table)

            # Show current profile search directories
            console.print("\n[bold]Profile Search Order:[/bold]")
            for i, directory in enumerate(global_config.get_profile_directories(), 1):
                source = ""
                if i == 1 and os.environ.get("CC_API_SWITCHER_PROFILE_DIR"):
                    source = " (environment variable)"
                elif i == 1:
                    source = " (global)"
                elif i == len(global_config.get_profile_directories()):
                    source = " (local)"

                console.print(f"  {i}. {directory}{source}")

        elif action == "get":
            if not key:
                console.print("[red]Error:[/red] Missing configuration key")
                raise typer.Exit(1)

            value = global_config.get_config_value(key)
            if value is not None:
                console.print(f"[green]{key}[/green] = [blue]{value}[/blue]")
            else:
                console.print(f"[yellow]Configuration key '{key}' not found[/yellow]")

        elif action == "set":
            if not key or value is None:
                console.print("[red]Error:[/red] Missing configuration key or value")
                raise typer.Exit(1)

            # Parse value as JSON if it looks like a complex type
            try:
                if value.startswith(("[", "{")):
                    import json
                    parsed_value = json.loads(value)
                elif value.lower() in ("true", "false"):
                    parsed_value = value.lower() == "true"
                elif value.isdigit():
                    parsed_value = int(value)
                else:
                    parsed_value = value
            except json.JSONDecodeError:
                parsed_value = value

            global_config.set_config_value(key, parsed_value)
            global_config.save_config()

            console.print(
                f"[bold green]✓[/bold green] Set [green]{key}[/green] = [blue]{parsed_value}[/blue]"
            )

        else:
            console.print(f"[red]Unknown action:[/red] {action}")
            console.print("[dim]Available actions: show, get, set[/dim]")
            raise typer.Exit(1)

    except Exception as e:
        console.print(
            Panel(f"[red]Error:[/red] {str(e)}", title="Configuration Error", border_style="red")
        )
        raise typer.Exit(1)


@app.command("profile-dir", rich_help_panel="Configuration")
def profile_directory() -> None:
    """Show current profile directory search order."""
    try:
        global_config = GlobalConfig()

        console.print("[bold]Profile Directory Search Order:[/bold]\n")

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
                source = " (local directory)"
                exists = True  # Current directory always exists
            else:
                source = ""
                exists = directory.exists()

            status = "[green]✓[/green]" if exists else "[red]✗[/red]"
            source_display = f"{source}" if source else ""

            console.print(f"  {i}. {status} {directory}{source_display}")

        # Show available profiles
        console.print("\n[bold]Available Profiles:[/bold]")
        profiles = global_config.list_available_profiles()

        if not profiles:
            console.print("[dim]No profiles found in any search directory[/dim]")
        else:
            for profile in profiles:
                source_colors = {
                    "global": "green",
                    "local": "yellow",
                    "env": "blue",
                    "custom": "cyan"
                }
                source_style = source_colors.get(profile["source"], "dim")
                console.print(f"  • [green]{profile['name']}[/green] ([{source_style}]{profile['source']}[/{source_style}])")

        # Show environment variables
        console.print("\n[bold]Environment Variables:[/bold]")
        env_vars = {
            "CC_API_SWITCHER_PROFILE_DIR": os.environ.get("CC_API_SWITCHER_PROFILE_DIR", "not set"),
            "XDG_CONFIG_HOME": os.environ.get("XDG_CONFIG_HOME", "not set"),
        }

        for var, value in env_vars.items():
            console.print(f"  • {var}: [dim]{value}[/dim]")

    except Exception as e:
        console.print(
            Panel(f"[red]Error:[/red] {str(e)}", title="Profile Directory Error", border_style="red")
        )
        raise typer.Exit(1)


@app.command("migrate", rich_help_panel="Configuration")
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
        help="Clean up local profiles after migration",
    ),
) -> None:
    """Migrate profiles to global configuration."""
    try:
        global_config = GlobalConfig()
        migration = ProfileMigration(global_config)

        console.print("[bold]Profile Migration Tool[/bold]\n")

        # Ensure global configuration exists
        if not global_config.config_file.exists():
            console.print(
                Panel(
                    "[yellow]Global configuration not found.[/yellow]\n"
                    "Initializing global configuration first...",
                    title="Configuration Setup",
                    border_style="yellow",
                )
            )
            global_config.initialize_config()

        # Perform migration
        migration.migrate_profiles(
            source_dir=source_dir,
            force=force,
            dry_run=dry_run,
        )

        # Cleanup if requested
        if cleanup and not dry_run:
            console.print("\n[bold]Cleaning up local profiles...[/bold]\n")
            migration.cleanup_local_profiles(force=force)

    except Exception as e:
        console.print(
            Panel(f"[red]Error:[/red] {str(e)}", title="Migration Failed", border_style="red")
        )
        raise typer.Exit(1)


def main() -> None:
    """Entry point."""
    app()


if __name__ == "__main__":
    app()
