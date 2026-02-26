"""Split SNBT lang files (new FTB Quests 1.20+ format) into per-chapter JSON files."""

from __future__ import annotations

import json
import os
from collections import OrderedDict
from pathlib import Path

from .snbt_parser import flatten_lang_data, load_snbt


def _categorize_entries(
    lang_data: OrderedDict,
) -> dict[str, OrderedDict]:
    """Categorize flattened lang entries by their prefix type.

    Returns a dict with keys: 'chapter', 'chapter_group', 'quest', 'task',
    'reward', 'reward_table', 'file', 'other'.
    """
    categories: dict[str, OrderedDict] = {
        "chapter": OrderedDict(),
        "chapter_group": OrderedDict(),
        "quest": OrderedDict(),
        "task": OrderedDict(),
        "reward": OrderedDict(),
        "reward_table": OrderedDict(),
        "file": OrderedDict(),
        "other": OrderedDict(),
    }

    prefix_map = {
        "chapter_group.": "chapter_group",
        "chapter.": "chapter",
        "quest.": "quest",
        "task.": "task",
        "reward_table.": "reward_table",
        "reward.": "reward",
        "file.": "file",
    }

    for key, value in lang_data.items():
        assigned = False
        # Check longer prefixes first to avoid "chapter." matching "chapter_group."
        for prefix in sorted(prefix_map.keys(), key=len, reverse=True):
            if key.startswith(prefix):
                categories[prefix_map[prefix]][key] = value
                assigned = True
                break
        if not assigned:
            categories["other"][key] = value

    return categories


def _build_chapter_id_map(chapters_dir: str | Path) -> dict[str, str]:
    """Build a mapping from chapter ID -> chapter filename (without .snbt).

    Reads each chapter SNBT file to extract its 'id' field.

    Args:
        chapters_dir: Path to the directory containing chapter SNBT files.

    Returns:
        Dict mapping hex chapter ID to the chapter filename stem.
    """
    chapter_id_map: dict[str, str] = {}
    chapters_path = Path(chapters_dir)
    if not chapters_path.is_dir():
        return chapter_id_map

    for filename in os.listdir(chapters_path):
        if not filename.endswith(".snbt"):
            continue
        try:
            chapter_data = load_snbt(chapters_path / filename)
            chapter_id = chapter_data.get("id")
            if chapter_id:
                chapter_id_map[chapter_id] = filename.removesuffix(".snbt")
        except Exception:
            continue

    return chapter_id_map


def _build_quest_to_chapter_map(
    chapters_dir: str | Path,
) -> dict[str, str]:
    """Build a mapping from quest/task/reward ID -> chapter ID.

    Args:
        chapters_dir: Path to directory containing chapter SNBT files.

    Returns:
        Dict mapping item hex IDs to their parent chapter hex ID.
    """
    item_to_chapter: dict[str, str] = {}
    chapters_path = Path(chapters_dir)
    if not chapters_path.is_dir():
        return item_to_chapter

    for filename in os.listdir(chapters_path):
        if not filename.endswith(".snbt"):
            continue
        try:
            chapter_data = load_snbt(chapters_path / filename)
            chapter_id = chapter_data.get("id")
            if not chapter_id:
                continue

            for quest in chapter_data.get("quests", []):
                quest_id = quest.get("id")
                if quest_id:
                    item_to_chapter[quest_id] = chapter_id
                    for task in quest.get("tasks", []):
                        task_id = task.get("id")
                        if task_id:
                            item_to_chapter[task_id] = chapter_id
                    for reward in quest.get("rewards", []):
                        reward_id = reward.get("id")
                        if reward_id:
                            item_to_chapter[reward_id] = chapter_id
        except Exception:
            continue

    return item_to_chapter


def _extract_hex_id(key: str) -> str | None:
    """Extract the hex ID from a lang key like 'quest.3BC0A50886A3222B.title'."""
    parts = key.split(".")
    if len(parts) >= 2:
        return parts[1]
def extract_single_file_lang(
    snbt_file: str | Path,
    output_dir: str | Path,
    *,
    flatten_single_lines: bool = False,
) -> int:
    """Extract a single SNBT lang file (e.g., lang/en_us.snbt) to a single JSON file.

    This handles the variant where modpack creators export all FTB Quests strings
    into a single SNBT file, rather than splitting by chapter.

    Args:
        snbt_file: Path to the .snbt lang file (e.g., ftbquests/quests/lang/en_us.snbt).
        output_dir: Directory to write the resulting en_us.json to.
        flatten_single_lines: If True, single-element lists won't get numeric suffixes.

    Returns:
        Number of entries extracted.
    """
    snbt_file = Path(snbt_file)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not snbt_file.is_file():
        raise FileNotFoundError(f"SNBT lang file not found: {snbt_file}")

    data = load_snbt(snbt_file)
    flat = flatten_lang_data(data, flatten_single_lines=flatten_single_lines)

    if not flat:
        print(f"No lang entries found in {snbt_file.name}.")
        return 0

    output_file = output_dir / snbt_file.with_suffix(".json").name
    _write_json(output_file, flat)

    print(f"Extracted {len(flat)} entries from {snbt_file.name} to {output_file.name}.")
    return len(flat)


