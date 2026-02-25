"""Command-line interface using Click."""

from __future__ import annotations

from pathlib import Path

import click

from . import __version__


@click.group()
@click.version_option(version=__version__, prog_name="ftb-quest-localizer")
def cli() -> None:
    """FTB Quest Localizer - Extract and manage quest strings for easy localization."""


@cli.command()
@click.option(
    "--input",
    "-i",
    "input_path",
    required=True,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Path to the ftbquests/quests directory.",
)
@click.option(
    "--output",
    "-o",
    "output_dir",
    required=True,
    type=click.Path(path_type=Path),
    help="Output directory for JSON translation files.",
)
@click.option(
    "--flatten-single-lines",
    is_flag=True,
    default=False,
    help="Flatten single-element lists without adding numeric suffixes.",
)
def split(
    input_path: Path,
    output_dir: Path,
    flatten_single_lines: bool,
) -> None:
    """Split SNBT lang files into per-chapter JSON files.

    For new-format FTB Quests (1.20+) that have a lang/ directory.
    """
    from .splitter import split_lang_files

    click.echo("=== FTB Quest Localizer: Split ===\n")
    try:
        results = split_lang_files(
            input_path,
            output_dir,
            flatten_single_lines=flatten_single_lines,
        )
        if results:
            click.echo(click.style("\nDone!", fg="green", bold=True))
        else:
            click.echo(click.style("No entries found.", fg="yellow"))
    except FileNotFoundError as e:
        click.echo(click.style(f"Error: {e}", fg="red"), err=True)
        raise SystemExit(1)


@cli.command()
@click.option(
    "--input",
    "-i",
    "input_path",
    required=True,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Path to the ftbquests/quests directory.",
)
@click.option(
    "--output",
    "-o",
    "output_dir",
    required=True,
    type=click.Path(path_type=Path),
    help="Output directory for modified chapters and JSON lang file.",
)
@click.option(
    "--modpack",
    "-m",
    required=True,
    type=str,
    help="Modpack name (used as prefix for translation keys).",
)
def extract(
    input_path: Path,
    output_dir: Path,
    modpack: str,
) -> None:
    """Extract translatable strings from chapter SNBT files.

    For old-format FTB Quests (pre-1.20) with inline strings in chapter files.
    """
    from .extractor import extract_quest_strings

    click.echo("=== FTB Quest Localizer: Extract ===\n")
    try:
        results = extract_quest_strings(input_path, output_dir, modpack)
        if results:
            click.echo(click.style("\nDone!", fg="green", bold=True))
        else:
            click.echo(click.style("No translatable strings found.", fg="yellow"))
    except FileNotFoundError as e:
        click.echo(click.style(f"Error: {e}", fg="red"), err=True)
        raise SystemExit(1)


@cli.command()
@click.option(
    "--input",
    "-i",
    "input_dir",
    required=True,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Directory containing translated JSON files.",
)
@click.option(
    "--output",
    "-o",
    "output_dir",
    required=True,
    type=click.Path(path_type=Path),
    help="Output lang directory (e.g., lang/zh_cn/).",
)
def merge(
    input_dir: Path,
    output_dir: Path,
) -> None:
    """Merge translated JSON files back into a lang directory structure.

    Recreates the same structure as lang/en_us/ with chapter.snbt,
    chapter_group.snbt, reward_table.snbt, file.snbt, and chapters/*.snbt.
    """
    from .merger import merge_json_to_lang_dir

    click.echo("=== FTB Quest Localizer: Merge ===\n")
    try:
        count = merge_json_to_lang_dir(input_dir, output_dir)
        if count:
            click.echo(click.style("\nDone!", fg="green", bold=True))
        else:
            click.echo(click.style("No entries merged.", fg="yellow"))
    except FileNotFoundError as e:
        click.echo(click.style(f"Error: {e}", fg="red"), err=True)
        raise SystemExit(1)


if __name__ == "__main__":
    cli()
