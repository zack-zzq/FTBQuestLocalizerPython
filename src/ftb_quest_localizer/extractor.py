"""Extract translatable strings from old-format FTB Quest chapter files (pre-1.20)."""

from __future__ import annotations

import json
import re
from collections import OrderedDict
from pathlib import Path

from .snbt_parser import load_snbt, dump_snbt


# Fields that contain translatable text
TRANSLATABLE_FIELDS = ("title", "subtitle", "description", "text")

# Pattern to detect image references that should be skipped
IMAGE_PATTERN = re.compile(r"^\{image:[0-9a-zA-Z]*:.*\}$")

# Pattern to detect page breaks that should be skipped
PAGEBREAK_PATTERN = re.compile(r"^\{@\w+\}$")


def _should_skip(text: str) -> bool:
    """Check if a text string should be skipped (images, page breaks, empty)."""
    if not text or not text.strip():
        return True
    if IMAGE_PATTERN.match(text):
        return True
    if PAGEBREAK_PATTERN.match(text):
        return True
    return False


def _extract_from_dict(
    data: dict,
    key_prefix: str,
    lang: OrderedDict,
) -> None:
    """Recursively extract translatable strings from a parsed SNBT dict.

    Modifies both `data` (replacing strings with translation keys) and `lang`
    (adding key-value pairs for the language file).

    Args:
        data: Parsed SNBT data dict (modified in-place).
        key_prefix: Key prefix for generating translation keys.
        lang: Language dict to accumulate extracted strings.
    """
    for field in TRANSLATABLE_FIELDS:
        if field not in data:
            continue

        value = data[field]

        if isinstance(value, list):
            # Multi-line field (e.g., description: ["line1", "line2"])
            has_content = False
            for i, line in enumerate(value):
                line_str = str(line)
                if _should_skip(line_str):
                    continue
                has_content = True
                if len(value) > 1:
                    lang_key = f"{key_prefix}.{field}{i}"
                else:
                    lang_key = f"{key_prefix}.{field}"
                lang[lang_key] = line_str
                value[i] = "{" + lang_key + "}"
            if has_content:
                data[field] = value

        elif isinstance(value, str):
            if _should_skip(value):
                continue
            lang_key = f"{key_prefix}.{field}"
            lang[lang_key] = value
            data[field] = "{" + lang_key + "}"

    # Process quest images hover text
    if "images" in data and isinstance(data["images"], list):
        for i, image in enumerate(data["images"]):
            if isinstance(image, dict) and "hover" in image:
                hover = image["hover"]
                if isinstance(hover, list):
                    for j, line in enumerate(hover):
                        line_str = str(line)
                        if _should_skip(line_str):
                            continue
                        lang_key = f"{key_prefix}.images{i}.hover{j}"
                        lang[lang_key] = line_str
                        hover[j] = "{" + lang_key + "}"
                elif isinstance(hover, str) and not _should_skip(hover):
                    lang_key = f"{key_prefix}.images{i}.hover"
                    lang[lang_key] = hover
                    image["hover"] = "{" + lang_key + "}"


def _extract_from_chapter(
    chapter_data: dict,
    chapter_name: str,
    modpack_name: str,
    lang: OrderedDict,
) -> None:
    """Extract all translatable strings from a chapter.

    Args:
        chapter_data: Parsed chapter SNBT data (modified in-place).
        chapter_name: Chapter file name (without extension).
        modpack_name: Modpack name for key prefix.
        lang: Language dict to accumulate extracted strings.
    """
    prefix = f"{modpack_name}.{chapter_name}"

    # Chapter-level fields
    _extract_from_dict(chapter_data, prefix, lang)

    # Process quests
    for i, quest in enumerate(chapter_data.get("quests", [])):
        quest_prefix = f"{prefix}.quests{i}"
        _extract_from_dict(quest, quest_prefix, lang)

        # Process tasks within quests
        for j, task in enumerate(quest.get("tasks", [])):
            task_prefix = f"{quest_prefix}.tasks{j}"
            _extract_from_dict(task, task_prefix, lang)

        # Process rewards within quests
        for j, reward in enumerate(quest.get("rewards", [])):
            reward_prefix = f"{quest_prefix}.rewards{j}"
            _extract_from_dict(reward, reward_prefix, lang)


