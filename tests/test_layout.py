import test_utils
from constants import HSTEP, SCROLLBAR_WIDTH
from layout import Layout, Text, Tag


class TestLayout:
    def test_rtl(self):
        text = [Text("Test1"), Text("test2")]
        layout = Layout(text, rtl=True)
        assert len(layout.display_list) == 2
        word1 = layout.display_list[0]

        # x coordinate of first word should be offset
        assert word1.x > HSTEP
        assert word1.text == "Test1"

        word2 = layout.display_list[1]
        # Word 2 should lay out after word 1
        assert word2.x > word1.x
        assert word2.text == "test2"

    def test_h1_center_align(self):
        text = [
            Tag('h1 class="title"'),
            Text("Test1"),
            Text("test2"),
            Tag("/h1"),
            Text("test3"),
        ]
        layout = Layout(text)
        assert len(layout.display_list) == 3
        # First word is the title, ensure it's centered
        word1 = layout.display_list[0]
        assert word1.x > HSTEP
        # Word 3 is outside of h1 tag so, should be right-aligned
        word3 = layout.display_list[2]
        assert word3.x == HSTEP

    def test_abbr_tag(self):
        text = [Tag("abbr"), Text("json"), Tag("/abbr")]
        layout = Layout(text)
        assert len(layout.display_list) == 1
        word1 = layout.display_list[0]
        assert word1.text == "JSON"
        assert word1.font.size == 10
        assert word1.font.weight == "bold"

    def test_soft_hyphen_breaks_long_line(self):
        text = [
            Text(
                "super­cali­fragi­listic­expi­ali­docious&shy;aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            )
        ]
        layout = Layout(text)
        assert len(layout.display_list) == 2
        assert (
            layout.display_list[0].text == "super­cali­fragi­listic­expi­ali­docious-"
        )
        assert layout.display_list[1].text == "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        # Both words should start at the beginning of the line
        assert layout.display_list[0].x == layout.display_list[1].x
        assert layout.display_list[0].y < layout.display_list[1].y

    def test_soft_hyphen_removes_hyphen_if_word_fits(self):
        text = [Text("super­cali­fragi­list&shy;ic­expi­ali­docious")]
        layout = Layout(text)
        assert len(layout.display_list) == 1
        assert layout.display_list[0].text == "super­cali­fragi­listic­expi­ali­docious"

    def test_soft_hyphen_handles_multiple_hyphens(self):
        text = [
            Text(
                "super­cali­fragi­listic­expi­ali­docious&shy;aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa&shy;bbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
            )
        ]
        layout = Layout(text)
        assert len(layout.display_list) == 3
        assert (
            layout.display_list[0].text == "super­cali­fragi­listic­expi­ali­docious-"
        )
        assert layout.display_list[1].text == "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-"
        assert layout.display_list[2].text == "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"

    def test_pre_tag_uses_monospaced_font(self):
        layout = Layout([Tag("pre"), Text("def get_font(self):"), Tag("/pre")])
        assert len(layout.display_list) == 1
        assert layout.display_list[0].font.family == "Courier New"

    def test_pre_tag_maintains_whitespace(self):
        layout = Layout(
            [Tag("pre"), Text("def get_font(self):               return"), Tag("/pre")]
        )
        assert len(layout.display_list) == 1
        assert layout.display_list[0].text == "def get_font(self):               return"

    def test_pre_tag_maintains_nested_tags(self):
        layout = Layout(
            [
                Tag("pre"),
                Text("def get_font(self):"),
                Tag("b"),
                Text("return"),
                Tag("/b"),
                Tag("/pre"),
            ]
        )
        assert len(layout.display_list) == 2
        assert layout.display_list[1].font.weight == "bold"
        assert layout.display_list[1].font.family == "Courier New"
