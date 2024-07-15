import argparse
import tkinter
import tkinter.font
from constants import (
    WIDTH,
    HEIGHT,
    HSTEP,
    VSTEP,
    SCROLLBAR_WIDTH,
    SCROLL_STEP,
    TEST_FILE,
)
from layout import Layout, lex
from tkinter import ttk
from url import URL


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
        self.display_list = Layout(self.text, rtl=self.rtl).display_list
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
        self.display_list = Layout(self.text, self.screen_width, self.rtl).display_list
        self.draw()
        self.draw_scrollbar()


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
