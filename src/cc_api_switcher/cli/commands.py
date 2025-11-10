"""Core CLI commands (list, switch, show, validate, backup, restore, diff, import, edit)."""

from pathlib import Path
from typing import Optional

import typer
from rich.table import Table
from rich.panel import Panel

from .base import BaseCommand
from .helpers import format_profile_for_display


def list_profiles(
    directory: Optional[Path] = typer.Option(
        None,
        "--dir",
        "-d",
        help="Directory containing profile JSON files (overrides global search)",
    ),
) -> None:
    """List all available profiles.

    Args:
        directory: Optional directory containing profile JSON files
    """
    command = BaseCommand(directory)

    try:
        profiles = command.store.list_profiles()

        if not profiles:
            command.warning("No profiles found.")
            if not directory:
                command.info("Use '[cyan]cc-api-switch init[/cyan]' to set up global configuration")
            return

        # Determine if we should show source column
        show_source = command.global_config is not None

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
                profile_info = command.store.get_profile_info(profile.name)
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

        command.console.print(table)

    except Exception as e:
        command.handle_error(e)


def switch_profile(
    name: str = typer.Argument(..., help="Name of profile to switch to"),
    target: Optional[Path] = typer.Option(
        None,
        "--target",
        "-t",
        help="Target path for settings file (overrides global configuration)",
    ),
    directory: Optional[Path] = typer.Option(
        None,
        "--dir",
        "-d",
        help="Directory containing profile JSON files (overrides global search)",
    ),
    backup: Optional[bool] = typer.Option(
        None,
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
    """Switch to a specific profile.

    Args:
        name: Name of profile to switch to
        target: Optional target path for settings file
        directory: Optional directory containing profile JSON files
        backup: Whether to create backup before switching
        verbose: Whether to show detailed output
    """
    command = BaseCommand(directory)

    try:
        # Ensure profile exists
        command.ensure_profile_exists(name)
        profile = command.store.get_profile(name)

        # Determine target path
        target_path = command.get_target_path(target)

        # Show what will be switched
        command.console.print(
            Panel(
                f"[bold]Profile:[/bold] {name}\n"
                f"[bold]Provider:[/bold] {profile.provider}\n"
                f"[bold]Target:[/bold] {target_path}",
                title=f"Switching to [green]{name}[/green]",
                border_style="blue",
            )
        )

        # Confirm if running interactively
        import sys
        if backup is None:  # If not specified by user
            backup = True  # Default to True for backwards compatibility

        if backup and sys.stdin.isatty():
            if not command.confirm_action("\n[bold]Create backup of current settings?[/bold]", default=True):
                backup = False

        # Create switcher and perform switch
        from ..core import CcApiSwitcher
        switcher = CcApiSwitcher(target_path=target_path)

        result = switcher.switch_to(profile, create_backup=backup)
        command.success(f"Switched to [bold cyan]{name}[/bold cyan]")

        if verbose:
            command.info(f"Target: {target_path}")
        command.info(f"Profile provider: {profile.provider}")

        if result:
            command.info(f"Settings saved to: {result}")

    except Exception as e:
        command.handle_error(e)


def show_current(
    target: Optional[Path] = typer.Option(
        None,
        "--target",
        "-t",
        help="Target settings file (default: ~/.claude/settings.json)",
    ),
) -> None:
    """Show the current active profile."""
    command = BaseCommand()

    try:
        target_path = command.get_target_path(target)

        from ..core import CcApiSwitcher
        switcher = CcApiSwitcher(target_path=target_path)

        profile = switcher.get_current_profile()

        if not profile:
            command.warning(f"No settings file found at {target_path}")
            command.info("Use '[cyan]cc-api-switch switch[/cyan]' to activate a profile")
            return

        # Format profile for display (with secrets masked)
        profile_data = format_profile_for_display(profile, show_secrets=False)

        # Build profile info string
        info_lines = []
        info_lines.append(f"[bold]Profile:[/bold] {profile.name}")
        info_lines.append(f"[bold]Provider:[/bold] {profile.provider}")

        if "env" in profile_data:
            env = profile_data["env"]
            if "ANTHROPIC_BASE_URL" in env:
                info_lines.append(f"[bold]Base URL:[/bold] {env['ANTHROPIC_BASE_URL']}")
            if "ANTHROPIC_MODEL" in env:
                info_lines.append(f"[bold]Model:[/bold] {env['ANTHROPIC_MODEL']}")

        profile_info = "\n".join(info_lines)

        command.console.print(
            Panel(profile_info, title="Current Profile", border_style="green")
        )

    except Exception as e:
        command.handle_error(e)


def validate_profile(
    name: str = typer.Argument(..., help="Name of profile to validate"),
    directory: Optional[Path] = typer.Option(
        None,
        "--dir",
        "-d",
        help="Directory containing profile JSON files (overrides global search)",
    ),
) -> None:
    """Validate a specific profile."""
    command = BaseCommand(directory)

    try:
        # Ensure profile exists
        command.ensure_profile_exists(name)
        profile = command.store.get_profile(name)

        # Get validation issues
        issues = profile.validate_profile()

        if not issues:
            command.success(f"Profile '[cyan]{name}[/cyan]' is valid")
        else:
            command.warning(f"Profile '[cyan]{name}[/cyan]' has [bold]{len(issues)}[/bold] issue(s):")
            for issue in issues:
                command.error(f"  • {issue}")

    except Exception as e:
        command.handle_error(e)


def create_backup(
    target: Optional[Path] = typer.Option(
        None,
        "--target",
        "-t",
        help="Target path for settings file (overrides global configuration)",
    ),
) -> None:
    """Create a manual backup of current settings."""
    command = BaseCommand()

    try:
        target_path = command.get_target_path(target)

        from ..core import CcApiSwitcher
        switcher = CcApiSwitcher(target_path=target_path)

        # Check if settings file exists
        if not target_path.exists():
            command.warning("No settings file found to backup")
            return

        backup_path = switcher.create_backup()
        command.success(f"Created backup: [cyan]{backup_path}[/cyan]")

    except Exception as e:
        command.handle_error(e)


def restore_from_backup(
    backup_file: Optional[str] = typer.Argument(
        None,
        help="Backup file to restore (use --list to see available)",
    ),
    target: Optional[Path] = typer.Option(
        None,
        "--target",
        "-t",
        help="Target path for settings file (overrides global configuration)",
    ),
    list_backups: bool = typer.Option(
        False,
        "--list",
        help="List available backups instead of restoring",
    ),
) -> None:
    """Restore from a backup file."""
    command = BaseCommand()

    try:
        target_path = command.get_target_path(target)

        from ..core import CcApiSwitcher
        switcher = CcApiSwitcher(target_path=target_path)

        if list_backups:
            backups = switcher.list_backups()

            if not backups:
                command.warning("No backups found")
                return

            table = Table(title="Available Backups")
            table.add_column("File", style="cyan")
            table.add_column("Date", style="green")
            table.add_column("Size", style="yellow")

            for backup in backups:
                backup_path = Path(backup)
                stat = backup_path.stat()
                from .helpers import format_file_size
                size = format_file_size(stat.st_size)
                import datetime
                date = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")

                table.add_row(backup_path.name, date, size)

            command.console.print(table)
        else:
            if not backup_file:
                command.error("No backup file specified")
                command.info("Use --list to see available backups")
                raise typer.Exit(1)

            # Restore from backup
            success = switcher.restore_from_backup(backup_file)
            if success:
                command.success(f"Restored from backup: [cyan]{backup_file}[/cyan]")
            else:
                command.error(f"Failed to restore from backup: {backup_file}")

    except Exception as e:
        command.handle_error(e)


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
    show_secrets: bool = typer.Option(
        False,
        "--show-secrets",
        help="[WARNING] Show raw tokens and URLs in output (insecure - for debugging only)",
    ),
) -> None:
    """Compare two profiles."""
    command = BaseCommand(directory)

    try:
        # Ensure profiles exist
        command.ensure_profile_exists(profile1)
        command.ensure_profile_exists(profile2)

        profile_data1 = command.store.get_profile(profile1)
        profile_data2 = command.store.get_profile(profile2)

        if show_secrets:
            command.warning(
                "[bold red]WARNING:[/bold red] Displaying secrets in output. "
                "Use with caution in secure environments."
            )

        # Format profiles for comparison
        if env_only:
            data1 = {"env": profile_data1.env}
            data2 = {"env": profile_data2.env}
        else:
            data1 = format_profile_for_display(profile_data1, show_secrets=True)
            data2 = format_profile_for_display(profile_data2, show_secrets=True)

        # Perform comparison
        import json
        import difflib

        str1 = json.dumps(data1, indent=2, sort_keys=True)
        str2 = json.dumps(data2, indent=2, sort_keys=True)

        if str1 == str2:
            command.success("Profiles are identical")
        else:
            diff = difflib.unified_diff(
                str1.splitlines(keepends=True),
                str2.splitlines(keepends=True),
                fromfile=f"{profile1} (current)",
                tofile=f"{profile2} (comparison)",
                lineterm=""
            )

            command.console.print("\n".join(diff))

    except Exception as e:
        command.handle_error(e)


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
    command = BaseCommand(directory)

    try:
        # Read source file
        if not source.exists():
            command.error(f"Source file not found: {source}")
            raise typer.Exit(1)

        import json
        with open(source) as f:
            profile_data = json.load(f)

        # Extract profile name from data if not provided
        if not name:
            if "name" in profile_data:
                name = profile_data.pop("name")
            else:
                # Use filename without extension
                name = source.stem

        # Validate profile
        from ..config import SettingsProfile
        profile = SettingsProfile.from_dict(profile_data, name=name)

        # Check if profile already exists
        if command.store.profile_exists(name) and not force:
            command.error(f"Profile '{name}' already exists")
            command.info("Use --force to overwrite")
            raise typer.Exit(1)

        # Import profile
        command.store.save_profile(profile)

        command.success(f"Imported profile '[cyan]{name}[/cyan]'")
        command.info(f"Provider: {profile.provider}")

        # Show validation issues if any
        issues = command.store.validate_profile(profile)
        if issues:
            command.warning("Profile has validation issues:")
            for issue in issues:
                command.error(f"  • {issue}")

    except Exception as e:
        command.handle_error(e)


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
    command = BaseCommand(directory)

    try:
        # Ensure profile exists
        command.ensure_profile_exists(name)
        profile = command.store.get_profile(name)

        # Get profile file path
        profile_file = command.store.get_profile_file(name)

        # Get editor command
        from .helpers import get_editor_command
        editor = get_editor_command()

        command.info(f"Opening [cyan]{name}[/cyan] in [cyan]{editor}[/cyan]")

        # Edit the file
        import subprocess
        result = subprocess.run([editor, str(profile_file)], check=False)

        if result.returncode != 0:
            command.error(f"Editor exited with code {result.returncode}")
            raise typer.Exit(1)

        # Validate edited profile
        try:
            edited_profile = command.store.get_profile(name)
            issues = command.store.validate_profile(edited_profile)

            if issues:
                command.warning("Edited profile has validation issues:")
                for issue in issues:
                    command.error(f"  • {issue}")

                import sys
                if sys.stdin.isatty():
                    if not command.confirm_action("\nKeep edited profile despite issues?", default=True):
                        # Restore original profile
                        command.store.save_profile(profile)
                        command.info("Original profile restored")
                        return
            else:
                command.success(f"Profile '[cyan]{name}[/cyan]' updated successfully")

        except Exception as e:
            command.error(f"Invalid JSON after edit: {e}")
            raise typer.Exit(1)

    except Exception as e:
        command.handle_error(e)


def register_commands(app: typer.Typer) -> None:
    """Register core commands with the typer app.

    Args:
        app: The typer application to register commands with
    """
    app.command("list", rich_help_panel="Commands")(list_profiles)
    app.command("switch", rich_help_panel="Commands")(switch_profile)
    app.command("show", rich_help_panel="Commands")(show_current)
    app.command("validate", rich_help_panel="Commands")(validate_profile)
    app.command("backup", rich_help_panel="Commands")(create_backup)
    app.command("restore", rich_help_panel="Commands")(restore_from_backup)
    app.command("diff", rich_help_panel="Commands")(diff_profiles)
    app.command("import", rich_help_panel="Commands")(import_profile)
    app.command("edit", rich_help_panel="Commands")(edit_profile)