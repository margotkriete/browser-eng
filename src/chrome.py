import tkinter.font

from constants import WIDTH
from draw import Rect, DrawLine, DrawOutline, DrawRect, DrawText
from font_cache import get_font
from url import URL


class Chrome:
    def __init__(self, browser):
        self.browser = browser
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

    def click(self, x: int, y: int):
        if self.newtab_rect.contains_point(x, y):
            self.browser.new_tab(URL("https://browser.engineering/"))
        else:
            for i, tab in enumerate(self.browser.tabs):
                if self.tab_rect(i).contains_point(x, y):
                    self.browser.active_tab = tab
                    break

    def tab_rect(self, i: int) -> Rect:
        tabs_start: int = self.newtab_rect.right + self.padding
        tab_width = self.font.measure("Tab X") + 2 * self.padding
        return Rect(
            tabs_start + tab_width * i,
            self.tabbar_top,
            tabs_start + tab_width * (i + 1),
            self.tabbar_bottom,
        )

    def paint(self) -> list:
        cmds = []
        cmds.append(DrawRect(Rect(0, 0, WIDTH, self.bottom), "white"))
        cmds.append(DrawLine(0, self.bottom, WIDTH, self.bottom, "black", 1))
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
                        bounds.right, bounds.bottom, WIDTH, bounds.bottom, "black", 1
                    )
                )
        cmds.append(DrawOutline(self.address_rect, "black", 1))
        url_string = str(self.browser.active_tab.url)
        cmds.append(
            DrawText(
                self.address_rect.left + self.padding,
                self.address_rect.top,
                url_string,
                self.font,
                "black",
            )
        )
        return cmds
