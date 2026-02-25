"""SNBT file reading and writing utilities, wrapping snbtlib."""

from __future__ import annotations

import re
from collections import OrderedDict
from pathlib import Path

import snbtlib


def load_snbt(path: str | Path) -> OrderedDict:
    """Read and parse an SNBT file into an OrderedDict.

    Args:
        path: Path to the SNBT file.

    Returns:
        Parsed data as an OrderedDict.

    Raises:
        FileNotFoundError: If the file does not exist.
        snbtlib.SNBTParseError: If the file contains invalid SNBT.
    """
    path = Path(path)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return snbtlib.loads(content)


def dump_snbt(data: dict, path: str | Path, *, compact: bool = False) -> None:
    """Serialize data and write it to an SNBT file.

    Args:
        data: The data to serialize.
        path: Output file path.
        compact: If True, use compact format (for 1.12 old-format files).
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    snbt_string = snbtlib.dumps(data, compact=compact)
    with open(path, "w", encoding="utf-8") as f:
        f.write(snbt_string)


def unescape_string(s: str) -> str:
    r"""Unescape a string loaded from SNBT.

    Converts escaped sequences back to their original characters:
    - ``\\\"`` -> ``"``
    - ``\\\\`` -> ``\\``
    """
    s = s.replace(r'\"', '"')
    s = s.replace("\\\\", "\\")
    return s


def escape_string_for_snbt(s: str) -> str:
    r"""Escape a string for writing back to SNBT.

    Converts characters that need escaping:
    - ``\\`` -> ``\\\\``
    - ``"`` -> ``\\\"``
    """
    s = s.replace("\\", "\\\\")
    s = s.replace('"', '\\"')
    return s


def flatten_lang_data(
    snbt_data: OrderedDict,
    *,
    flatten_single_lines: bool = False,
) -> OrderedDict:
    """Flatten SNBT lang data by expanding list values into numbered keys.

    For example, a key ``quest.123.quest_desc`` with value ``["line1", "line2"]``
    becomes ``quest.123.quest_desc1`` = ``"line1"`` and ``quest.123.quest_desc2`` = ``"line2"``.

    Args:
        snbt_data: Parsed SNBT data (key-value pairs).
        flatten_single_lines: If True, single-element lists won't get a numeric
            suffix (the key stays as-is).

    Returns:
        Flattened OrderedDict with string values only.
    """
    lang_data = OrderedDict()
    for key, value in snbt_data.items():
        if isinstance(value, list):
            if flatten_single_lines and len(value) == 1:
                lang_data[key] = unescape_string(str(value[0]))
            else:
                for i, line in enumerate(value, 1):
                    new_key = f"{key}{i}"
                    lang_data[new_key] = unescape_string(str(line))
        elif isinstance(value, str):
            lang_data[key] = unescape_string(value)
        else:
            lang_data[key] = value
    return lang_data


def unflatten_lang_data(flat_data: OrderedDict) -> OrderedDict:
    """Reconstruct multi-line entries from numbered keys back to lists.

    Keys ending with digits (e.g., ``quest.123.quest_desc1``) are merged back
    into list values under the base key (``quest.123.quest_desc``).

    Args:
        flat_data: Flattened lang data with numbered suffixes.

    Returns:
        OrderedDict with list values reconstructed.
    """
    multi_line_pattern = re.compile(r"^(.*?)(\d+)$")
    temp_multiline: dict[str, list[tuple[int, str]]] = {}
    reconstructed = OrderedDict()

    for key, value in flat_data.items():
        match = multi_line_pattern.match(key)
        if match:
            base_key = match.group(1)
            line_number = int(match.group(2))
            if base_key not in temp_multiline:
                temp_multiline[base_key] = []
            temp_multiline[base_key].append((line_number, value))
        else:
            reconstructed[key] = value

    for base_key, lines_with_nums in temp_multiline.items():
        lines_with_nums.sort(key=lambda x: x[0])
        sorted_lines = [text for _, text in lines_with_nums]
        reconstructed[base_key] = sorted_lines

    return reconstructed
