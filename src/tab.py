import os
import tkinter
from parser import Element, HTMLParser, Text, ViewSourceHTMLParser

from constants import HEIGHT, SCROLL_STEP, SCROLLBAR_WIDTH, VSTEP, WIDTH
from css_parser import CSSParser, style
from document_layout import DocumentLayout
from helpers import cascade_priority, paint_tree, tree_to_list
from typedclasses import ScrollbarCoordinate
from url import URL


class Tab:
    def __init__(self, tab_height: int, screen_height=HEIGHT, screen_width=WIDTH):
        self.scroll = 0
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.view_source = False
        self.url = None
        self.tab_height = tab_height
        self.history: list = []

    def _get_page_height(self) -> int:
        return self.tab_height

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

    def load_style_sheet(self) -> CSSParser:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        return CSSParser(open(os.path.join(dir_path, "browser.css")).read()).parse()

    def load(self, url: URL) -> None:
        self.history.append(url)
        self.url = url
        body: str | None = url.request()
        if not body:
            return
        self.nodes: Element | Text
        if url.view_source:
            self.nodes = ViewSourceHTMLParser(body).parse()
        else:
            self.nodes = HTMLParser(body).parse()
        rules: list = self.load_style_sheet().copy()
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
        self.document = DocumentLayout(node=self.nodes)
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

    def draw(self, canvas: tkinter.Canvas, offset: int):
        for cmd in self.display_list:
            if cmd.rect.top > self.scroll + self.tab_height:
                continue
            if cmd.rect.bottom < self.scroll:
                continue
            cmd.execute(self.scroll - offset, canvas)
        self.draw_scrollbar(canvas)

    def scrolldown(self) -> None:
        if not self.display_list:
            return
        max_y = max(self.document.height + 2 * VSTEP - self.tab_height, 0)
        self.scroll = min(self.scroll + SCROLL_STEP, max_y)

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

    def go_back(self):
        if len(self.history) > 1:
            self.history.pop()
            back: URL = self.history.pop()
            self.load(back)
