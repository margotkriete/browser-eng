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
