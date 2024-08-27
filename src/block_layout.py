import tkinter
from enum import Enum
from typing import Literal, Union

from constants import (
    BLOCK_ELEMENTS,
    Alignment,
    Style,
    HSTEP,
    SCROLLBAR_WIDTH,
    VSTEP,
    INLINE_LAYOUT,
    BLOCK_LAYOUT,
)
from draw import DrawRect, DrawText
from font_cache import get_font
from typedclasses import DisplayListItem, LineItem
from parser import Text, Element


class BlockLayout:
    cursor_y: int
    cursor_x: int
    line: list
    alignment: Enum
    in_pre: bool

    def __init__(
        self,
        node: Element | Text,
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
        self.alignment: Enum = alignment
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
        self.flush()
        self.word(split_text[1], node)

    def handle_entities(self, word: str) -> None:
        if "&quot;" in word:
            word = word.replace("&quot;", '"')
        if "&apos;" in word:
            word = word.replace("&apos;", "'")
        if "&ndash;" in word or "&hyphen;" in word:
            word = word.replace("&ndash;", "‐")
            word = word.replace("&hyphen;", "‐")
        if "&amp;" in word:
            word = word.replace("&amp", "&")
        return word

    def word(self, word: str, node: Element | Text) -> None:
        weight: Literal["bold", "normal"] = node.style["font-weight"]
        style: Literal["roman", "italic"] = node.style["font-style"]
        color: str = node.style["color"]
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
            if "&shy;" in word:
                return self._handle_soft_hyphen(word, font, node, color)
            self.flush()
        elif "&shy;" in word:
            word = word.replace("&shy;", "")

        word = self.handle_entities(word)

        self.line.append(LineItem(x=self.cursor_x, text=word, font=font, color=color))
        if self.in_pre or is_abbr:
            self.cursor_x += w
        else:
            self.cursor_x += w + font.measure(" ")

        if "\n" in word:
            self.cursor_y += VSTEP
            self.cursor_x = HSTEP

    def flush(self) -> None:
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
            offset = int((self.width - self.cursor_x - SCROLLBAR_WIDTH) / 2)

        # Add words to display_list
        for item in self.line:
            y = self.y + baseline - item.font.metrics("ascent")
            item.x += self.x + offset
            self.display_list.append(
                DrawText(
                    x1=item.x, y1=y, text=item.text, font=item.font, color=item.color
                )
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
                    self.word(word, tree)
            else:
                for line in tree.text.splitlines(keepends=True):
                    self.word(line, tree)
                    if line.endswith("\n"):
                        self.flush()
        else:
            self.handle_global_tag_styles(tree)
            for child in tree.children:
                self.recurse(child)

    def handle_global_tag_styles(self, tree: Element):
        if tree.tag == "br":
            self.flush()
        if tree.tag == "pre":
            self.in_pre = True
        if (
            tree.tag == "h1"
            and tree.attributes
            and tree.attributes.get("class") == "title"
        ):
            self.alignment = Alignment.CENTER

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
            next = BlockLayout(
                child, self, previous, rtl=self.rtl, alignment=self.alignment
            )
            self.children.append(next)
            previous = next

    def _layout_inline_mode(self) -> None:
        self.cursor_x: int = 0
        self.cursor_y: int = 0
        self.height = self.cursor_y
        self.size: int = 12
        self.line: list[LineItem] = []
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

        if self.layout_mode() == INLINE_LAYOUT:
            for item in self.display_list:
                if isinstance(item, DrawText):
                    cmds.append(
                        DrawText(
                            x1=item.left,
                            y1=item.top,
                            text=item.text,
                            font=item.font,
                            color=item.color,
                        )
                    )

        return cmds