def split_lang_files(
    ftbquests_path: str | Path,
    output_dir: str | Path,
    *,
    flatten_single_lines: bool = False,
) -> dict[str, int]:
    """Split SNBT lang files into per-chapter JSON files.

    This handles the new FTB Quests format (1.20+) where translatable strings
    live in ``ftbquests/quests/lang/<locale>/`` as SNBT files.

    Args:
        ftbquests_path: Path to the ``ftbquests/quests`` directory.
        output_dir: Directory to write JSON output files to.
        flatten_single_lines: If True, single-element lists won't get numeric suffixes.

    Returns:
        Dict mapping output filename to number of entries written.
    """
    ftbquests_path = Path(ftbquests_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    lang_dir = ftbquests_path / "lang" / "en_us"
    lang_file = ftbquests_path / "lang" / "en_us.snbt"
    chapters_dir = ftbquests_path / "chapters"

    if not lang_dir.is_dir() and not lang_file.is_file():
        raise FileNotFoundError(
            f"Lang directory/file not found at {ftbquests_path / 'lang'}\n"
            "This modpack may use the old format. Try 'extract' command instead."
        )

    # 1. Load all lang SNBT files and merge into a single dict
    all_lang_data = OrderedDict()

    # Load single lang file if it exists
    if lang_file.is_file():
        try:
            data = load_snbt(lang_file)
            flat = flatten_lang_data(data, flatten_single_lines=flatten_single_lines)
            all_lang_data.update(flat)
        except Exception as e:
            print(f"Warning: Failed to parse {lang_file.name}: {e}")

    # Load from lang/en_us/ directory if it exists
    if lang_dir.is_dir():
        # Load top-level lang files
        for snbt_file in sorted(lang_dir.glob("*.snbt")):
            try:
                data = load_snbt(snbt_file)
                flat = flatten_lang_data(data, flatten_single_lines=flatten_single_lines)
                all_lang_data.update(flat)
            except Exception as e:
                print(f"Warning: Failed to parse {snbt_file.name}: {e}")

        # Load chapter-specific lang files
        chapters_lang_dir = lang_dir / "chapters"
        if chapters_lang_dir.is_dir():
            for snbt_file in sorted(chapters_lang_dir.glob("*.snbt")):
                try:
                    data = load_snbt(snbt_file)
                    flat = flatten_lang_data(
                        data, flatten_single_lines=flatten_single_lines
                    )
                    all_lang_data.update(flat)
                except Exception as e:
                    print(f"Warning: Failed to parse chapters/{snbt_file.name}: {e}")

    if not all_lang_data:
        print("No lang entries found.")
        return {}

    print(f"Loaded {len(all_lang_data)} total lang entries.")

    # 2. Categorize entries
    categories = _categorize_entries(all_lang_data)

    # 3. Build mappings for grouping by chapter
    chapter_id_map = _build_chapter_id_map(chapters_dir)
    item_to_chapter = _build_quest_to_chapter_map(chapters_dir)

    # 4. Output non-chapter/quest entries as separate files
    results: dict[str, int] = {}

    for cat_name in ("chapter_group", "reward_table", "file", "other"):
        data = categories[cat_name]
        if data:
            filename = f"en_us_{cat_name}.json"
            _write_json(output_dir / filename, data)
            results[filename] = len(data)
            print(f"  -> Exported {len(data)} entries to: {filename}")

    # 5. Group chapter/quest/task/reward entries by chapter
    chapter_outputs: dict[str, OrderedDict] = {}

    # Chapter-level entries (chapter.HEXID.*)
    for key, value in categories["chapter"].items():
        hex_id = _extract_hex_id(key)
        if hex_id and hex_id in chapter_id_map:
            chapter_name = chapter_id_map[hex_id]
            chapter_outputs.setdefault(chapter_name, OrderedDict())[key] = value

    # Quest/task/reward entries -> map to chapter via quest_to_chapter
    for cat_name in ("quest", "task", "reward"):
        for key, value in categories[cat_name].items():
            hex_id = _extract_hex_id(key)
            if hex_id and hex_id in item_to_chapter:
                chapter_id = item_to_chapter[hex_id]
                if chapter_id in chapter_id_map:
                    chapter_name = chapter_id_map[chapter_id]
                    chapter_outputs.setdefault(chapter_name, OrderedDict())[
                        key
                    ] = value

    # 6. Write per-chapter JSON files
    for chapter_name, data in sorted(chapter_outputs.items()):
        filename = f"en_us_{chapter_name}.json"
        _write_json(output_dir / filename, data)
        results[filename] = len(data)
        print(f"  -> Exported {len(data)} entries to: {filename}")

    total = sum(results.values())
    print(f"\nSplit complete. {total} entries across {len(results)} files.")
    return results


def _write_json(path: Path, data: OrderedDict) -> None:
    """Write an OrderedDict to a JSON file with pretty formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
