import pytest
from constants import HSTEP
from document_layout import DocumentLayout
from parser import HTMLParser
from helpers import paint_tree
from css_parser import style


class TestLayout:
    def setup(self, html: str) -> list:
        tree = HTMLParser(html).parse()
        style(tree, [])
        document = DocumentLayout(tree)
        document.layout()
        display_list = []
        paint_tree(document, display_list)
        return display_list

    @pytest.mark.skip
    def test_h1_center_align(self):
        display_list = self.setup("<h1 class='title'>Test1 test2</h1>test3")
        assert len(display_list) == 3
        # Ensure title is centered
        word1 = display_list[0]
        assert word1.rect.left > HSTEP
        # Word 3 is outside of h1 tag so, should be right-aligned
        word3 = display_list[2]
        assert word3.rect.left == HSTEP

    def test_abbr_tag(self):
        display_list = self.setup("<abbr>json</abbr>")
        assert len(display_list) == 1
        word1 = display_list[0]
        assert word1.text == "JSON"
        assert word1.font.size == 12

    @pytest.mark.skip
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

    @pytest.mark.skip
    def test_soft_hyphen_removes_hyphen_if_word_fits(self):
        display_list = self.setup("super­cali­fragi­list&shy;ic­expi­ali­docious")
        assert len(display_list) == 1
        assert display_list[0].text == "super­cali­fragi­listic­expi­ali­docious"

    @pytest.mark.skip
    def test_soft_hyphen_handles_multiple_hyphens(self):
        display_list = self.setup(
            "super­cali­fragi­listic­expi­ali­docious&shy;aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa&shy;bbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        )
        assert len(display_list) == 3
        assert display_list[0].text == "super­cali­fragi­listic­expi­ali­docious-"
        assert display_list[1].text == "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-"
        assert display_list[2].text == "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
