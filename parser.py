import re
from typing import Optional, Tuple


class Text:
    def __init__(self, text: str, parent: "Element"):
        self.text: str = text
        self.children: list[Element | Text] = []
        self.parent: Element = parent

    def __repr__(self) -> str:
        return repr(self.text)


class Element:
    def __init__(
        self,
        tag: str,
        attributes: Optional[dict] = None,
        parent: Optional["Element"] = None,
    ):
        self.tag: str = tag
        self.children: list[Element | Text] = []
        self.parent: Optional[Element] = parent
        self.attributes: Optional[dict] = attributes

    def __repr__(self) -> str:
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
    SIBLING_TAGS = ["p", "li"]

    def replace_character_references(self, s: str) -> str:
        s = s.replace("&lt;", "<")
        s = s.replace("&gt;", ">")
        return s

    def __init__(self, body: str, view_source: bool = False) -> None:
        self.body: str = body
        self.unfinished: list[Element] = []
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
        parts: list[str] = text.split()
        tag: str = parts[0].casefold()
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

    def parse(self) -> Element | Text:
        title = re.search("<title>(.*)</title>", self.body)
        if title:
            self.body = self.body.replace(title.group(1), "")

        if self.view_source:
            self.add_text(self.body)
            return self.finish()

        self._parse_body()
        return self.finish()

    def _parse_body(self) -> None:
        text: str = ""
        in_tag, in_comment = False, False
        body_length = len(self.body)

        for i, c in enumerate(self.body):
            if c == "<":
                if in_comment:
                    continue
                if i + 4 < body_length and self.body[i + 1 : i + 4] == "!--":
                    in_comment = True
                in_tag = True
                if text:
                    self.add_text(text)
                text = ""
            elif c == ">":
                in_tag = False
                if i - 2 > 0 and self.body[i - 2 : i] == "--" and in_comment:
                    in_comment = False
                    text = ""
                    continue
                self.add_tag(text)
                text = ""
            else:
                text += c

        if not in_tag and text:
            self.add_text(text)

    def add_text(self, text: str) -> None:
        if text.isspace():
            return
        self.implicit_tags(None)
        text = self.replace_character_references(text)
        # Add text as a child of the last unfinished node
        parent: Element = self.unfinished[-1]
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
            # Close tags finish the last unfinished node by adding
            # it to the previous unfinished node
            node: Element = self.unfinished.pop()
            parent: Optional[Element] = self.unfinished[-1]
            if parent:
                parent.children.append(node)
        elif tag in self.SELF_CLOSING_TAGS:
            parent = self.unfinished[-1]
            node = Element(tag=tag, attributes=attributes, parent=parent)
            parent.children.append(node)
        else:
            parent = self.unfinished[-1] if self.unfinished else None
            if tag in self.SIBLING_TAGS:
                # If the parent <p> tag is a direct parent, finish the
                # parent node and
                if parent and parent.tag in self.SIBLING_TAGS:
                    # Pop parent tag off and append to previously unfinished node to finish it
                    parent_p_tag: Element = self.unfinished.pop()
                    parent = self.unfinished[-1]
                    if parent:
                        parent.children.append(parent_p_tag)
                    # Reset parent to the parent_p_tag so we create the nested
                    # <p> tag below
                    parent = parent_p_tag
                # If the parent tag isn't a direct <p> tag, look for parent p tag in the
                # descendants
                has_parent_p_tag = any(item.tag == "p" for item in self.unfinished)
                if has_parent_p_tag:
                    # Iterate through unfinished nodes until we find the parent 'p' tag
                    tags_to_finish = []
                    while self.unfinished:
                        node = self.unfinished.pop()
                        if node.tag == "p":
                            break
                        tags_to_finish.append(node)
                    # Now finish

            node = Element(tag=tag, attributes=attributes, parent=parent)
            self.unfinished.append(node)

    def handle_nested_p_parent_tag(self):
        tags_to_close = []
        has_parent_p_tag = any(item.tag == "p" for item in self.unfinished)
        if has_parent_p_tag:
            while self.unfinished:
                node = self.unfinished.pop()
                tags_to_close.append(node)
                if node.tag == "p":
                    break

            tags_to_close.reverse()
            parent_p_tag = node
            print("tags to close", tags_to_close)
            print("parent p tag parent - should be body", parent_p_tag.parent)
            # Once we find the parent p tag,
            new_parent = Element(
                tag=parent_p_tag.tag,
                attributes=parent_p_tag.attributes,
                parent=parent_p_tag.parent,
            )
            for tag_to_close in tags_to_close:
                new_parent.children.append(tag_to_close)
            self.unfinished.append(new_parent)

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