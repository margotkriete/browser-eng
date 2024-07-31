import pytest
from parser import HTMLParser


class TestParser:
    @pytest.mark.parametrize(
        "input", ["test", "<body>test", "<html><body>test</body></html>"]
    )
    def test_parses_tags_and_adds_missing(self, input):
        parsed = HTMLParser(input).parse()
        assert parsed.tag == "html"
        assert len(parsed.children) == 1
        child = parsed.children[0]
        assert child.tag == "body"
        assert len(child.children) == 1
        assert child.children[0].text == "test"

    def test_head_tags_placed_in_head(self):
        parsed = HTMLParser(
            "<base><basefont></basefont><title></title><div></div>"
        ).parse()
        assert parsed.tag == "html"
        # <html> should have <head> and <body> nested beneath
        assert len(parsed.children) == 2
        head_tag = parsed.children[0]
        assert head_tag.tag == "head"
        assert len(head_tag.children) == 3
        assert head_tag.children[0].tag == "base"
        assert head_tag.children[1].tag == "basefont"
        assert head_tag.children[2].tag == "title"
        body_tag = parsed.children[1]
        assert body_tag.tag == "body"
        assert len(body_tag.children) == 1
        assert body_tag.children[0].tag == "div"

    def test_skips_creating_nodes_for_comments(self):
        parsed = HTMLParser("<div><!-- ab<>cd--></div>").parse()
        assert parsed.tag == "html"
        assert len(parsed.children) == 1
        child = parsed.children[0]
        assert child.tag == "body"
        assert len(child.children) == 1
        assert child.children[0].tag == "div"
        div = child.children[0]
        assert len(div.children) == 0

    def test_comments_ignored_when_adjacent_to_elements(self):
        parsed = HTMLParser(
            "<div><!-- ab<>cd-->test<!--comment--></div><p>test2</p>"
        ).parse()
        assert parsed.tag == "html"
        assert len(parsed.children) == 1
        child = parsed.children[0]
        assert child.tag == "body"
        assert len(child.children) == 2
        assert child.children[0].tag == "div"
        div = child.children[0]
        p = child.children[1]
        assert div.children[0].text == "test"
        assert p.children[0].text == "test2"