def extract_quest_strings(
    ftbquests_path: str | Path,
    output_dir: str | Path,
    modpack_name: str,
) -> dict[str, int]:
    """Extract translatable strings from old-format FTB Quest chapter files.

    This handles the old FTB Quests format (pre-1.20) where translatable strings
    are embedded directly in the chapter SNBT files.

    Args:
        ftbquests_path: Path to the ``ftbquests/quests`` directory.
        output_dir: Directory to write output files to.
        modpack_name: Name of the modpack (used as key prefix).

    Returns:
        Dict mapping output filename to number of entries written.
    """
    ftbquests_path = Path(ftbquests_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Normalize modpack name for keys: lowercase, spaces -> underscores
    key_prefix = re.sub(r"[^a-z0-9_]", "_", modpack_name.lower()).strip("_")

    chapters_dir = ftbquests_path / "chapters"
    if not chapters_dir.is_dir():
        raise FileNotFoundError(f"Chapters directory not found: {chapters_dir}")

    all_lang = OrderedDict()
    results: dict[str, int] = {}
    chapters_output = output_dir / "chapters"
    chapters_output.mkdir(parents=True, exist_ok=True)

    # Process data.snbt if present (has title field)
    data_file = ftbquests_path / "data.snbt"
    if data_file.exists():
        try:
            data_data = load_snbt(data_file)
            _extract_from_dict(data_data, f"{key_prefix}.data", all_lang)
            dump_snbt(data_data, output_dir / "data.snbt")
            print("  -> Processed data.snbt")
        except Exception as e:
            print(f"Warning: Failed to process data.snbt: {e}")

    # Process chapter_groups if present
    chapter_groups_file = ftbquests_path / "chapter_groups.snbt"
    if chapter_groups_file.exists():
        try:
            groups_data = load_snbt(chapter_groups_file)
            if "chapter_groups" in groups_data:
                for i, group in enumerate(groups_data["chapter_groups"]):
                    if "title" in group:
                        prefix = (
                            f"{key_prefix}.chapter_groups.title{i}"
                        )
                        all_lang[prefix] = group["title"]
                        group["title"] = "{" + prefix + "}"
                dump_snbt(groups_data, output_dir / "chapter_groups.snbt")
                print("  -> Processed chapter_groups.snbt")
        except Exception as e:
            print(f"Warning: Failed to process chapter_groups.snbt: {e}")

    # Process reward_tables if present
    reward_tables_dir = ftbquests_path / "reward_tables"
    if reward_tables_dir.is_dir():
        rt_output = output_dir / "reward_tables"
        rt_output.mkdir(parents=True, exist_ok=True)
        for filename in sorted(os.listdir(reward_tables_dir)):
            if not filename.endswith(".snbt"):
                continue
            try:
                rt_data = load_snbt(reward_tables_dir / filename)
                rt_name = filename.removesuffix(".snbt")
                prefix = f"{key_prefix}.reward_tables.{rt_name}"
                _extract_from_dict(rt_data, prefix, all_lang)
                dump_snbt(rt_data, rt_output / filename)
            except Exception as e:
                print(f"Warning: Failed to process reward_table {filename}: {e}")

    # Process each chapter file
    for filename in sorted(os.listdir(chapters_dir)):
        if not filename.endswith(".snbt"):
            continue

        chapter_name = filename.removesuffix(".snbt")
        try:
            chapter_data = load_snbt(chapters_dir / filename)
            chapter_lang = OrderedDict()

            _extract_from_chapter(chapter_data, chapter_name, key_prefix, chapter_lang)

            if chapter_lang:
                all_lang.update(chapter_lang)
                dump_snbt(chapter_data, chapters_output / filename)
                results[filename] = len(chapter_lang)
                print(f"  -> Extracted {len(chapter_lang)} strings from {filename}")
            else:
                # No translatable content, just copy the file
                dump_snbt(chapter_data, chapters_output / filename)

        except Exception as e:
            print(f"Warning: Failed to process {filename}: {e}")

    # Write language file
    if all_lang:
        lang_file = output_dir / "en_us.json"
        with open(lang_file, "w", encoding="utf-8") as f:
            json.dump(all_lang, f, ensure_ascii=False, indent=2)
        print(f"\nExtracted {len(all_lang)} total strings to en_us.json")

    return results


# Need os for listdir
import os
