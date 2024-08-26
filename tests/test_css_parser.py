from css_parser import CSSParser, ClassSelector, DescendantSelector, TagSelector


class TestCSSParser:
    def test_parses_tag_selector(self):
        rules = CSSParser("a { color: blue; }").parse()
        assert len(rules) == 1
        selector, body = rules[0]
        assert isinstance(selector, TagSelector)
        assert selector.tag == "a"
        assert isinstance(body, dict)
        assert body.get("color") == "blue"

    def test_parses_descendant_selector(self):
        rules = CSSParser("div a { color: blue; }").parse()
        assert len(rules) == 1
        selector, body = rules[0]
        assert isinstance(selector, DescendantSelector)
        assert isinstance(selector.ancestor, TagSelector)
        assert selector.ancestor.tag == "div"
        assert selector.descendant.tag == "a"
        assert isinstance(body, dict)
        assert body.get("color") == "blue"

    def test_parses_class_selector(self):
        rules = CSSParser(".main { color: blue; }").parse()
        assert len(rules) == 1
        selector, body = rules[0]
        assert isinstance(selector, ClassSelector)
        assert selector.cls == "main"
        assert selector.tag is None
        assert isinstance(body, dict)
        assert body.get("color") == "blue"

    def test_parses_class_selector_with_tag(self):
        rules = CSSParser("p.main { color: blue; }").parse()
        assert len(rules) == 1
        selector, body = rules[0]
        assert isinstance(selector, ClassSelector)
        assert selector.cls == "main"
        assert selector.tag == "p"
        assert isinstance(body, dict)
        assert body.get("color") == "blue"
