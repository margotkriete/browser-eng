import tkinter
from enum import Enum
from typing import Literal

from constants import (
    Style,
    BLOCK_ELEMENTS,
    ENTITY_MAP,
    HSTEP,
    SCROLLBAR_WIDTH,
    INLINE_LAYOUT,
    BLOCK_LAYOUT,
)
from draw import DrawRect, DrawText
from font_cache import get_font
from line_layout import LineLayout, TextLayout
from typedclasses import DisplayListItem, LineItem
from parser import Text, Element


class BlockLayout:
    cursor_y: int
    cursor_x: int

    def __init__(
        self,
        node: Element | Text,
        parent,
        previous,
        width: int = 0,
        rtl: bool = False,
    ):
        self.node = node
        self.parent = parent
        self.previous = previous
        self.children: list[BlockLayout] = []
        self.width: int = width
        # height is a public field and always contains the correct value;
        # cursor_y changes as we lay out paragraphs and sometimes "wrong"
        self.height: int = 0
        self.rtl = rtl
        self.display_list: list[DisplayListItem | DrawText | DrawRect] = []
        self.x: int = 0
        self.y: int = 0

    def _handle_soft_hyphen(
        self, word: str, font: tkinter.font.Font, node, color
    ) -> None:
        # If word has a soft hyphen, append string before hyphen to the current
        # line, start a new line, and call .word on the rest of the word
        split_text = word.split("&shy;", 1)
        self.line.append(
            LineItem(x=self.cursor_x, text=split_text[0] + "-", font=font, color=color)
        )
        self.new_line()
        self.word(split_text[1], node)

    def replace_entities(self, word: str) -> str:
        for entity in ENTITY_MAP:
            if entity in word:
                word = word.replace(entity, ENTITY_MAP[entity])
        return word

    def new_line(self):
        self.cursor_x = 0
        last_line = self.children[-1] if self.children else None
        new_line = LineLayout(self.node, self, last_line)
        self.children.append(new_line)

    def word(self, word: str, node: Element | Text) -> None:
        weight: Literal["bold", "normal"] = node.style["font-weight"]
        style: Literal["roman", "italic"] = node.style["font-style"]
        family: str = node.style["font-family"]

        # Convert normal -> roman style and CSS pixels -> Tk points
        if style == "normal":
            style = Style.ROMAN.value
        size: int = int(float(node.style["font-size"][:-2]) * 0.75)

        font = get_font(size, weight, style, family)
        is_abbr = isinstance(node, Text) and node.parent.tag == "abbr"
        if is_abbr:
            word = word.replace(word, word.upper())
        w = font.measure(word)
        if self.cursor_x + w > self.width - HSTEP - SCROLLBAR_WIDTH:
            self.new_line()
            # if "&shy;" in word:
            # return self._handle_soft_hyphen(word, font, node, color)
        # elif "&shy;" in word:
        # word = word.replace("&shy;", "")

        word = self.replace_entities(word)
        line = self.children[-1]
        previous_word = line.children[-1] if line.children else None
        text = TextLayout(node, word, line, previous_word)
        line.children.append(text)
        self.cursor_x += w + font.measure(" ")

    def recurse(self, node: Text | Element) -> None:
        if isinstance(node, Text):
            for word in node.text.split():
                self.word(word, node)
        else:
            self.handle_global_tag_styles(node)
            for child in node.children:
                self.recurse(child)

    def handle_global_tag_styles(self, tree: Element):
        if tree.tag == "br":
            self.new_line()

    def layout_mode(self) -> str:
        if isinstance(self.node, Text):
            return INLINE_LAYOUT
        elif any(
            [
                isinstance(child, Element) and child.tag in BLOCK_ELEMENTS
                for child in self.node.children
            ]
        ):
            return BLOCK_LAYOUT
        elif self.node.children:
            return INLINE_LAYOUT
        else:
            return BLOCK_LAYOUT

    def _layout_block_mode(self) -> None:
        previous = None
        for child in self.node.children:
            if isinstance(child, Element) and child.tag == "head":
                continue
            next = BlockLayout(child, self, previous, rtl=self.rtl)
            self.children.append(next)
            previous = next

    def _layout_inline_mode(self) -> None:
        self.new_line()
        self.recurse(self.node)

    def layout(self) -> None:
        self.x = self.parent.x
        self.width = self.parent.width
        if self.previous:
            self.y = self.previous.y + self.previous.height
        else:
            self.y = self.parent.y

        mode = self.layout_mode()
        if mode == BLOCK_LAYOUT:
            self._layout_block_mode()
        else:
            self._layout_inline_mode()

        for block_child in self.children:
            block_child.layout()

        self.height = sum([child.height for child in self.children])

    def paint(self) -> list[DrawRect]:
        cmds: list[DrawRect] = []
        if isinstance(self.node, Element):
            bg_color: str = ""
            if (
                self.node.tag == "nav"
                and self.node.attributes
                and self.node.attributes.get("class") == "links"
            ):
                bg_color = "#eeeeee"
            if not bg_color:
                bg_color = self.node.style.get("background-color", "transparent")
            if bg_color and bg_color != "transparent":
                x2, y2 = self.x + self.width - SCROLLBAR_WIDTH, self.y + self.height
                rect = DrawRect(self.x, self.y, x2, y2, bg_color)
                cmds.append(rect)
        return cmds
