"""Tests for snbt_parser module."""

from collections import OrderedDict

import pytest

from ftb_quest_localizer.snbt_parser import (
    escape_string_for_snbt,
    flatten_lang_data,
    unescape_string,
    unflatten_lang_data,
)


class TestUnescapeString:
    def test_escaped_quotes(self):
        assert unescape_string(r'hello \"world\"') == 'hello "world"'

    def test_escaped_backslash(self):
        assert unescape_string("hello\\\\world") == "hello\\world"

    def test_no_escapes(self):
        assert unescape_string("hello world") == "hello world"

    def test_combined(self):
        assert unescape_string(r'path\\to\\\"file\"') == 'path\\to\\"file"'

    def test_empty(self):
        assert unescape_string("") == ""


class TestEscapeStringForSnbt:
    def test_quotes(self):
        assert escape_string_for_snbt('hello "world"') == 'hello \\"world\\"'

    def test_backslash(self):
        assert escape_string_for_snbt("hello\\world") == "hello\\\\world"

    def test_no_special(self):
        assert escape_string_for_snbt("hello world") == "hello world"

    def test_empty(self):
        assert escape_string_for_snbt("") == ""


class TestFlattenLangData:
    def test_simple_string(self):
        data = OrderedDict([("chapter.123.title", "Hello")])
        result = flatten_lang_data(data)
        assert result == OrderedDict([("chapter.123.title", "Hello")])

    def test_list_expansion(self):
        data = OrderedDict([("quest.ABC.quest_desc", ["Line 1", "Line 2"])])
        result = flatten_lang_data(data)
        assert result == OrderedDict([
            ("quest.ABC.quest_desc1", "Line 1"),
            ("quest.ABC.quest_desc2", "Line 2"),
        ])

    def test_single_element_list(self):
        data = OrderedDict([("quest.ABC.quest_desc", ["Only line"])])
        result = flatten_lang_data(data)
        assert result == OrderedDict([("quest.ABC.quest_desc1", "Only line")])

    def test_single_element_flatten(self):
        data = OrderedDict([("quest.ABC.quest_desc", ["Only line"])])
        result = flatten_lang_data(data, flatten_single_lines=True)
        assert result == OrderedDict([("quest.ABC.quest_desc", "Only line")])

    def test_unescape_applied(self):
        data = OrderedDict([("key", r'hello \"world\"')])
        result = flatten_lang_data(data)
        assert result["key"] == 'hello "world"'

    def test_mixed_types(self):
        data = OrderedDict([
            ("string_key", "value"),
            ("list_key", ["a", "b"]),
            ("number_key", 42),
        ])
        result = flatten_lang_data(data)
        assert result["string_key"] == "value"
        assert result["list_key1"] == "a"
        assert result["list_key2"] == "b"
        assert result["number_key"] == 42

    def test_empty(self):
        result = flatten_lang_data(OrderedDict())
        assert result == OrderedDict()


class TestUnflattenLangData:
    def test_merge_numbered_keys(self):
        data = OrderedDict([
            ("quest.ABC.quest_desc1", "Line 1"),
            ("quest.ABC.quest_desc2", "Line 2"),
        ])
        result = unflatten_lang_data(data)
        assert result == OrderedDict([
            ("quest.ABC.quest_desc", ["Line 1", "Line 2"]),
        ])

    def test_preserves_non_numbered(self):
        data = OrderedDict([
            ("chapter.123.title", "Hello"),
        ])
        result = unflatten_lang_data(data)
        assert result == OrderedDict([("chapter.123.title", "Hello")])

    def test_sorts_by_number(self):
        data = OrderedDict([
            ("key3", "third"),
            ("key1", "first"),
            ("key2", "second"),
        ])
        result = unflatten_lang_data(data)
        assert result["key"] == ["first", "second", "third"]

    def test_round_trip(self):
        """flatten then unflatten should reconstruct original lists."""
        original = OrderedDict([
            ("quest.ABC.quest_desc", ["Line 1", "Line 2", "Line 3"]),
            ("chapter.123.title", "Hello"),
        ])
        flat = flatten_lang_data(original)
        result = unflatten_lang_data(flat)
        assert result["quest.ABC.quest_desc"] == ["Line 1", "Line 2", "Line 3"]
        assert result["chapter.123.title"] == "Hello"
