import tkinter.font

from constants import WIDTH
from draw import ChromeRect, DrawLine, DrawOutline, DrawText
from font_cache import get_font


class Chrome:
    def __init__(self, browser):
        self.browser = browser
        self.font: tkinter.font.Font = get_font(20, "normal", "roman")
        self.font_height: int = self.font.metrics("linespace")
        self.padding: int = 5
        self.tabbar_top = 0
        self.tabbar_bottom: int = self.font_height + 2 * self.padding
        plus_width: int = self.font.measure("+") + 2 * self.padding
        self.newtab_rect = ChromeRect(
            self.padding,
            self.padding,
            self.padding + plus_width,
            self.padding + self.font_height,
        )

    def tab_rect(self, i: int) -> ChromeRect:
        tabs_start: int = self.newtab_rect + self.padding
        tab_width = self.font.measure("Tab X") + 2 * self.padding
        return ChromeRect(
            tabs_start + tab_width * i,
            self.tabbar_top,
            tabs_start + tab_width * (i + 1),
            self.tabbar_bottom,
        )

    def paint(self) -> list:
        cmds = []
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

        return cmds
