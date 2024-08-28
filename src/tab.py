import os
import tkinter
from parser import Element, HTMLParser, Text, ViewSourceHTMLParser

from constants import HEIGHT, SCROLL_STEP, SCROLLBAR_WIDTH, WIDTH
from css_parser import CSSParser, style
from document_layout import DocumentLayout
from helpers import cascade_priority, paint_tree, tree_to_list
from typedclasses import ScrollbarCoordinate
from url import URL

dir_path = os.path.dirname(os.path.realpath(__file__))

DEFAULT_STYLE_SHEET = CSSParser(
    open(os.path.join(dir_path, "browser.css")).read()
).parse()


class Tab:
    def __init__(self, rtl: bool = False):
        self.scroll = 0
        self.screen_height = HEIGHT
        self.screen_width = WIDTH
        self.rtl = rtl
        self.view_source = False
        self.url = None

    def _get_page_height(self) -> int:
        return self.display_list[-1].bottom

    def get_stylesheet_links(self) -> list:
        return [
            node.attributes["href"]
            for node in tree_to_list(self.nodes, [])
            if isinstance(node, Element)
            and node.tag == "link"
            and node.attributes
            and node.attributes.get("rel") == "stylesheet"
            and "href" in node.attributes
        ]

    def load(self, url: URL) -> None:
        self.url = url
        body: str | None = url.request()
        if not body:
            return
        self.nodes: Element | Text
        if url.view_source:
            self.nodes = ViewSourceHTMLParser(body).parse()
        else:
            self.nodes = HTMLParser(body).parse()
        rules: list = DEFAULT_STYLE_SHEET.copy()
        links: list = self.get_stylesheet_links()
        for link in links:
            style_url: URL = url.resolve(link)
            try:
                body = style_url.request()
            except:
                continue
            assert body is not None
            rules.extend(CSSParser(body).parse())
        style(self.nodes, sorted(rules, key=cascade_priority))
        self.document = DocumentLayout(node=self.nodes, rtl=self.rtl)
        self.document.layout()
        self.display_list: list = []
        paint_tree(self.document, self.display_list)

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
    def draw_scrollbar(self, canvas) -> None:
        if not self.display_list:
            return
        if self._get_page_height() <= self.screen_height:
            canvas.delete("scrollbar")
            return
        coords = self.get_scrollbar_coordinates()
        if canvas.gettags("scrollbar"):
            canvas.coords(
                "scrollbar",
                coords.x0,
                coords.y0,
                coords.x1,
                coords.y1,
            )
        else:
            canvas.create_rectangle(
                coords.x0,
                coords.y0,
                coords.x1,
                coords.y1,
                fill="blue",
                tags="scrollbar",
            )

    def draw(self, canvas: tkinter.Canvas):
        for cmd in self.display_list:
            if cmd.top > self.scroll + self.screen_height:
                continue
            if cmd.bottom < self.scroll:
                continue
            cmd.execute(self.scroll, canvas)
        self.draw_scrollbar(canvas)

    def scrolldown(self) -> None:
        if not self.display_list:
            return
        if self.scroll + self.screen_height < self._get_page_height():
            self.scroll += SCROLL_STEP

    def scrollup(self) -> None:
        if self.scroll >= SCROLL_STEP:
            self.scroll -= SCROLL_STEP

    # Exercise 2.2
    def mousescroll(self, e) -> None:
        scroll_change = self.scroll - e.delta
        if (scroll_change + self.screen_height < self._get_page_height()) and (
            scroll_change > 0
        ):
            self.scroll -= e.delta

    def click(self, x: int, y: int) -> None:
        y += (
            self.scroll
        )  # Click handling goes from screen coordinates to page coordinates
        objs = [
            obj
            for obj in tree_to_list(self.document, [])
            if obj.x <= x < obj.x + obj.width and obj.y <= y < obj.y + obj.height
        ]
        if not objs:
            return
        elt: Element | Text = objs[-1].node
        while elt:
            if isinstance(elt, Text):
                pass
            elif elt.tag == "a" and "href" in elt.attributes:
                url = self.url.resolve(elt.attributes["href"])
                return self.load(url)
            elt = elt.parent
