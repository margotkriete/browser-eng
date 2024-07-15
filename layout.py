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
        # else:
        #     match tok.tag:
        #         case 'i':
        #             self.style = "italic"
        #         case '/i':
        #             self.style = "roman"
        #         case ''

        # elif tok.tag == "b":
        #     self.weight = "bold"
        # elif tok.tag == "/b":
        #     self.weight = "normal"

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
