from parser import Element, Text
from typing import Optional, Tuple

from constants import INHERTIED_PROPERTIES


class Selector:
    def __init__(self):
        self.priority = 1

    def matches(self, node):
        pass


class TagSelector(Selector):
    def __init__(self, tag: str):
        self.tag: str = tag
        self.priority: int = 1

    def matches(self, node) -> bool:
        return isinstance(node, Element) and self.tag == node.tag


class ClassSelector(Selector):
    def __init__(self, cls: str, tag: Optional[str] = None):
        self.cls: str = cls
        self.priority: int = 0
        self.tag: Optional[str] = tag

    def matches(self, node) -> bool:
        tag_matches = (
            self.tag is not None and isinstance(node, Element) and node.tag == self.tag
        ) or not self.tag
        return (
            isinstance(node, Element)
            and node.attributes is not None
            and node.attributes.get("class") == self.cls
            and tag_matches
        )


class DescendantSelector(Selector):
    def __init__(self, ancestor: Selector, descendant: Selector):
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
            except Exception:
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

    def selector(self) -> Selector:
        out: Selector
        word = self.word()
        if "." in word:
            tag, cls = word.split(".", 1)
            out = ClassSelector(cls=cls.casefold(), tag=tag.casefold() if tag else None)
        else:
            out = TagSelector(word.casefold())
        self.whitespace()
        while self.i < len(self.s) and self.s[self.i] != "{":
            tag = self.word()
            descendant = TagSelector(tag.casefold())
            out = DescendantSelector(out, descendant)
            self.whitespace()
        return out

    def parse(self) -> list:
        rules: list[Tuple[Selector, dict]] = []
        while self.i < len(self.s):
            try:
                self.whitespace()
                selector: Selector = self.selector()
                self.literal("{")
                self.whitespace()
                body: dict = self.body()
                self.literal("}")
                rules.append((selector, body))
            except Exception:
                why = self.ignore_until(["}"])
                if why == "}":
                    self.literal("}")
                    self.whitespace()
                else:
                    break
        return rules


def style(node: Element | Text, rules: list[Tuple[Selector, dict]]):
    node.style = {}

    for property, default_value in INHERTIED_PROPERTIES.items():
        if node.parent:
            node.style[property] = node.parent.style[property]
        else:
            node.style[property] = default_value

    for selector, body in rules:
        if not selector.matches(node):
            continue
        for property, value in body.items():
            node.style[property] = value

    if isinstance(node, Element) and node.attributes and "style" in node.attributes:
        pairs: dict = CSSParser(node.attributes["style"]).body()
        for property, value in pairs.items():
            node.style[property] = value

    if node.style["font-size"].endswith("%"):
        if node.parent:
            parent_font_size = node.parent.style["font-size"]
        else:
            parent_font_size = INHERTIED_PROPERTIES["font-size"]
        node_pct: float = float(node.style["font-size"][:-1]) / 100
        parent_px: float = float(parent_font_size[:-2])
        node.style["font-size"] = f"{str(node_pct * parent_px)}px"

    if isinstance(node, Element) and node.tag in ["pre", "code"]:
        node.style["font-family"] = "Courier New"

    for child in node.children:
        style(child, rules)
