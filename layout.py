import re
import tkinter
from enum import Enum

from constants import Alignment, HSTEP, SCROLLBAR_WIDTH, VSTEP, WIDTH
from font_cache import get_font
from typedclasses import DisplayListItem, LineItem, Tag, Text


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

    def token(self, tok: Text | Tag) -> None:
        if isinstance(tok, Text):
            if not self.in_pre:
                for word in tok.text.split():
                    self.word(word)
            else:
                for word in tok.text.split("\n"):
                    self.word(word)
                    if not word:
                        self.flush()
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
                case 'h1 class="title"':
                    self.alignment = Alignment.CENTER
                case "/h1":
                    self.flush()
                    self.alignment = Alignment.RIGHT
                case "abbr":
                    self.abbr = True
                case "/abbr":
                    self.abbr = False
                case "pre":
                    self.in_pre = True
                    self.family = "Courier New"
                case "/pre":
                    self.in_pre = False
                    self.family = None

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
                font = get_font(self.size - 2, "bold", self.style)
                word = word.replace(char, char.upper())
        return word, font

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

    def __init__(
        self,
        tokens: list[Tag | Text],
        width: int = WIDTH,
        rtl: bool = False,
    ) -> None:
        self.rtl: bool = rtl
        self.cursor_x, self.cursor_y = HSTEP, VSTEP
        self.weight, self.style = "normal", "roman"
        self.display_list: list[DisplayListItem] = []
        self.line: list[LineItem] = []
        self.width: int = width
        self.size: int = 12
        self.alignment: Enum = Alignment.RIGHT
        self.abbr: bool = False
        self.in_pre: bool = False
        self.family = None

        for tok in tokens:
            self.token(tok)

        self.flush()


# Convert raw response body to a list of parsed Tags and Text
def lex(body: str, view_source: bool = False) -> list[Tag | Text]:
    buffer: str = ""
    out: list[Tag | Text] = []
    in_tag: bool = False

    title = re.search("<title>(.*)</title>", body)
    title_text = ""
    if title:
        title_text = title.group(1)
    body = body.replace(title_text, "")

    if view_source:
        body = replace_character_references(body)
        out.append(Text(body))
        return out

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
