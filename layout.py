import tkinter
from constants import HSTEP, VSTEP, SCROLLBAR_WIDTH, WIDTH


class Text:
    def __init__(self, text):
        self.text = text


class Tag:
    def __init__(self, tag):
        self.tag = tag


class Layout:
    def token(self, tok):
        if isinstance(tok, Text):
            self.handle_text(tok)
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

    def handle_text(self, token):
        for word in token.text.split():
            font = tkinter.font.Font(
                size=self.size, weight=self.weight, slant=self.style
            )
            w = font.measure(word)

            # Wrap text once we reach the edge of the screen
            if self.cursor_x + w >= self.width - HSTEP - SCROLLBAR_WIDTH:
                self.cursor_y += font.metrics("linespace") * 1.25
                self.cursor_x = HSTEP

            self.display_list.append((self.cursor_x, self.cursor_y, word, font))
            self.cursor_x += w + font.measure(" ")
            # Increase cursor_y if the character is a newline
            if word == "\n":
                self.cursor_y += VSTEP
                self.cursor_x = HSTEP

    def __init__(
        self, tokens: "list[str]", width: int = WIDTH, rtl: bool = False
    ) -> "list[tuple[int, int, str]]":
        # if rtl:
        # return layout_rtl(tokens, width)

        self.cursor_x, self.cursor_y = HSTEP, VSTEP
        self.weight, self.style = "normal", "roman"
        self.display_list = []
        self.width = width
        self.size = 12
        self.bi_times = tkinter.font.Font(family="Times", size=16)

        for tok in tokens:
            self.token(tok)


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


# Exercise 2.7
# TODO: fix after working through Chapter 3
def layout_rtl(text: str, width: int = WIDTH):
    cursor_x = width - HSTEP
    cursor_y = VSTEP
    display_list = []
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
                display_list.append((cursor_x, cursor_y, l, font))
                cursor_x -= HSTEP
            cursor_y += VSTEP

            # Reset cursor_x so the next iteration begins a new line
            cursor_x = width - HSTEP
            line = []

    return display_list
