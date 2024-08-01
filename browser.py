import argparse
import tkinter
import tkinter.font
from parser import HTMLParser, Element, Text

from constants import HEIGHT, SCROLL_STEP, SCROLLBAR_WIDTH, TEST_FILE, VSTEP, WIDTH
from layout import Layout
from typedclasses import ScrollbarCoordinate
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
        self.view_source = False

    def _get_page_height(self) -> int:
        return self.display_list[-1].y

    def load(self, url: URL) -> None:
        body = url.request()
        if not body:
            return
        self.nodes: Element | Text = HTMLParser(
            body, view_source=url.view_source
        ).parse()
        self.display_list = Layout(
            tree=self.nodes, width=self.screen_width, rtl=self.rtl
        ).display_list
        self.draw()

    # Exercise 2.4
    def get_scrollbar_coordinates(self) -> ScrollbarCoordinate:
        page_height = self._get_page_height()
        scrollbar_height = int((self.screen_height / page_height) * self.screen_height)
        x0 = self.screen_width - SCROLLBAR_WIDTH
        y0 = int((self.scroll / page_height) * self.screen_height)
        x1 = self.screen_width
        y1 = y0 + scrollbar_height
        return ScrollbarCoordinate(x0, y0, x1, y1)

    # Exercise 2.4
    def draw_scrollbar(self) -> None:
        if not self.display_list:
            return
        if self._get_page_height() <= self.screen_height:
            self.canvas.delete("scrollbar")
            return
        coords = self.get_scrollbar_coordinates()
        if self.canvas.gettags("scrollbar"):
            self.canvas.coords(
                "scrollbar",
                coords.x0,
                coords.y0,
                coords.x1,
                coords.y1,
            )
        else:
            self.canvas.create_rectangle(
                coords.x0,
                coords.y0,
                coords.x1,
                coords.y1,
                fill="blue",
                tags="scrollbar",
            )

    def draw(self):
        self.canvas.delete("text")
        for item in self.display_list:
            if item.y > self.scroll + self.screen_height:
                continue
            if item.y + VSTEP < self.scroll:
                continue
            self.canvas.create_text(
                item.x,
                item.y - self.scroll,
                text=item.text,
                font=item.font,
                anchor="nw",
                tag="text",
            )
        self.draw_scrollbar()

    def scrolldown(self, e) -> None:
        if not self.display_list:
            return
        if self.scroll + self.screen_height < self._get_page_height():
            self.scroll += SCROLL_STEP
            self.draw()

    def scrollup(self, e) -> None:
        if self.scroll >= SCROLL_STEP:
            self.scroll -= SCROLL_STEP
            self.draw()

    # Exercise 2.2
    def mousescroll(self, e) -> None:
        scroll_change = self.scroll - e.delta
        if (scroll_change + self.screen_height < self._get_page_height()) and (
            scroll_change > 0
        ):
            self.scroll -= e.delta
            self.draw()

    # Exercise 2.3
    def resize(self, e: tkinter.Event) -> None:
        self.screen_height = e.height
        self.screen_width = e.width
        self.display_list = Layout(
            tree=self.nodes, width=self.screen_width, rtl=self.rtl
        ).display_list
        self.draw()


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
