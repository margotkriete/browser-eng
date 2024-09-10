import tkinter.font

from constants import WIDTH
from draw import Rect, DrawLine, DrawOutline, DrawRect, DrawText
from font_cache import get_font
from url import URL


class Chrome:
    def __init__(self, browser):
        self.browser = browser
        self.browser_width = self.browser.screen_width
        self.font: tkinter.font.Font = get_font(20, "normal", "roman")
        self.font_height: int = self.font.metrics("linespace")
        self.padding: int = 5
        self.tabbar_top = 0
        self.tabbar_bottom: int = self.font_height + 2 * self.padding
        plus_width: int = self.font.measure("+") + 2 * self.padding
        self.newtab_rect = Rect(
            self.padding,
            self.padding,
            self.padding + plus_width,
            self.padding + self.font_height,
        )
        self.bottom = self.tabbar_bottom
        self.urlbar_top = self.tabbar_bottom
        self.urlbar_bottom = self.urlbar_top + self.font_height + 2 * self.padding
        self.bottom = self.urlbar_bottom

        back_width = self.font.measure("<") + 2 * self.padding
        self.back_rect = Rect(
            self.padding,
            self.urlbar_top + self.padding,
            self.padding + back_width,
            self.urlbar_bottom - self.padding,
        )
        self.address_rect = Rect(
            self.back_rect.top + self.padding,
            self.urlbar_top + self.padding,
            self.browser_width - self.padding,
            self.urlbar_bottom - self.padding,
        )
        self.focus = None
        self.address_bar = ""

    def click(self, x: int, y: int):
        self.focus = None
        if self.newtab_rect.contains_point(x, y):
            self.browser.new_tab(URL("https://browser.engineering/"))
        elif self.back_rect.contains_point(x, y):
            self.browser.active_tab.go_back()
        elif self.address_rect.contains_point(x, y):
            self.focus = "address bar"
            self.address_bar = ""
        else:
            for i, tab in enumerate(self.browser.tabs):
                if self.tab_rect(i).contains_point(x, y):
                    self.browser.active_tab = tab
                    break

    def keypress(self, char: str):
        if self.focus == "address bar":
            self.address_bar += char

    def backspace(self):
        if self.focus == "address bar":
            self.address_bar = self.address_bar[:-1]

    def enter(self):
        if self.focus == "address bar":
            self.browser.active_tab.load(URL(self.address_bar))
            self.focus = None

    def tab_rect(self, i: int) -> Rect:
        tabs_start: int = self.newtab_rect.right + self.padding
        tab_width = self.font.measure("Tab X") + 2 * self.padding
        return Rect(
            tabs_start + tab_width * i,
            self.tabbar_top,
            tabs_start + tab_width * (i + 1),
            self.tabbar_bottom,
        )

    def _paint_new_tab_button(self, cmds):
        cmds.append(DrawRect(Rect(0, 0, self.browser_width, self.bottom), "white"))
        cmds.append(
            DrawLine(0, self.bottom, self.browser_width, self.bottom, "black", 1)
        )
        cmds.append(DrawOutline(self.newtab_rect, "black", 1))
        cmds.append(
            DrawText(
                self.newtab_rect.left + self.padding,
                self.newtab_rect.top,
                "+",
                self.font,
                "black",
            )
        )

    def _paint_tabs(self, cmds):
        for i, tab in enumerate(self.browser.tabs):
            bounds = self.tab_rect(i)
            cmds.append(
                DrawLine(bounds.left, 0, bounds.left, bounds.bottom, "black", 1)
            )
            cmds.append(
                DrawLine(bounds.right, 0, bounds.right, bounds.bottom, "black", 1)
            )
            cmds.append(
                DrawText(
                    bounds.left + self.padding,
                    bounds.top + self.padding,
                    f"Tab {i}",
                    self.font,
                    "black",
                )
            )
            if tab == self.browser.active_tab:
                cmds.append(
                    DrawLine(0, bounds.bottom, bounds.left, bounds.bottom, "black", 1)
                )
                cmds.append(
                    DrawLine(
                        bounds.right,
                        bounds.bottom,
                        self.browser_width,
                        bounds.bottom,
                        "black",
                        1,
                    )
                )

    def _paint_address_bar(self, cmds):
        cmds.append(DrawOutline(self.address_rect, "black", 1))
        if self.focus == "address bar":
            cmds.append(
                DrawText(
                    self.address_rect.left + self.padding,
                    self.address_rect.top,
                    self.address_bar,
                    self.font,
                    "black",
                )
            )
            w = self.font.measure(self.address_bar)
            cmds.append(
                DrawLine(
                    self.address_rect.left + self.padding + w,
                    self.address_rect.top,
                    self.address_rect.left + self.padding + w,
                    self.address_rect.bottom,
                    "red",
                    1,
                )
            )
        else:
            url = str(self.browser.active_tab.url)
            cmds.append(
                DrawText(
                    self.address_rect.left + self.padding,
                    self.address_rect.top,
                    url,
                    self.font,
                    "black",
                )
            )

    def _paint_back_button(self, cmds):
        cmds.append(DrawOutline(self.back_rect, "black", 1))
        cmds.append(
            DrawText(
                self.back_rect.left + self.padding,
                self.back_rect.top,
                "<",
                self.font,
                "black",
            )
        )

    def paint(self) -> list:
        cmds = []
        self._paint_new_tab_button(cmds)
        self._paint_tabs(cmds)
        self._paint_address_bar(cmds)
        self._paint_back_button(cmds)

        return cmds
