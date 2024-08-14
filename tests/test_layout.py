from constants import HSTEP
from document_layout import DocumentLayout
from parser import HTMLParser
from browser import paint_tree


class TestLayout:
    def setup(self, html: str, rtl: bool = False) -> list:
        tree = HTMLParser(html).parse()
        document = DocumentLayout(tree, rtl=rtl)
        document.layout()
        display_list = []
        paint_tree(document, display_list)
        return display_list

    def test_rtl(self):
        display_list = self.setup("<head><p>Test1 test2</p>", rtl=True)
        assert len(display_list) == 2
        word1 = display_list[0]

        # x coordinate of first word should be offset
        assert word1.left > HSTEP
        assert word1.text == "Test1"

        word2 = display_list[1]
        # Word 2 should lay out after word 1
        assert word2.left > word1.left
        assert word2.text == "test2"

    def test_h1_center_align(self):
        display_list = self.setup("<h1 class='title'>Test1 test2</h1>test3")
        assert len(display_list) == 2
        # Ensure title is centered
        word1 = display_list[0]
        assert word1.left > HSTEP
        # Word 3 is outside of h1 tag so, should be right-aligned
        word3 = display_list[1]
        assert word3.left == HSTEP

    def test_abbr_tag(self):
        display_list = self.setup("<abbr>json</abbr>")
        assert len(display_list) == 1
        word1 = display_list[0]
        assert word1.text == "JSON"
        assert word1.font.size == 10
        assert word1.font.weight == "bold"

    def test_abbr_tag_respects_mixed_casing(self):
        # This doesn't pass the specifications in the exercise, as it
        # still bolds the uppercase letters in e.g. JsOn
        display_list = self.setup("<head><abbr>JsOn 123</abbr>")
        assert len(display_list) == 2
        word1 = display_list[0]
        assert word1.text == "JSON"
        assert word1.font.weight == "bold"
        word2 = display_list[1]
        assert word2.font.weight == "normal"

    def test_soft_hyphen_breaks_long_line(self):
        display_list = self.setup(
            "super­cali­fragi­listic­expi­ali­docious&shy;aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        )
        assert len(display_list) == 2
        assert display_list[0].text == "super­cali­fragi­listic­expi­ali­docious-"
        assert display_list[1].text == "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        # Both words should start at the beginning of the line
        assert display_list[0].left == display_list[1].left
        assert display_list[0].bottom < display_list[1].bottom

    def test_soft_hyphen_removes_hyphen_if_word_fits(self):
        display_list = self.setup("super­cali­fragi­list&shy;ic­expi­ali­docious")
        assert len(display_list) == 1
        assert display_list[0].text == "super­cali­fragi­listic­expi­ali­docious"

    def test_soft_hyphen_handles_multiple_hyphens(self):
        display_list = self.setup(
            "super­cali­fragi­listic­expi­ali­docious&shy;aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa&shy;bbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        )
        assert len(display_list) == 3
        assert display_list[0].text == "super­cali­fragi­listic­expi­ali­docious-"
        assert display_list[1].text == "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-"
        assert display_list[2].text == "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"

    def test_pre_tag_uses_monospaced_font(self):
        display_list = self.setup("<pre>def get_font(self):</pre>")
        assert len(display_list) == 2
        assert display_list[1].font.family == "Courier New"

    def test_pre_tag_maintains_whitespace(self):
        display_list = self.setup("<pre>def get_font(self):               return</pre")
        assert len(display_list) == 2
        assert display_list[1].text == "def get_font(self):               return"

    def test_pre_tag_maintains_nested_tags(self):
        display_list = self.setup("<pre>def get_font(self):<b>return</b></pre>")
        assert len(display_list) == 3
        assert display_list[2].font.weight == "bold"
        assert display_list[2].font.family == "Courier New"
