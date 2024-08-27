from constants import HSTEP
from document_layout import DocumentLayout
from parser import HTMLParser
from browser import paint_tree
from css_parser import style


class TestLayout:
    def setup(self, html: str, rtl: bool = False) -> list:
        tree = HTMLParser(html).parse()
        style(tree, [])
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
        assert len(display_list) == 3
        word1 = display_list[0]
        assert word1.left > HSTEP
        # TODO: figure out why these tests differ from actual behavior
        # word3 = display_list[2]
        # assert word3.left == HSTEP

    def test_abbr_tag(self):
        display_list = self.setup("<abbr>json</abbr>")
        assert len(display_list) == 1
        word1 = display_list[0]
        assert word1.text == "JSON"
        assert word1.font.size == 12

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
