import test_utils
from constants import HSTEP
from layout import Layout, Text


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