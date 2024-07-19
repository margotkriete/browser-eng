from constants import HSTEP, SCROLLBAR_WIDTH, VSTEP, WIDTH
from font_cache import get_font
from tkinter import font
import tkinter

from typedclasses import DisplayListItem


class Text:
    def __init__(self, text: str):
        self.text = text


class Tag:
    def __init__(self, tag: str):
        self.tag = tag


class Layout:
    cursor_y: int
    cursor_x: int
    line: list

    def token(self, tok: Text | Tag) -> None:
        if isinstance(tok, Text):
            for word in tok.text.split():
                self.word(word)
        else:
            match tok.tag:
                case "i":
                    self.style = "italic"
                case "/i":
                    self.style = "roman"
                case "b":
                    self.weight = "bold"
                case "/b":
                    self.weight = "normal"
                case "small":
                    self.size -= 2
                case "/small":
                    self.size += 2
                case "big":
                    self.size += 4
                case "/big":
                    self.size -= 4
                case "br":
                    self.flush()
                case "/p":
                    self.flush()
                    self.cursor_y += VSTEP

    def word(self, word) -> None:
        font = get_font(self.size, self.weight, self.style)
        w = font.measure(word)

        # Wrap text once we reach the edge of the screen
        if self.cursor_x + w > self.width - HSTEP - SCROLLBAR_WIDTH:
            self.flush()

        self.line.append((self.cursor_x, word, font))
        self.cursor_x += w + font.measure(" ")

        # Increase cursor_y if the character is a newline
        if word == "\n":
            self.cursor_y += VSTEP
            self.cursor_x = HSTEP

    def flush(self) -> None:
        if not self.line:
            return

        # Align words along the baseline
        metrics = [font.metrics() for _, _, font in self.line]
        max_ascent = max([metric["ascent"] for metric in metrics])
        baseline = self.cursor_y + 1.25 * max_ascent

        if self.rtl:
            offset = self.width - (HSTEP * 2) - self.cursor_x

        # Add words to display_list
        for x, word, font in self.line:
            y = baseline - font.metrics("ascent")
            if self.rtl:
                x += offset
            self.display_list.append(DisplayListItem(x, y, word, font))

        # Update cursor_x and cursor_y
        # cursor_y moves below baseline to account for deepest character
        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1.25 * max_descent
        self.cursor_x = HSTEP
        self.line = []

    def __init__(
        self, tokens: list[Tag | Text], width: int = WIDTH, rtl: bool = False
    ) -> None:
        self.rtl: bool = rtl
        self.cursor_x, self.cursor_y = HSTEP, VSTEP
        self.weight, self.style = "normal", "roman"
        self.display_list: list[DisplayListItem] = []

        # self.line is a buffer of x positions, computed in the
        # first pass of text
        self.line = []
        self.width: int = width
        self.size: int = 12

        for tok in tokens:
            self.token(tok)

        self.flush()


def lex(body: str) -> list[Tag | Text]:
    buffer = ""
    out: list[Tag | Text] = []
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True  # word is in between < >
            if buffer:
                out.append(Text(buffer))
            buffer = ""
        elif c == ">":
            in_tag = False
            out.append(Tag(buffer))
            buffer = ""
        else:
            buffer += c
    if not in_tag and buffer:
        out.append(Text(buffer))
    return out
