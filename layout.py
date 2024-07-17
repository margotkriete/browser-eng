import tkinter
from constants import HSTEP, VSTEP, SCROLLBAR_WIDTH, WIDTH
from font_cache import get_font


class Text:
    def __init__(self, text):
        self.text = text


class Tag:
    def __init__(self, tag):
        self.tag = tag


class Layout:
    def token(self, tok):
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

    def word(self, word):
        font = get_font(self.size, self.weight, self.style)
        w = font.measure(word)

        # Wrap text once we reach the edge of the screen
        if self.cursor_x + w > self.width - HSTEP - SCROLLBAR_WIDTH:
            self.flush()

        self.line.append((self.cursor_x, word, font))
        if self.rtl:
            self.cursor_x -= w + font.measure(" ")
        else:
            self.cursor_x += w + font.measure(" ")

        # # Increase cursor_y if the character is a newline
        # if word == "\n":
        #     self.cursor_y += VSTEP
        #     self.cursor_x = HSTEP

    def flush(self):
        if not self.line:
            return

        # Align words along the baseline
        metrics = [font.metrics() for _, _, font in self.line]
        max_ascent = max([metric["ascent"] for metric in metrics])
        baseline = self.cursor_y + 1.25 * max_ascent

        # Add words to display_list
        for x, word, font in self.line:
            y = baseline - font.metrics("ascent")
            self.display_list.append((x, y, word, font))

        # Update cursor_x and cursor_y
        # cursor_y moves below baseline to account for deepest character
        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1.25 * max_descent
        if self.rtl:
            self.cursor_x = self.width - HSTEP
        else:
            self.cursor_x = HSTEP
        self.line = []

    def __init__(self, tokens: "list[str]", width: int = WIDTH, rtl: bool = False):
        self.rtl = rtl
        self.cursor_x, self.cursor_y = HSTEP, VSTEP
        if self.rtl:
            self.cursor_x = width - HSTEP
        self.weight, self.style = "normal", "roman"
        self.display_list = []

        # self.line is a buffer of x positions, computed in the
        # first pass of text
        self.line = []
        self.width = width
        self.size = 12

        for tok in tokens:
            self.token(tok)

        self.flush()

    # Exercise 2.7
    def layout_rtl(self, text: str, width: int = WIDTH):
        cursor_x = width - HSTEP
        cursor_y = VSTEP
        font = tkinter.font.Font(family="Times", size=16)

        # Keep track of current line in list, and when you reach
        # a new line, append existing list to display_list, but lay out in reverse
        line = []
        for c in text:
            # If cursor_x is still within the same line, keep
            # adding to line array
            if cursor_x >= HSTEP and c != "\n":
                line.append(c)
                cursor_x -= HSTEP
            else:
                # If cursor_x is now at the end of the line, lay out line list,
                # starting from the rightmost edge
                cursor_x = width - HSTEP
                line.reverse()
                for l in line:
                    self.display_list.append((cursor_x, cursor_y, l, font))
                    cursor_x -= HSTEP
                cursor_y += VSTEP

                # Reset cursor_x so the next iteration begins a new line
                cursor_x = width - HSTEP
                line = []


def lex(body: str) -> "list[str]":
    buffer = ""
    out = []
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
