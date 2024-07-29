import pytest
from parser import HTMLParser


class TestParser:
    @pytest.mark.parametrize(
        "input", ["test", "<body>test", "<html><body>test</body></html>"]
    )
    def test_parses_tags_and_adds_missing(self, input):
        parsed = HTMLParser(input).parse()
        assert str(parsed) == "<html>"
        assert len(parsed.children) == 1
        child = parsed.children[0]
        assert str(child) == "<body>"
        assert len(child.children) == 1
        assert child.children[0].text == "test"

    def test_head_tags_placed_in_head(self):
        parsed = HTMLParser(
            "<base><basefont></basefont><title></title><div></div>"
        ).parse()
        assert str(parsed) == "<html>"

        # <html> should have <head> and <body> nested beneath
        assert len(parsed.children) == 2
        head_tag = parsed.children[0]
        assert str(head_tag) == "<head>"
        assert len(head_tag.children) == 3
        assert str(head_tag.children[0]) == "<base>"
        assert str(head_tag.children[1]) == "<basefont>"
        assert str(head_tag.children[2]) == "<title>"
        body_tag = parsed.children[1]
        assert str(body_tag) == "<body>"
        assert len(body_tag.children) == 1
        assert str(body_tag.children[0]) == "<div>"

    def test_skips_creating_nodes_for_comments(self):
        parsed = HTMLParser("<div><!-- ab<>cd !--></div>").parse()
        assert str(parsed) == "<html>"
        assert len(parsed.children) == 1
        child = parsed.children[0]
        assert str(child) == "<body>"
        assert len(child.children) == 1
        assert str(child.children[0]) == "<div>"
        div = child.children[0]
        assert len(div.children) == 0
