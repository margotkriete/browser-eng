import tkinter
from enum import Enum

from constants import (
    BLOCK_ELEMENTS,
    HEAD_TAG,
    TEXT_LIKE_TAGS,
    Alignment,
    Style,
    Weight,
    HSTEP,
    SCROLLBAR_WIDTH,
    VSTEP,
    INLINE_LAYOUT,
    BLOCK_LAYOUT,
)
from draw import DrawRect, DrawText
from font_cache import get_font
from typedclasses import LineItem
from parser import Text, Element
from typing import Literal, Optional


class BlockLayout:
    cursor_y: int
    cursor_x: int
    line: list
    alignment: Enum
    abbr: bool
    in_pre: bool
    style: Literal["roman", "italic"]
    weight: Literal["bold", "normal"]
    family: Optional[str]

    def __init__(
        self,
        node: list[Element | Text] | Element | Text,
        parent,
        previous,
        width: int = 0,
        rtl: bool = False,
        alignment: Enum = Alignment.RIGHT,
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
        self.in_pre = False
        self.family = None
        self.abbr: bool = False
        self.alignment: Enum = alignment
        self.display_list: list[DrawText | DrawRect] = []
        self.x: int = 0
        self.y: int = 0

    def _handle_soft_hyphen(self, word: str, font: tkinter.font.Font) -> None:
        # If word has a soft hyphen, append string before hyphen to the current
        # line, start a new line, and call .word on the rest of the word
        split_text = word.split("&shy;", 1)
        self.line.append(LineItem(x=self.cursor_x, text=split_text[0] + "-", font=font))
        self.flush()
        self.word(split_text[1])

    def _handle_abbr(
        self, word: str, font: tkinter.font.Font
    ) -> tuple[str, tkinter.font.Font]:
        for char in word:
            if char.islower() and char.isalpha():
                font = get_font(self.size - 2, Weight.BOLD.value, self.style)
                word = word.replace(char, char.upper())
        return word, font

    def open_tag(self, tag: str, attributes: Optional[dict] = None) -> None:
        match tag:
            case "i":
                self.style = Style.ITALIC.value
            case "b":
                self.weight = Weight.BOLD.value
            case "small":
                self.size -= 2
            case "big":
                self.size += 4
            case "br":
                self.flush()
            case "h1":
                if attributes and attributes.get("class") == "title":
                    self.alignment = Alignment.CENTER
            case "abbr":
                self.abbr = True
            case "pre":
                self.in_pre = True
                self.family = "Courier New"

    def close_tag(self, tag: str) -> None:
        match tag:
            case "i":
                self.style = Style.ROMAN.value
            case "b":
                self.weight = Weight.NORMAL.value
            case "small":
                self.size += 2
            case "big":
                self.size -= 4
            case "p":
                self.flush()
                self.cursor_y += VSTEP
            case "h1":
                if self.alignment == Alignment.CENTER:
                    self.flush()
                    self.alignment = Alignment.RIGHT
            case "abbr":
                self.abbr = False
            case "pre":
                self.in_pre = False
                self.family = None

    def word(self, word: str) -> None:
        font = get_font(self.size, self.weight, self.style, self.family)
        if self.abbr:
            word, font = self._handle_abbr(word, font)
        w = font.measure(word)

        if self.cursor_x + w > self.width - HSTEP - SCROLLBAR_WIDTH:
            if "&shy;" in word:
                return self._handle_soft_hyphen(word, font)
            self.flush()
        elif "&shy;" in word:
            word = word.replace("&shy;", "")

        self.line.append(LineItem(x=self.cursor_x, text=word, font=font))
        if self.in_pre:
            self.cursor_x += w
        else:
            self.cursor_x += w + font.measure(" ")

        # Increase cursor_y if the character is a newline
        if word == "\n":
            self.cursor_y += VSTEP
            self.cursor_x = HSTEP

    def flush(self) -> None:
        # self.line is a buffer of x positions, computed in the first pass of text
        if not self.line:
            return

        # Align words along the baseline
        metrics = [item.font.metrics() for item in self.line]
        max_ascent = max([metric["ascent"] for metric in metrics])
        baseline = self.cursor_y + 1.25 * max_ascent
        offset: int = 0

        if self.rtl:
            offset = self.width - (HSTEP * 2) - self.cursor_x

        if self.alignment == Alignment.CENTER:
            offset = int((self.width - self.line[-1].x - SCROLLBAR_WIDTH) / 2)

        # Add words to display_list
        for item in self.line:
            y = self.y + baseline - item.font.metrics("ascent")
            item.x += self.x + offset
            self.display_list.append(
                DrawText(x1=item.x, y1=y, text=item.text, font=item.font)
            )

        # Update cursor_x and cursor_y
        # cursor_y moves below baseline to account for deepest character
        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1.25 * max_descent
        self.cursor_x = 0
        self.line = []

    def recurse(self, tree: Text | Element) -> None:
        if isinstance(tree, Text):
            if not self.in_pre:
                for word in tree.text.split():
                    self.word(word)
            else:
                for line in tree.text.split("\n"):
                    self.word(line)
                    if line:
                        self.flush()
        else:
            self.open_tag(tree.tag, tree.attributes)
            for child in tree.children:
                self.recurse(child)
            self.close_tag(tree.tag)

    def layout_mode(self) -> str:
        if isinstance(self.node, list):
            return INLINE_LAYOUT
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
        siblings: list[Element] = []
        for child in self.node.children:
            if isinstance(child, Element):
                if child.tag == HEAD_TAG:
                    continue
                if child.tag in TEXT_LIKE_TAGS:
                    siblings.append(child)
                    continue
                elif siblings:
                    next = BlockLayout(
                        siblings, self, previous, rtl=self.rtl, alignment=self.alignment
                    )
                    self.children.append(next)
                    previous = next
                    siblings = []
            next = BlockLayout(
                child, self, previous, rtl=self.rtl, alignment=self.alignment
            )
            self.children.append(next)
            previous = next

        if siblings:
            next = BlockLayout(
                siblings, self, previous, rtl=self.rtl, alignment=self.alignment
            )
            self.children.append(next)

    def _layout_inline_mode(self) -> None:
        self.cursor_x: int = 0
        self.cursor_y: int = 0
        self.weight, self.style = Weight.NORMAL.value, Style.ROMAN.value
        self.height = self.cursor_y
        self.size: int = 12
        self.line: list[LineItem] = []
        if isinstance(self.node, list):
            for n in self.node:
                self.recurse(n)
        else:
            self.recurse(self.node)
        self.flush()

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

        if mode == BLOCK_LAYOUT:
            self.height = sum([child.height for child in self.children])
        else:
            self.height = self.cursor_y

    def paint(self) -> list[DrawText | DrawRect]:
        cmds: list[DrawText | DrawRect] = []

        if isinstance(self.node, Element):
            bg_color: str = ""
            if self.node.tag == "pre":
                bg_color = "gray"
            if (
                self.node.tag == "nav"
                and self.node.attributes
                and self.node.attributes.get("class") == "links"
            ):
                bg_color = "#eeeeee"
            if bg_color:
                x2, y2 = self.x + self.width - SCROLLBAR_WIDTH, self.y + self.height
                rect = DrawRect(self.x, self.y, x2, y2, bg_color)
                cmds.append(rect)

        if self.layout_mode() == INLINE_LAYOUT:
            for item in self.display_list:
                if isinstance(item, DrawText):
                    cmds.append(
                        DrawText(
                            x1=item.left, y1=item.top, text=item.text, font=item.font
                        )
                    )

        return cmds
