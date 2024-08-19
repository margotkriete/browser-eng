from constants import INHERTIED_PROPERTIES
from parser import Element, Text


class TagSelector:
    def __init__(self, tag: str):
        self.tag: str = tag
        self.priority: int = 1

    def matches(self, node) -> bool:
        return isinstance(node, Element) and self.tag == node.tag


class DescendantSelector:
    def __init__(self, ancestor: Element | Text, descendant: Element | Text):
        self.ancestor = ancestor
        self.descendant = descendant
        self.priority: int = ancestor.priority + descendant.priority

    def matches(self, node: Element | Text) -> bool:
        if not self.descendant.matches(node):
            return False
        while node.parent:
            if self.ancestor.matches(node.parent):
                return True
            node = node.parent
        return False


class CSSParser:
    def __init__(self, s: str) -> None:
        self.s: str = s
        self.i: int = 0

    def whitespace(self) -> None:
        while self.i < len(self.s) and self.s[self.i].isspace():
            self.i += 1

    def word(self) -> str:
        start: int = self.i
        while self.i < len(self.s):
            if self.s[self.i].isalnum() or self.s[self.i] in "#-.%":
                self.i += 1
            else:
                break
        if not (self.i > start):
            raise Exception(f"parsing error: i = {self.i}, start = {start}")
        return self.s[start : self.i]

    def literal(self, literal):
        if not (self.i < len(self.s) and self.s[self.i] == literal):
            raise Exception(f"parsing error: i = {self.i}, literal = {literal}")
        self.i += 1

    def pair(self) -> tuple[str, str]:
        prop: str = self.word()
        self.whitespace()
        self.literal(":")
        self.whitespace()
        val: str = self.word()
        return prop.casefold(), val

    def body(self) -> dict:
        pairs = {}
        while self.i < len(self.s) and self.s[self.i] != "}":
            try:
                prop, val = self.pair()
                pairs[prop.casefold()] = val
                self.whitespace()
                self.literal(";")
                self.whitespace()
            except Exception as e:
                # print(f"exception: {e}")
                why = self.ignore_until([";", "}"])
                if why == ";":
                    self.literal(";")
                    self.whitespace()
                else:
                    break
        return pairs

    def ignore_until(self, chars: list[str]) -> str | None:
        while self.i < len(self.s):
            if self.s[self.i] in chars:
                return self.s[self.i]
            else:
                self.i += 1
        return None

    def selector(self) -> TagSelector | DescendantSelector:
        out = TagSelector(self.word().casefold())
        self.whitespace()
        while self.i < len(self.s) and self.s[self.i] != "{":
            tag: str = self.word()
            descendant = TagSelector(tag.casefold())
            out = DescendantSelector(out, descendant)
            self.whitespace()
        return out

    def parse(self) -> list:
        rules: list = []
        while self.i < len(self.s):
            try:
                self.whitespace()
                selector: TagSelector | DescendantSelector = self.selector()
                self.literal("{")
                self.whitespace()
                body: dict = self.body()
                self.literal("}")
                rules.append((selector, body))
            except Exception as e:
                # print(f"exception in parse(): {e}")
                why = self.ignore_until(["}"])
                if why == "}":
                    self.literal("}")
                    self.whitespace()
                else:
                    break
        return rules


def style(node: Element | Text, rules: list):
    node.style = {}

    for property, default_value in INHERTIED_PROPERTIES.items():
        if node.parent:
            node.style[property] = node.parent.style[property]
        else:
            node.style[property] = default_value

    # style attribute should override style sheet values
    if isinstance(node, Element) and "style" in node.attributes:
        pairs: dict = CSSParser(node.attributes["style"]).body()
        for property, value in pairs.items():
            node.style[property] = value

    for selector, body in rules:
        if not selector.matches(node):
            continue
        for property, value in body.items():
            node.style[property] = value

    if node.style["font-size"].endswith("%"):
        if node.parent:
            parent_font_size = node.parent.style["font-size"]
        else:
            parent_font_size = INHERTIED_PROPERTIES["font-size"]
        node_pct: float = float(node.style["font-size"][:-1]) / 100
        parent_px: float = float(parent_font_size[:-2])
        node.style["font-size"] = f"{str(node_pct * parent_px)}px"

    for child in node.children:
        style(child, rules)
