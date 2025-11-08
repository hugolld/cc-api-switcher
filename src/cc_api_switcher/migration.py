"""Profile migration utilities for CC API Switcher."""

import os
import shutil
from pathlib import Path
from typing import List, Optional

from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table

from .config import ProfileStore, SettingsProfile
from .global_config import GlobalConfig

console = Console()


class ProfileMigration:
    """Utilities for migrating profiles to global configuration."""

    def __init__(self, global_config: Optional[GlobalConfig] = None):
        """
        Initialize migration tool.

        Args:
            global_config: Optional GlobalConfig instance
        """
        self.global_config = global_config or GlobalConfig()

    def discover_local_profiles(self) -> List[Path]:
        """
        Discover profiles in common local directories.

        Returns:
            List of profile files found
        """
        profile_files = []

        # Current directory
        current_dir = Path.cwd()
        for profile_file in current_dir.glob("*_settings.json"):
            profile_files.append(profile_file)

        # Common profile directories
        search_dirs = [
            current_dir / "profiles",
            current_dir / ".profiles",
            Path.home() / "profiles",
        ]

        for search_dir in search_dirs:
            if search_dir.exists():
                for profile_file in search_dir.glob("*_settings.json"):
                    profile_files.append(profile_file)

        return sorted(set(profile_files))

    def migrate_profiles(
        self,
        source_dir: Optional[Path] = None,
        force: bool = False,
        dry_run: bool = False,
    ) -> None:
        """
        Migrate profiles from source directory to global configuration.

        Args:
            source_dir: Source directory containing profiles
            force: Force overwrite existing profiles
            dry_run: Show what would be migrated without doing it
        """
        # Ensure global profiles directory exists
        global_profiles_dir = self.global_config.ensure_global_profiles_dir()

        if source_dir:
            # Migrate from specific directory
            source_files = list(source_dir.glob("*_settings.json"))
        else:
            # Discover and migrate from common locations
            source_files = self.discover_local_profiles()

        if not source_files:
            console.print("[yellow]No profiles found to migrate.[/yellow]")
            return

        # Show migration plan
        self._show_migration_plan(source_files, global_profiles_dir)

        if dry_run:
            console.print("\n[dim]Dry run mode - no files were copied.[/dim]")
            return

        # Confirm migration
        if not force and not Confirm.ask("\n[bold]Proceed with migration?[/bold]"):
            console.print("[dim]Migration cancelled.[/dim]")
            return

        # Perform migration
        migrated_count = 0
        skipped_count = 0

        for source_file in source_files:
            try:
                profile_name = source_file.stem.replace("_settings", "")
                target_file = global_profiles_dir / f"{profile_name}_settings.json"

                # Check if target exists
                if target_file.exists() and not force:
                    console.print(
                        f"[yellow]⚠ Skipped {profile_name} (already exists)[/yellow]"
                    )
                    skipped_count += 1
                    continue

                # Copy profile
                shutil.copy2(source_file, target_file)
                console.print(f"[green]✓ Migrated {profile_name}[/green]")
                migrated_count += 1

            except Exception as e:
                console.print(f"[red]✗ Failed to migrate {source_file}: {e}[/red]")
                skipped_count += 1

        # Show summary
        console.print(
            f"\n[bold]Migration Summary:[/bold]\n"
            f"  [green]✓ Migrated:[/green] {migrated_count}\n"
            f"  [yellow]⚠ Skipped:[/yellow] {skipped_count}\n"
            f"  [dim]Target directory:[/dim] {global_profiles_dir}"
        )

        if migrated_count > 0:
            console.print(
                "\n[dim]You can now use '[cyan]cc-api-switch list[/cyan]' to see your profiles "
                "and '[cyan]cc-api-switch switch[/cyan]' from any directory.[/dim]"
            )

    def _show_migration_plan(self, source_files: List[Path], target_dir: Path) -> None:
        """Show the migration plan to the user."""
        table = Table(title="Migration Plan", show_header=True, header_style="bold cyan")
        table.add_column("Source", style="green")
        table.add_column("Profile Name", style="blue")
        table.add_column("Target", style="yellow")
        table.add_column("Status", style="magenta")

        for source_file in source_files:
            profile_name = source_file.stem.replace("_settings", "")
            target_file = target_dir / f"{profile_name}_settings.json"

            if target_file.exists():
                status = "[yellow]Will overwrite[/yellow]"
            else:
                status = "[green]Will create[/green]"

            # Truncate long paths
            source_display = str(source_file)
            if len(source_display) > 50:
                source_display = "..." + source_display[-47:]

            table.add_row(
                source_display,
                profile_name,
                str(target_file),
                status,
            )

        console.print(table)
        console.print(f"\n[dim]Target directory:[/dim] {target_dir}")

    def cleanup_local_profiles(self, force: bool = False) -> None:
        """
        Clean up local profile files after successful migration.

        Args:
            force: Skip confirmation prompt
        """
        local_profiles = self.discover_local_profiles()

        if not local_profiles:
            console.print("[yellow]No local profiles found to clean up.[/yellow]")
            return

        # Show what will be cleaned up
        table = Table(title="Local Profiles to Clean Up", show_header=True, header_style="bold cyan")
        table.add_column("File", style="red")
        table.add_column("Size", style="yellow")

        total_size = 0
        for profile_file in local_profiles:
            size = profile_file.stat().st_size if profile_file.exists() else 0
            size_str = self._format_size(size)
            total_size += size

            table.add_row(str(profile_file), size_str)

        console.print(table)
        console.print(f"\n[dim]Total size:[/dim] {self._format_size(total_size)}")

        # Confirm cleanup
        if not force and not Confirm.ask(
            "\n[bold red]Delete these local profile files?[/bold red] "
            "[dim](This cannot be undone)[/dim]"
        ):
            console.print("[dim]Cleanup cancelled.[/dim]")
            return

        # Perform cleanup
        deleted_count = 0
        for profile_file in local_profiles:
            try:
                profile_file.unlink()
                console.print(f"[green]✓ Deleted {profile_file}[/green]")
                deleted_count += 1
            except Exception as e:
                console.print(f"[red]✗ Failed to delete {profile_file}: {e}[/red]")

        console.print(
            f"\n[bold]Cleanup Summary:[/bold]\n"
            f"  [green]✓ Deleted:[/green] {deleted_count}\n"
            f"  [red]🗑️ Space freed:[/red] {self._format_size(total_size)}"
        )

    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def validate_migrated_profiles(self) -> None:
        """Validate all profiles in global configuration."""
        global_profiles_dir = self.global_config.global_profiles_dir

        if not global_profiles_dir.exists():
            console.print("[yellow]Global profiles directory does not exist.[/yellow]")
            return

        profile_files = list(global_profiles_dir.glob("*_settings.json"))

        if not profile_files:
            console.print("[yellow]No profiles found in global directory.[/yellow]")
            return

        console.print("[bold]Validating migrated profiles...[/bold]\n")

        valid_count = 0
        invalid_count = 0

        for profile_file in profile_files:
            try:
                profile = SettingsProfile.from_file(profile_file)
                issues = profile.validate_profile()

                if not issues:
                    console.print(f"[green]✓ {profile.name}[/green]")
                    valid_count += 1
                else:
                    console.print(f"[yellow]⚠ {profile.name} has issues:[/yellow]")
                    for issue in issues:
                        console.print(f"  • [dim]{issue}[/dim]")
                    valid_count += 1  # Still valid format, just has configuration issues

            except Exception as e:
                console.print(f"[red]✗ {profile_file.name}: {e}[/red]")
                invalid_count += 1

        # Show summary
        console.print(
            f"\n[bold]Validation Summary:[/bold]\n"
            f"  [green]✓ Valid:[/green] {valid_count}\n"
            f"  [red]✗ Invalid:[/red] {invalid_count}"
        )