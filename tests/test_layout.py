from constants import HSTEP
from block_layout import BlockLayout
from parser import Text, Element, HTMLParser


class TestLayout:
    def test_rtl(self):
        tree = HTMLParser("<head><p>Test1 test2</p>").parse()
        layout = BlockLayout(tree, rtl=True)
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
        tree = HTMLParser("<head><h1 class='title'>Test1 test2</h1>test3").parse()
        layout = BlockLayout(tree)
        assert len(layout.display_list) == 3
        # Ensure title is centered
        word1 = layout.display_list[0]
        assert word1.x > HSTEP
        # Word 3 is outside of h1 tag so, should be right-aligned
        word3 = layout.display_list[2]
        assert word3.x == HSTEP

    def test_abbr_tag(self):
        tree = HTMLParser("<head><abbr>json</abbr>").parse()
        layout = BlockLayout(tree)
        assert len(layout.display_list) == 1
        word1 = layout.display_list[0]
        assert word1.text == "JSON"
        assert word1.font.size == 10
        assert word1.font.weight == "bold"

    def test_abbr_tag_respects_mixed_casing(self):
        # This doesn't pass the specifications in the exercise, as it
        # still bolds the uppercase letters in e.g. JsOn
        tree = HTMLParser("<head><abbr>JsOn 123</abbr>").parse()
        layout = BlockLayout(tree)
        assert len(layout.display_list) == 2
        word1 = layout.display_list[0]
        assert word1.text == "JSON"
        assert word1.font.weight == "bold"
        word2 = layout.display_list[1]
        assert word2.font.weight == "normal"

    def test_soft_hyphen_breaks_long_line(self):
        tree = HTMLParser(
            "super­cali­fragi­listic­expi­ali­docious&shy;aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        ).parse()
        layout = BlockLayout(tree)
        assert len(layout.display_list) == 2
        assert (
            layout.display_list[0].text == "super­cali­fragi­listic­expi­ali­docious-"
        )
        assert layout.display_list[1].text == "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        # Both words should start at the beginning of the line
        assert layout.display_list[0].x == layout.display_list[1].x
        assert layout.display_list[0].y < layout.display_list[1].y

    def test_soft_hyphen_removes_hyphen_if_word_fits(self):
        tree = HTMLParser("super­cali­fragi­list&shy;ic­expi­ali­docious").parse()
        layout = BlockLayout(tree)
        assert len(layout.display_list) == 1
        assert layout.display_list[0].text == "super­cali­fragi­listic­expi­ali­docious"

    def test_soft_hyphen_handles_multiple_hyphens(self):
        tree = HTMLParser(
            "super­cali­fragi­listic­expi­ali­docious&shy;aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa&shy;bbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        ).parse()
        layout = BlockLayout(tree)
        assert len(layout.display_list) == 3
        assert (
            layout.display_list[0].text == "super­cali­fragi­listic­expi­ali­docious-"
        )
        assert layout.display_list[1].text == "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-"
        assert layout.display_list[2].text == "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"

    def test_pre_tag_uses_monospaced_font(self):
        tree = HTMLParser("<pre>def get_font(self):</pre>").parse()
        layout = BlockLayout(tree)
        assert len(layout.display_list) == 1
        assert layout.display_list[0].font.family == "Courier New"

    def test_pre_tag_maintains_whitespace(self):
        tree = HTMLParser("<pre>def get_font(self):               return</pre").parse()
        layout = BlockLayout(tree)
        assert len(layout.display_list) == 1
        assert layout.display_list[0].text == "def get_font(self):               return"

    def test_pre_tag_maintains_nested_tags(self):
        tree = HTMLParser("<pre>def get_font(self):<b>return</b></pre").parse()
        layout = BlockLayout(tree)
        assert len(layout.display_list) == 2
        assert layout.display_list[1].font.weight == "bold"
        assert layout.display_list[1].font.family == "Courier New"
