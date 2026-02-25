"""Tests for merger module."""

from __future__ import annotations

import json
from collections import OrderedDict
from pathlib import Path

import pytest

from ftb_quest_localizer.merger import (
    merge_json_to_lang_dir,
    _get_top_level_file,
    _extract_json_chapter_name,
)


class TestGetTopLevelFile:
    def test_chapter_key(self):
        assert _get_top_level_file("chapter.ABC.title") == "chapter.snbt"

    def test_chapter_group_key(self):
        assert _get_top_level_file("chapter_group.ABC.title") == "chapter_group.snbt"

    def test_reward_table_key(self):
        assert _get_top_level_file("reward_table.ABC.title") == "reward_table.snbt"

    def test_file_key(self):
        assert _get_top_level_file("file.ABC.title") == "file.snbt"

    def test_quest_key_not_top_level(self):
        assert _get_top_level_file("quest.ABC.title") is None

    def test_task_key_not_top_level(self):
        assert _get_top_level_file("task.ABC.title") is None


class TestExtractJsonChapterName:
    def test_simple(self):
        assert _extract_json_chapter_name("en_us_welcome.json") == "welcome"

    def test_with_underscores(self):
        assert _extract_json_chapter_name("en_us_ice__fire.json") == "ice__fire"

    def test_different_locale(self):
        assert _extract_json_chapter_name("zh_cn_welcome.json") == "welcome"


class TestMergeJsonToLangDir:
    def test_top_level_files(self, tmp_path):
        """Test merging produces separate SNBT files for top-level categories."""
        json_dir = tmp_path / "json"
        json_dir.mkdir()

        for name, prefix in [("chapter_group", "chapter_group"), ("file", "file")]:
            data = OrderedDict([(f"{prefix}.ABC.title", f"{name} Title")])
            with open(json_dir / f"en_us_{name}.json", "w", encoding="utf-8") as f:
                json.dump(data, f)

        output_dir = tmp_path / "zh_cn"
        count = merge_json_to_lang_dir(json_dir, output_dir)

        assert count == 2
        assert (output_dir / "chapter_group.snbt").exists()
        assert (output_dir / "file.snbt").exists()

    def test_chapter_files_go_to_chapters_dir(self, tmp_path):
        """Test that non-category JSON files go to chapters/ subdirectory."""
        json_dir = tmp_path / "json"
        json_dir.mkdir()

        data = OrderedDict([("quest.ABC.title", "Quest Title")])
        with open(json_dir / "en_us_welcome.json", "w", encoding="utf-8") as f:
            json.dump(data, f)

        output_dir = tmp_path / "zh_cn"
        count = merge_json_to_lang_dir(json_dir, output_dir)

        assert count == 1
        assert (output_dir / "chapters" / "welcome.snbt").exists()

    def test_multi_line_reconstruction(self, tmp_path):
        """Test that numbered keys are merged back into lists in SNBT."""
        json_dir = tmp_path / "json"
        json_dir.mkdir()

        data = OrderedDict([
            ("chapter.ABC.chapter_subtitle1", "Line 1"),
            ("chapter.ABC.chapter_subtitle2", "Line 2"),
        ])
        with open(json_dir / "en_us_chapter.json", "w", encoding="utf-8") as f:
            json.dump(data, f)

        output_dir = tmp_path / "output"
        merge_json_to_lang_dir(json_dir, output_dir)

        content = (output_dir / "chapter.snbt").read_text(encoding="utf-8")
        assert "chapter.ABC.chapter_subtitle" in content

    def test_empty_dir_raises(self, tmp_path):
        json_dir = tmp_path / "empty"
        json_dir.mkdir()
        with pytest.raises(FileNotFoundError):
            merge_json_to_lang_dir(json_dir, tmp_path / "output")

    def test_nonexistent_dir_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            merge_json_to_lang_dir(tmp_path / "nonexistent", tmp_path / "output")

    def test_unicode(self, tmp_path):
        json_dir = tmp_path / "json"
        json_dir.mkdir()

        data = OrderedDict([("chapter.ABC.title", "欢迎来到 ATM10！")])
        with open(json_dir / "en_us_chapter.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

        output_dir = tmp_path / "zh_cn"
        merge_json_to_lang_dir(json_dir, output_dir)
        content = (output_dir / "chapter.snbt").read_text(encoding="utf-8")
        assert "欢迎来到 ATM10" in content


# Path to ATM10 test data
TEST_DATA = Path(__file__).parent.parent / "output" / "config" / "ftbquests" / "quests"


@pytest.mark.skipif(not TEST_DATA.exists(), reason="ATM10 test data not available")
class TestMergeRoundTrip:
    """Split then merge and verify structure matches original."""

    def test_round_trip_structure(self, tmp_path):
        from ftb_quest_localizer.splitter import split_lang_files

        json_dir = tmp_path / "json"
        split_lang_files(TEST_DATA, json_dir)

        output_dir = tmp_path / "merged"
        count = merge_json_to_lang_dir(json_dir, output_dir)

        assert count > 0
        assert (output_dir / "chapter.snbt").exists()
        assert (output_dir / "chapter_group.snbt").exists()
        assert (output_dir / "file.snbt").exists()
        assert (output_dir / "reward_table.snbt").exists()
        assert (output_dir / "chapters").is_dir()

        chapter_files = list((output_dir / "chapters").glob("*.snbt"))
        assert len(chapter_files) > 0
        assert any("welcome" in f.name for f in chapter_files)
