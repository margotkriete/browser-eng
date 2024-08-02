import re
from typing import Optional, Tuple
from constants import SELF_CLOSING_TAGS, HEAD_TAGS, SIBLING_TAGS


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

    def __str__(self) -> str:
        child_strings = ""
        for child in self.children:
            child_strings += str(child)

        close_tag = "" if self.tag in SELF_CLOSING_TAGS else f"</{self.tag}>"
        return f"<{self.tag}>{child_strings}{close_tag}"


class HTMLParser:
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
                if tag in HEAD_TAGS:
                    self.add_tag("head")
                else:
                    self.add_tag("body")
            elif open_tags == ["html", "head"] and tag not in ["/head"] + HEAD_TAGS:
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

        self.lexer()
        return self.finish()

    def _started_comment_tag(self, i: int, body_length: int) -> bool:
        return i + 4 < body_length and self.body[i + 1 : i + 4] == "!--"

    def _finished_comment_tag(self, i: int, in_comment: bool) -> bool:
        return i - 2 > 0 and self.body[i - 2 : i] == "--" and in_comment

    def _finished_script_tag(self, i: int) -> bool:
        return self.body[i + 1 : i + 8] == "/script"

    def lexer(self) -> None:
        text: str = ""
        in_tag, in_comment, in_script = False, False, False
        body_length = len(self.body)

        for i, c in enumerate(self.body):
            if c == "<":
                if in_comment:
                    continue
                if self._started_comment_tag(i, body_length):
                    in_comment = True
                if self._finished_script_tag(i):
                    in_script = False
                if in_script:
                    text += c
                    continue
                in_tag = True
                if text:
                    self.add_text(text)
                text = ""
            elif c == ">":
                if self._finished_comment_tag(i, in_comment):
                    in_comment = False
                    text = ""
                    continue
                if in_script:
                    text += c
                    continue
                if text == "script":
                    in_script = True
                self.add_tag(text)
                text = ""
                in_tag = False
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
        elif tag in SELF_CLOSING_TAGS:
            parent = self.unfinished[-1]
            node = Element(tag=tag, attributes=attributes, parent=parent)
            parent.children.append(node)
        else:
            if tag in SIBLING_TAGS:
                self.handle_nested_tags(tag, attributes)
            else:
                parent = self.unfinished[-1] if self.unfinished else None
                node = Element(tag=tag, attributes=attributes, parent=parent)
                self.unfinished.append(node)

    # TODO: clean this up, handle <li> tags
    def handle_nested_tags(self, tag, attributes) -> None:
        parent = self.unfinished[-1] if self.unfinished else None
        tags_to_finish = []

        # If <p> is nested within another <p> tag, finish the first tag and create another
        if parent and parent.tag in SIBLING_TAGS and parent.tag == tag:
            parent_p_tag: Element = self.unfinished.pop()
            parent = self.unfinished[-1]
            if parent:
                parent.children.append(parent_p_tag)
                parent = parent_p_tag
        # If the parent tag isn't the same, look for parent p tag in the descendents
        elif any(item.tag == "p" for item in self.unfinished):
            while self.unfinished:
                last_node = self.unfinished.pop()
                if last_node.tag == "p":
                    break
                tags_to_finish.append(last_node)
            # Add tags to finish as children of parent tag
            tags_to_finish.reverse()
            node_to_append = last_node
            for item in tags_to_finish:
                node_to_append.children.append(item)
                node_to_append = item
            # Parent tag is finished, so append it to the last unfinished node
            self.unfinished[-1].children.append(last_node)
        node = Element(tag=tag, attributes=attributes, parent=parent)
        self.unfinished.append(node)
        for item in tags_to_finish:
            self.unfinished.append(
                Element(tag=item.tag, attributes=attributes, parent=node)
            )

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
