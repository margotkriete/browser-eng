import argparse
import tkinter
import tkinter.font
from tkinter import ttk
from url import URL


WIDTH, HEIGHT = 800, 600
SCROLL_STEP = 100
TEST_FILE = "/Users/margotkriete/Desktop/test.txt"
HSTEP, VSTEP = 13, 18
SCROLLBAR_WIDTH = 20


class Browser:
    def __init__(self, rtl: bool = False):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window,
            width=WIDTH,
            height=HEIGHT,
        )
        self.canvas.pack(fill="both", expand=1)
        self.scroll = 0
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<MouseWheel>", self.mousescroll)
        self.window.bind("<Configure>", self.resize)
        self.screen_height = HEIGHT
        self.screen_width = WIDTH
        self.rtl = rtl

        # Size unit is "points," which are 72nds of an inch, not pixels
        self.bi_times = tkinter.font.Font(family="Times", size=16)

    def _get_page_height(self):
        return self.display_list[len(self.display_list) - 1][1]

    def load(self, url: str) -> None:
        body = url.request()
        self.text = lex(body)
        self.display_list = layout(self.text, rtl=self.rtl)
        self.draw_scrollbar()
        self.draw()

    # Exercise 2.4
    def get_scrollbar_coordinates(self):
        page_height = self._get_page_height()
        scrollbar_height = (self.screen_height / page_height) * self.screen_height
        if self.display_list:
            x0 = self.screen_width - SCROLLBAR_WIDTH
            y0 = (self.scroll / page_height) * self.screen_height
            x1 = self.screen_width
            y1 = y0 + scrollbar_height
            return x0, y0, x1, y1

    # Exercise 2.4
    def draw_scrollbar(self) -> None:
        if self.display_list:
            if self._get_page_height() < self.screen_height:
                return
            x0, y0, x1, y1 = self.get_scrollbar_coordinates()
            if self.canvas.gettags("scrollbar"):
                self.canvas.coords("scrollbar", x0, y0, x1, y1)
            else:
                self.canvas.create_rectangle(
                    x0, y0, x1, y1, fill="blue", tags="scrollbar"
                )

    def draw(self, font=None) -> None:
        self.canvas.delete("text")
        for x, y, c, font in self.display_list:
            if not font:
                font = self.bi_times
            if y > self.scroll + self.screen_height:
                continue
            if y + VSTEP < self.scroll:
                continue
            self.canvas.create_text(
                x, y - self.scroll, text=c, font=font, anchor="nw", tag="text"
            )

    def scrolldown(self, e):
        if not self.display_list:
            return
        if self.scroll + self.screen_height < self._get_page_height():
            self.scroll += SCROLL_STEP
            self.draw()
            self.draw_scrollbar()

    def scrollup(self, e):
        if self.scroll >= SCROLL_STEP:
            self.scroll -= SCROLL_STEP
        self.draw()
        self.draw_scrollbar()

    # Exercise 2.2
    def mousescroll(self, e):
        updated_scroll = self.scroll - e.delta + self.screen_height
        if (updated_scroll < self._get_page_height()) and (self.scroll - e.delta > 0):
            self.scroll -= e.delta
            self.draw()
            self.draw_scrollbar()

    # Exercise 2.3
    def resize(self, e):
        self.screen_height = e.height
        self.screen_width = e.width
        self.display_list = layout(self.text, self.screen_width, self.rtl)
        self.draw()
        self.draw_scrollbar()


def layout(
    tokens: "list[str]", width: int = WIDTH, rtl: bool = False
) -> "list[tuple[int, int, str]]":
    if rtl:
        return layout_rtl(tokens, width)

    cursor_x, cursor_y = HSTEP, VSTEP
    weight, style = "normal", "roman"
    display_list = []

    for token in tokens:
        if isinstance(token, Text):
            for word in token.text.split():
                font = tkinter.font.Font(size=16, weight=weight, slant=style)
                w = font.measure(word)
                display_list.append((cursor_x, cursor_y, word, font))
                cursor_x += w + font.measure(" ")

                # Wrap text once we reach the edge of the screen
                if cursor_x + w >= width - HSTEP - SCROLLBAR_WIDTH:
                    cursor_y += font.metrics("linespace") * 1.25
                    cursor_x = HSTEP

                # Increase cursor_y if the character is a newline
                if word == "\n":
                    cursor_y += VSTEP
                    cursor_x = HSTEP
        elif token.tag == "i":
            style = "italic"
        elif token.tag == "/i":
            print("found italic", token.tag)
            style = "roman"
        elif token.tag == "b":
            weight = "bold"
        elif token.tag == "/b":
            weight = "normal"
    return display_list


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


class Text:
    def __init__(self, text):
        self.text = text


class Tag:
    def __init__(self, tag):
        self.tag = tag


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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-r", help="Lay characters from right to left", action="store_true"
    )
    parser.add_argument(
        "url",
        metavar="URL",
        default=f"file://{TEST_FILE}",
        help="URL to serve",
        nargs="?",
    )
    args = parser.parse_args()
    Browser(rtl=args.r).load(URL(args.url))
    tkinter.mainloop()
