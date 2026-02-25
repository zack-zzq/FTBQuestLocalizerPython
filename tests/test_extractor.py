"""Tests for extractor module."""

from __future__ import annotations

import json
import os
from collections import OrderedDict
from pathlib import Path

import pytest

from ftb_quest_localizer.extractor import (
    _extract_from_dict,
    _should_skip,
)


class TestShouldSkip:
    def test_empty_string(self):
        assert _should_skip("") is True

    def test_whitespace_only(self):
        assert _should_skip("   ") is True

    def test_image_reference(self):
        assert _should_skip("{image:abc123:texture.png}") is True

    def test_pagebreak(self):
        assert _should_skip("{@pagebreak}") is True

    def test_normal_text(self):
        assert _should_skip("Hello World") is False

    def test_text_with_color_codes(self):
        assert _should_skip("&6Golden Text") is False


class TestExtractFromDict:
    def test_extract_title(self):
        data = {"title": "My Quest", "id": "ABC"}
        lang = OrderedDict()
        _extract_from_dict(data, "test", lang)
        assert lang["test.title"] == "My Quest"
        assert data["title"] == "{test.title}"

    def test_extract_description_list(self):
        data = {"description": ["Line 1", "Line 2"]}
        lang = OrderedDict()
        _extract_from_dict(data, "test", lang)
        assert lang["test.description0"] == "Line 1"
        assert lang["test.description1"] == "Line 2"
        assert data["description"][0] == "{test.description0}"
        assert data["description"][1] == "{test.description1}"

    def test_single_line_list(self):
        data = {"description": ["Only line"]}
        lang = OrderedDict()
        _extract_from_dict(data, "test", lang)
        assert lang["test.description"] == "Only line"

    def test_skip_image_in_list(self):
        data = {"description": ["{image:abc:texture.png}", "Normal text"]}
        lang = OrderedDict()
        _extract_from_dict(data, "test", lang)
        # Image should be skipped
        assert "test.description0" not in lang
        assert lang["test.description1"] == "Normal text"

    def test_skip_empty_field(self):
        data = {"title": ""}
        lang = OrderedDict()
        _extract_from_dict(data, "test", lang)
        assert len(lang) == 0

    def test_non_translatable_fields_ignored(self):
        data = {"id": "ABC", "x": 1.0, "y": 2.0}
        lang = OrderedDict()
        _extract_from_dict(data, "test", lang)
        assert len(lang) == 0

    def test_multiple_fields(self):
        data = {
            "title": "Quest Title",
            "subtitle": "Quest Subtitle",
            "description": ["Desc line"],
        }
        lang = OrderedDict()
        _extract_from_dict(data, "test", lang)
        assert lang["test.title"] == "Quest Title"
        assert lang["test.subtitle"] == "Quest Subtitle"
        assert lang["test.description"] == "Desc line"

    def test_hover_text_extraction(self):
        data = {
            "images": [
                {"hover": ["Join Discord!"], "image": "texture.png"},
            ]
        }
        lang = OrderedDict()
        _extract_from_dict(data, "test", lang)
        assert lang["test.images0.hover0"] == "Join Discord!"
