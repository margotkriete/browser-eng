import tkinter
from enum import Enum

from constants import Alignment, Style, Weight, HSTEP, SCROLLBAR_WIDTH, VSTEP, WIDTH
from font_cache import get_font
from typedclasses import DisplayListItem, LineItem
from parser import Text, Element
from typing import Optional


def replace_character_references(s: str) -> str:
    s = s.replace("&lt;", "<")
    s = s.replace("&gt;", ">")
    return s


class Layout:
    cursor_y: int
    cursor_x: int
    line: list
    alignment: Enum
    abbr: bool
    in_pre: bool

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
                if attributes.get("class") == "title":
                    self.alignment = Alignment.CENTER
            case "abbr":
                self.abbr = True
            case "pre":
                self.in_pre = True
                self.family = "Courier New"

    def close_tag(self, tag: str, attributes: Optional[dict] = None) -> None:
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
                if attributes.get("class") == "title":
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
            y = baseline - item.font.metrics("ascent")
            item.x += offset
            self.display_list.append(DisplayListItem(item.x, y, item.text, item.font))

        # Update cursor_x and cursor_y
        # cursor_y moves below baseline to account for deepest character
        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1.25 * max_descent
        self.cursor_x = HSTEP
        self.line = []

    def recurse(self, tree) -> None:
        if isinstance(tree, Text):
            if not self.in_pre:
                for word in tree.text.split():
                    self.word(word)
            else:
                for line in tree.text.split("\n"):
                    self.word(line)
                    if not line:
                        self.flush()
        else:
            self.open_tag(tree.tag, tree.attributes)
            for child in tree.children:
                self.recurse(child)
            self.close_tag(tree.tag, tree.attributes)

    def __init__(
        self,
        tree: Element | Text,
        width: int = WIDTH,
        rtl: bool = False,
    ) -> None:
        self.rtl: bool = rtl
        self.cursor_x, self.cursor_y = HSTEP, VSTEP
        self.weight, self.style = Weight.NORMAL.value, Style.ROMAN.value
        self.display_list: list[DisplayListItem] = []
        self.line: list[LineItem] = []
        self.width: int = width
        self.size: int = 12
        self.alignment: Enum = Alignment.RIGHT
        self.abbr: bool = False
        self.in_pre: bool = False
        self.family = None
        self.recurse(tree)
        self.flush()
