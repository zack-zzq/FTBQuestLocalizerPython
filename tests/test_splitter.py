"""Tests for splitter module using ATM10 test data."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from ftb_quest_localizer.splitter import (
    _build_chapter_id_map,
    _build_quest_to_chapter_map,
    _categorize_entries,
    _extract_hex_id,
    split_lang_files,
)
from collections import OrderedDict


# Path to ATM10 test data
TEST_DATA = Path(__file__).parent.parent / "output" / "config" / "ftbquests" / "quests"


class TestExtractHexId:
    def test_quest_key(self):
        assert _extract_hex_id("quest.3BC0A50886A3222B.title") == "3BC0A50886A3222B"

    def test_chapter_key(self):
        assert _extract_hex_id("chapter.5B00676D79306EA2.title") == "5B00676D79306EA2"

    def test_task_key(self):
        assert _extract_hex_id("task.103C42C743E2A2DB.title") == "103C42C743E2A2DB"

    def test_no_id(self):
        assert _extract_hex_id("single") is None


class TestCategorizeEntries:
    def test_basic_categorization(self):
        data = OrderedDict([
            ("chapter.ABC.title", "Chapter Title"),
            ("chapter_group.DEF.title", "Group Title"),
            ("quest.GHI.title", "Quest Title"),
            ("task.JKL.title", "Task Title"),
            ("reward.MNO.title", "Reward Title"),
            ("reward_table.PQR.title", "Reward Table"),
            ("file.STU.title", "File Title"),
            ("unknown.key", "Other"),
        ])
        result = _categorize_entries(data)
        assert "Chapter Title" in result["chapter"].values()
        assert "Group Title" in result["chapter_group"].values()
        assert "Quest Title" in result["quest"].values()
        assert "Task Title" in result["task"].values()
        assert "Reward Title" in result["reward"].values()
        assert "Reward Table" in result["reward_table"].values()
        assert "File Title" in result["file"].values()
        assert "Other" in result["other"].values()

    def test_chapter_group_not_confused_with_chapter(self):
        """Ensure 'chapter_group.' prefix is not matched by 'chapter.'."""
        data = OrderedDict([
            ("chapter_group.ABC.title", "Group"),
            ("chapter.DEF.title", "Chapter"),
        ])
        result = _categorize_entries(data)
        assert len(result["chapter_group"]) == 1
        assert len(result["chapter"]) == 1


@pytest.mark.skipif(
    not TEST_DATA.exists(),
    reason="ATM10 test data not available",
)
class TestBuildMaps:
    def test_chapter_id_map(self):
        chapters_dir = TEST_DATA / "chapters"
        id_map = _build_chapter_id_map(chapters_dir)
        assert len(id_map) > 0
        # welcome.snbt has id 5B00676D79306EA2
        assert id_map.get("5B00676D79306EA2") == "welcome"

    def test_quest_to_chapter_map(self):
        chapters_dir = TEST_DATA / "chapters"
        item_map = _build_quest_to_chapter_map(chapters_dir)
        assert len(item_map) > 0
        # Quest 3BC0A50886A3222B should map to chapter 5B00676D79306EA2 (welcome)
        assert item_map.get("3BC0A50886A3222B") == "5B00676D79306EA2"


@pytest.mark.skipif(
    not TEST_DATA.exists(),
    reason="ATM10 test data not available",
)
class TestSplitLangFiles:
    def test_split_produces_output(self, tmp_path):
        results = split_lang_files(TEST_DATA, tmp_path)
        assert len(results) > 0

        # Check that JSON files were created
        json_files = list(tmp_path.glob("*.json"))
        assert len(json_files) > 0

        # Check that welcome chapter was split
        welcome_files = [f for f in json_files if "welcome" in f.name]
        assert len(welcome_files) == 1

        # Verify JSON content
        with open(welcome_files[0], "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data) > 0
        # Should contain quest entries from welcome chapter
        quest_keys = [k for k in data if k.startswith("quest.")]
        assert len(quest_keys) > 0

    def test_split_includes_chapter_groups(self, tmp_path):
        results = split_lang_files(TEST_DATA, tmp_path)
        assert "en_us_chapter_group.json" in results

    def test_split_includes_reward_tables(self, tmp_path):
        results = split_lang_files(TEST_DATA, tmp_path)
        assert "en_us_reward_table.json" in results
