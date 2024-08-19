import argparse
import tkinter
import tkinter.font
from parser import Element, HTMLParser, Text, ViewSourceHTMLParser

from block_layout import BlockLayout
from constants import HEIGHT, SCROLL_STEP, SCROLLBAR_WIDTH, TEST_FILE, WIDTH
from css_parser import CSSParser, style
from document_layout import DocumentLayout
from draw import DrawRect, DrawText
from helpers import cascade_priority, tree_to_list
from typedclasses import DisplayListItem, ScrollbarCoordinate
from url import URL


def paint_tree(
    layout_object: BlockLayout | DocumentLayout,
    display_list: list[DisplayListItem | DrawRect | DrawText],
):
    display_list.extend(layout_object.paint())

    for child in layout_object.children:
        paint_tree(child, display_list)


import os

dir_path = os.path.dirname(os.path.realpath(__file__))

DEFAULT_STYLE_SHEET = CSSParser(
    open(os.path.join(dir_path, "browser.css")).read()
).parse()


class Browser:
    def __init__(self, rtl: bool = False):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window, width=WIDTH, height=HEIGHT, bg="#ffffff"
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
        return self.display_list[-1].bottom

    def generate_links(self) -> list:
        return [
            node.attributes["href"]
            for node in tree_to_list(self.nodes, [])
            if isinstance(node, Element)
            and node.tag == "link"
            and node.attributes.get("rel") == "stylesheet"
            and "href" in node.attributes
        ]

    def load(self, url: URL) -> None:
        body: str | None = url.request()
        if not body:
            return
        self.nodes: Element | Text
        if url.view_source:
            self.nodes = ViewSourceHTMLParser(body).parse()
        else:
            self.nodes = HTMLParser(body).parse()
        rules: list = DEFAULT_STYLE_SHEET.copy()
        links: list = self.generate_links()
        for link in links:
            style_url = url.resolve(link)
            try:
                body = style_url.request()
            except:
                continue
            rules.extend(CSSParser(body).parse())
        style(self.nodes, sorted(rules, key=cascade_priority))
        self.document = DocumentLayout(node=self.nodes, rtl=self.rtl)
        self.document.layout()
        self.display_list: list = []
        paint_tree(self.document, self.display_list)
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
        for cmd in self.display_list:
            if cmd.top > self.scroll + self.screen_height:
                continue
            if cmd.bottom < self.scroll:
                continue
            cmd.execute(self.scroll, self.canvas)
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
        self.document = DocumentLayout(node=self.nodes, width=e.width, rtl=self.rtl)
        self.document.layout()
        self.display_list = []
        paint_tree(self.document, self.display_list)
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
