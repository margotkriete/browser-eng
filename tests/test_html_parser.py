import pytest
from parser import HTMLParser


class TestHTMLParser:
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

    def test_script_tag_does_not_create_child_nodes(self):
        parsed = HTMLParser("<script>window.load() => {}</script>").parse()
        assert (
            str(parsed)
            == "<html><head><script>'window.load() => {}'</script></head></html>"
        )

    def test_handles_attributes(self):
        parsed = HTMLParser("<p disabled id='1'>content</p>").parse()
        assert (
            str(parsed)
            == "<html><body><p disabled='' id='1'>'content'</p></body></html>"
        )

    def test_handles_quoted_attributes(self):
        parsed = HTMLParser("<div id='1' class='test > abcd'>content</div>").parse()
        assert (
            str(parsed)
            == "<html><body><div id='1' class='test > abcd'>'content'</div></body></html>"
        )
