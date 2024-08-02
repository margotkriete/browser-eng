import pytest
from parser import HTMLParser


class TestParser:
    @pytest.mark.parametrize(
        "input", ["test", "<body>test", "<html><body>test</body></html>"]
    )
    def test_parses_tags_and_adds_missing(self, input):
        parsed = HTMLParser(input).parse()
        assert str(parsed) == "<html><body>'test'</body></html>"

    def test_places_title_in_missing_head_tag(self):
        parsed = HTMLParser(
            "<base><basefont></basefont><title></title><div></div>"
        ).parse()
        assert (
            str(parsed)
            == "<html><head><base><basefont></basefont><title></title></head><body><div></div></body></html>"
        )

    def test_skips_creating_nodes_for_comments(self):
        parsed = HTMLParser("<div><!-- ab<>cd--></div>").parse()
        assert str(parsed) == "<html><body><div></div></body></html>"

    def test_comments_ignored_when_adjacent_to_elements(self):
        parsed = HTMLParser(
            "<div><!-- ab<>cd-->test<!--comment--></div><p>test2</p>"
        ).parse()
        assert (
            str(parsed) == "<html><body><div>'test'</div><p>'test2'</p></body></html>"
        )
