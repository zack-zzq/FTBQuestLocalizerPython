# FTB Quest Localizer

[![PyPI version](https://img.shields.io/pypi/v/ftb-quest-localizer.svg)](https://pypi.org/project/ftb-quest-localizer/)
[![Python Version](https://img.shields.io/pypi/pyversions/ftb-quest-localizer.svg)](https://pypi.org/project/ftb-quest-localizer/)
[![License](https://img.shields.io/github/license/zack-zzq/FTBQuestLocalizerPython)](LICENSE)

English | [中文](README_zh.md)

A tool for extracting and managing FTB Quest localization strings. Supports both **new format** (1.20+, with `lang/` directory) and **old format** (pre-1.20, inline strings in chapter files).

## Installation

From PyPI:
```bash
pip install ftb-quest-localizer
```

From source (using [uv](https://docs.astral.sh/uv/)):
```bash
git clone https://github.com/zack-zzq/FTBQuestLocalizerPython
cd FTBQuestLocalizerPython
uv sync
```

## Usage

The tool provides three commands: `split`, `extract`, and `merge`.

### `split` — New Format (1.20+)

Split SNBT lang files from `lang/en_us/` into per-chapter JSON files for translation:

```bash
ftb-quest-localizer split -i <ftbquests/quests> -o <output_dir>
```

This reads the `lang/en_us/` directory and outputs one JSON file per chapter, plus separate files for chapter groups, reward tables, etc.

### `extract` — Old Format (pre-1.20)

Extract translatable strings directly from chapter SNBT files:

```bash
ftb-quest-localizer extract -i <ftbquests/quests> -o <output_dir> -m <modpack_name>
```

This replaces inline strings with translation keys and generates an `en_us.json` language file.

### `merge` — Merge Translations Back

Merge translated JSON files back into SNBT lang directory structure:

```bash
ftb-quest-localizer merge -i <json_dir> -o <output_lang_dir>
```

This recreates the same structure as `lang/en_us/` (`chapter.snbt`, `chapter_group.snbt`, `chapters/*.snbt`, etc.) for direct use in a modpack.

### As a Python Library

```python
from ftb_quest_localizer.splitter import split_lang_files
from ftb_quest_localizer.extractor import extract_quest_strings
from ftb_quest_localizer.merger import merge_json_to_lang_dir

# New format: split SNBT lang files into JSON
split_lang_files("path/to/ftbquests/quests", "output/")

# Old format: extract strings from chapter files
extract_quest_strings("path/to/ftbquests/quests", "output/", "modpack_name")

# Merge translated JSON back into SNBT
merge_json_to_lang_dir("translated_json/", "lang/zh_cn/")
```

## How It Works

### New Format (1.20+)
1. Reads SNBT lang files from `lang/en_us/` (chapter, quest, task, reward entries)
2. Flattens multi-line descriptions into numbered keys
3. Groups entries by chapter and outputs per-chapter JSON files
4. Merge reconstructs the original directory structure from translated JSON

### Old Format (pre-1.20)
1. Parses chapter SNBT files using `snbtlib`
2. Extracts `title`, `subtitle`, `description`, `text`, and hover text fields
3. Replaces original text with translation keys
4. Generates JSON language files with the original text
