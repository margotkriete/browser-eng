import argparse
import tkinter
import tkinter.font
from typing import Optional

from chrome import Chrome
from constants import HEIGHT, TEST_FILE, WIDTH
from tab import Tab
from url import URL


class Browser:
    def __init__(self):
        self.tabs: list[Tab] = []
        self.active_tab: Optional[Tab] = None
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.window, width=WIDTH, height=HEIGHT)
        self.canvas.pack(fill="both", expand=1)
        self.chrome = Chrome(self)
        self.window.bind("<Down>", self.handle_down)
        self.window.bind("<Up>", self.handle_up)
        # self.window.bind("<Configure>", self.resize)
        self.window.bind("<Button-1>", self.handle_click)

    def handle_up(self, e):
        self.active_tab.scrollup()
        self.draw()

    def handle_down(self, e):
        self.active_tab.scrolldown()
        self.draw()

    def handle_click(self, e):
        if e.y < self.chrome.bottom:
            self.chrome.click(e.x, e.y)
        else:
            # Subtract chrome size when clicking tab contents
            tab_y = e.y - self.chrome.bottom
            self.active_tab.click(e.x, tab_y)
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        self.active_tab.draw(self.canvas, self.chrome.bottom)
        for cmd in self.chrome.paint():
            cmd.execute(0, self.canvas)

    def new_tab(self, url):
        new_tab = Tab(HEIGHT - self.chrome.bottom)
        new_tab.load(url)
        self.active_tab = new_tab
        self.tabs.append(new_tab)
        self.draw()

    # # Exercise 2.3
    # def resize(self, e: tkinter.Event) -> None:
    #     self.screen_height = e.height
    #     self.screen_width = e.width
    #     self.document = DocumentLayout(node=self.nodes, width=e.width, rtl=self.rtl)
    #     self.document.layout()
    #     self.display_list = []
    #     paint_tree(self.document, self.display_list)


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
    Browser().new_tab(URL(args.url))
    tkinter.mainloop()
