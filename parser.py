import re
from typing import Optional, Tuple


class Text:
    def __init__(self, text: str, parent):
        self.text: str = text
        self.children = []
        self.parent = parent

    def __repr__(self):
        return repr(self.text)


class Element:
    def __init__(self, tag: str, attributes: dict, parent):
        self.tag = tag
        self.children = []
        self.parent = parent
        self.attributes = attributes

    def __repr__(self):
        return f"<{self.tag}>"


class HTMLParser:
    SELF_CLOSING_TAGS = [
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    ]
    HEAD_TAGS = [
        "base",
        "basefont",
        "bgsound",
        "noscript",
        "link",
        "meta",
        "title",
        "style",
        "script",
    ]

    def __init__(self, body: str, view_source: bool = False) -> None:
        self.body: str = body
        self.unfinished = []
        self.view_source: bool = view_source

    def implicit_tags(self, tag: Optional[str] = None) -> None:
        while True:
            open_tags = [node.tag for node in self.unfinished]
            if open_tags == [] and tag != "html":
                self.add_tag("html")
            elif open_tags == ["html"] and tag not in ["head", "body", "/html"]:
                if tag in self.HEAD_TAGS:
                    self.add_tag("head")
                else:
                    self.add_tag("body")
            elif (
                open_tags == ["html", "head"] and tag not in ["/head"] + self.HEAD_TAGS
            ):
                self.add_tag("/head")
            else:
                break

    def get_attributes(self, text: str) -> Tuple[str, dict]:
        parts: str = text.split()
        tag = parts[0].casefold()
        attributes: dict = {}
        for attrpair in parts[1:]:
            if "=" in attrpair:
                key, value = attrpair.split("=", 1)
                # fmt: off
                if len(value) > 2 and value[0] in ["'", '\"']:
                    value = value[1:-1]
                attributes[key.casefold()] = value
            else:
                attributes[attrpair.casefold()] = ""
        return tag, attributes

    def parse(
        self,
    ) -> list[Element | Text]:
        text: str = ""
        in_tag = False

        title = re.search("<title>(.*)</title>", self.body)
        title_text = ""
        if title:
            title_text = title.group(1)
        self.body = self.body.replace(title_text, "")

        if self.view_source:
            self.add_text(text)
            return self.finish()

        for c in self.body:
            if c == "<":
                in_tag = True  # word is in between < >
                if text:
                    self.add_text(text)
                text = ""
            elif c == ">":
                in_tag = False
                self.add_tag(text)
                text = ""
            else:
                text += c
        if not in_tag and text:
            self.add_text(text)
        return self.finish()

    def add_text(self, text: str) -> None:
        if text.isspace():
            return
        self.implicit_tags(None)
        # Add text as a child of the last unfinished node
        parent = self.unfinished[-1]
        node: Text = Text(text, parent)
        parent.children.append(node)

    def add_tag(self, tag: str) -> None:
        tag, attributes = self.get_attributes(tag)
        if tag.startswith("!"):
            return
        self.implicit_tags(tag)
        if tag.startswith("/"):
            if len(self.unfinished) == 1:
                return
            # Close tags finish last unfinished node by adding
            # it to the previous unfinished node
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
        elif tag in self.SELF_CLOSING_TAGS:
            parent = self.unfinished[-1]
            node: Element = Element(tag=tag, attributes=attributes, parent=parent)
            parent.children.append(node)
        else:
            parent: Element | Text | None = (
                self.unfinished[-1] if self.unfinished else None
            )
            node: Element = Element(tag=tag, attributes=attributes, parent=parent)
            self.unfinished.append(node)

    def finish(self) -> Element | Text:
        if not self.unfinished:
            self.implicit_tags(None)
        while len(self.unfinished) > 1:
            node: Element | Text = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
        return self.unfinished.pop()


def print_tree(node, indent: int = 0):
    print(" " * indent, node)
    for child in node.children:
        print_tree(child, indent + 1)
