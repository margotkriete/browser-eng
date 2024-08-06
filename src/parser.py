import re
from typing import Optional, Tuple
from constants import (
    SELF_CLOSING_TAGS,
    HEAD_TAGS,
    SIBLING_TAGS,
    HTML_TAG,
    HEAD_TAG,
    CLOSING_HEAD_TAG,
    CLOSING_HTML_TAG,
    BODY_TAG,
)


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
        child_strings, attr_string = "", ""
        for child in self.children:
            child_strings += str(child)
        if self.attributes:
            for attr in self.attributes:
                attr_string += f" {attr}='{self.attributes[attr]}'"
        close_tag = "" if self.tag in SELF_CLOSING_TAGS else f"</{self.tag}>"
        return f"<{self.tag}{attr_string}>{child_strings}{close_tag}"


class HTMLParser:
    def replace_character_references(self, s: str) -> str:
        s = s.replace("&lt;", "<")
        s = s.replace("&gt;", ">")
        return s

    def __init__(self, body: str) -> None:
        self.body: str = body
        self.unfinished: list[Element] = []

    def implicit_tags(self, tag: Optional[str] = None) -> None:
        while True:
            open_tags = [node.tag for node in self.unfinished]
            if open_tags == [] and tag != HTML_TAG:
                self.add_tag(HTML_TAG)
            elif open_tags == [HTML_TAG] and tag not in [
                HEAD_TAG,
                BODY_TAG,
                CLOSING_HTML_TAG,
            ]:
                if tag in HEAD_TAGS:
                    self.add_tag(HEAD_TAG)
                else:
                    self.add_tag(BODY_TAG)
            elif (
                open_tags == [HTML_TAG, HEAD_TAG]
                and tag not in [CLOSING_HEAD_TAG] + HEAD_TAGS
            ):
                self.add_tag(CLOSING_HEAD_TAG)
            else:
                break

    def get_attributes(
        self, text: str, attributes: Optional[list] = []
    ) -> Tuple[str, dict]:
        tag: str = text.casefold()
        attrs_dict: dict = {}
        if attributes:
            for attrpair in attributes:
                if "=" in attrpair:
                    key, value = attrpair.split("=", 1)
                    # fmt: off
                    if len(value) > 2 and value[0] in ["'", '\"']:
                        value = value[1:-1]
                    attrs_dict[key.casefold()] = value
                else:
                    attrs_dict[attrpair.casefold()] = ""
        return tag, attrs_dict

    def parse(self) -> Element | Text:
        title = re.search("<title>(.*)</title>", self.body)
        if title:
            self.body = self.body.replace(title.group(1), "")

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
        IN_TAG, IN_COMMENT, IN_SCRIPT, IN_ATTR, IN_QUOTED_ATTR = (
            False,
            False,
            False,
            False,
            False,
        )
        body_length: int = len(self.body)
        attributes = []
        current_attribute = ""

        for i, c in enumerate(self.body):
            if c == '"' or c == "'":
                if IN_QUOTED_ATTR:
                    IN_QUOTED_ATTR = False
                    IN_ATTR = True
                elif IN_ATTR:
                    IN_QUOTED_ATTR = True
                    IN_ATTR = False
            elif c == " ":
                if IN_QUOTED_ATTR:
                    current_attribute += c
                elif IN_TAG:
                    IN_ATTR = True
                    if current_attribute:
                        attributes.append(current_attribute)
                        current_attribute = ""
                else:
                    text += c
            elif c == "<":
                if IN_QUOTED_ATTR:
                    current_attribute += c
                    continue
                if IN_COMMENT:
                    continue
                if self._started_comment_tag(i, body_length):
                    IN_COMMENT = True
                if self._finished_script_tag(i):
                    IN_SCRIPT = False
                if IN_SCRIPT:
                    text += c
                    continue
                IN_TAG = True
                if text:
                    self.add_text(text)
                text = ""
            elif c == ">":
                if IN_QUOTED_ATTR:
                    current_attribute += c
                    continue
                if self._finished_comment_tag(i, IN_COMMENT):
                    IN_COMMENT = False
                    text = ""
                    continue
                if IN_SCRIPT:
                    text += c
                    continue
                if text == "script":
                    IN_SCRIPT = True
                if IN_ATTR:
                    attributes.append(current_attribute)
                    current_attribute = ""
                self.add_tag(text, attributes)
                text = ""
                attributes = []
                IN_TAG = False
                IN_ATTR = False
            else:
                if IN_QUOTED_ATTR or IN_ATTR:
                    current_attribute += c
                    continue
                text += c

        if not IN_TAG and text:
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

    def add_tag(self, tag: str, attributes: Optional[list] = []) -> None:
        tag, attrs_dict = self.get_attributes(tag, attributes)
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
            node = Element(tag=tag, attributes=attrs_dict, parent=parent)
            parent.children.append(node)
        else:
            if tag in SIBLING_TAGS:
                self.handle_nested_tags(tag, attrs_dict)
            else:
                parent = self.unfinished[-1] if self.unfinished else None
                node = Element(tag=tag, attributes=attrs_dict, parent=parent)
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


class ViewSourceHTMLParser(HTMLParser):
    # view-source creates only text nodes and bold tag nodes.
    # We add a <b> tag before parsing actual text, and treat other
    # tags as if they were text, not tags.

    def lexer(self) -> None:
        IN_TAG, IN_TEXT = False, False
        buffer: str = ""

        for c in self.body:
            if c == "<":
                IN_TAG = True
                if IN_TEXT:
                    self.add_text(buffer)
                    self.add_tag("/b")
                    IN_TEXT = False
                    buffer = c
                else:
                    buffer += c
            elif c == ">":
                buffer += c
                IN_TAG = False
                if buffer:
                    self.add_text(buffer)
                    buffer = ""
            else:
                buffer += c
                if not IN_TAG and not IN_TEXT and not c.isspace():
                    self.add_tag("b")
                    IN_TEXT = True

        if buffer:
            self.add_text(buffer)
