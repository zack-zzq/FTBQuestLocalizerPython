"""Merge translated JSON files back into SNBT lang directory structure."""

from __future__ import annotations

import json
import os
from collections import OrderedDict
from pathlib import Path

import snbtlib

from .snbt_parser import escape_string_for_snbt, unflatten_lang_data


# Key prefixes that map to top-level SNBT files (not chapters/)
TOP_LEVEL_PREFIX_MAP = {
    "chapter.": "chapter.snbt",
    "chapter_group.": "chapter_group.snbt",
    "file.": "file.snbt",
    "reward_table.": "reward_table.snbt",
}

# Filename stems that are known top-level categories (not chapters)
TOP_LEVEL_FILE_STEMS = {"chapter_group", "reward_table", "file"}


def _write_snbt_lang_file(path: Path, data: OrderedDict) -> None:
    """Write an OrderedDict to an SNBT lang file with proper escaping."""
    path.parent.mkdir(parents=True, exist_ok=True)

    # Reconstruct multi-line entries
    reconstructed = unflatten_lang_data(data)

    # Escape strings for SNBT
    snbt_data: dict = {}
    for key, value in sorted(reconstructed.items()):
        if isinstance(value, list):
            snbt_data[key] = [escape_string_for_snbt(str(line)) for line in value]
        elif isinstance(value, str):
            snbt_data[key] = escape_string_for_snbt(value)
        else:
            snbt_data[key] = value

    snbt_string = snbtlib.dumps(snbt_data)
    with open(path, "w", encoding="utf-8") as f:
        f.write(snbt_string)


def _get_top_level_file(key: str) -> str | None:
    """Check if a lang key belongs to a top-level SNBT file.

    Returns the filename (e.g., 'chapter.snbt') if so, else None.
    Uses longest-prefix matching to avoid 'chapter.' matching 'chapter_group.'.
    """
    for prefix in sorted(TOP_LEVEL_PREFIX_MAP.keys(), key=len, reverse=True):
        if key.startswith(prefix):
            return TOP_LEVEL_PREFIX_MAP[prefix]
    return None


def _extract_json_chapter_name(filename: str) -> str:
    """Extract the chapter name from a JSON filename.

    E.g., 'en_us_welcome.json' -> 'welcome',
          'zh_cn_ice__fire.json' -> 'ice__fire'.
    """
    stem = filename.removesuffix(".json")
    parts = stem.split("_", 2)
    return parts[2] if len(parts) >= 3 else stem


def merge_json_to_lang_dir(
    json_dir: str | Path,
    output_dir: str | Path,
) -> int:
    """Merge translated JSON files into a lang directory structure.

    Uses **key prefixes** to route entries to the correct output file:
    - Keys starting with ``chapter.`` → ``chapter.snbt``
    - Keys starting with ``chapter_group.`` → ``chapter_group.snbt``
    - Keys starting with ``file.`` → ``file.snbt``
    - Keys starting with ``reward_table.`` → ``reward_table.snbt``
    - All other keys → ``chapters/<name>.snbt`` (inferred from JSON filename)

    Args:
        json_dir: Directory containing translated JSON files.
        output_dir: Output directory (e.g., ``lang/zh_cn/``).

    Returns:
        Total number of entries written.

    Raises:
        FileNotFoundError: If json_dir does not exist or has no JSON files.
    """
    json_dir = Path(json_dir)
    output_dir = Path(output_dir)

    if not json_dir.is_dir():
        raise FileNotFoundError(f"JSON directory not found: {json_dir}")

    json_files = sorted(f for f in os.listdir(json_dir) if f.endswith(".json"))
    if not json_files:
        raise FileNotFoundError(f"No JSON files found in: {json_dir}")

    # Accumulate entries by output file path
    output_buckets: dict[Path, OrderedDict] = {}

    for filename in json_files:
        filepath = json_dir / filename
        try:
            with open(filepath, "r", encoding="utf-8-sig") as f:
                data = json.load(f, object_pairs_hook=OrderedDict)
        except Exception as e:
            print(f"  Warning: Failed to read {filename}: {e}")
            continue

        if not data:
            continue

        chapter_name = _extract_json_chapter_name(filename)

        for key, value in data.items():
            top_level = _get_top_level_file(key)
            if top_level:
                out_path = output_dir / top_level
            else:
                # Extract chapter name from key prefix:
                # Keys are like "ModpackName.chapter_name.rest"
                # The 2nd segment is the chapter name
                parts = key.split(".", 2)
                if len(parts) >= 2:
                    chapter = parts[1]
                else:
                    chapter = chapter_name  # fallback to filename-based
                if chapter in TOP_LEVEL_FILE_STEMS:
                    out_path = output_dir / f"{chapter}.snbt"
                else:
                    out_path = output_dir / "chapters" / f"{chapter}.snbt"

            if out_path not in output_buckets:
                output_buckets[out_path] = OrderedDict()
            output_buckets[out_path][key] = value

        print(f"  -> Loaded {len(data)} entries from: {filename}")

    if not output_buckets:
        print("Error: No data loaded from JSON files.")
        return 0

    # Write all output files
    output_dir.mkdir(parents=True, exist_ok=True)
    total = 0

    for out_path, data in sorted(output_buckets.items()):
        _write_snbt_lang_file(out_path, data)
        total += len(data)
        rel_path = out_path.relative_to(output_dir)
        print(f"  -> Wrote {len(data)} entries to: {rel_path}")

    file_count = len(output_buckets)
    print(f"\nMerge complete. {total} entries across {file_count} files.")
    return total
