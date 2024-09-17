from tkinter import Text
from typing import Literal

from constants import Style, INPUT_WIDTH_PX
from draw import DrawRect, DrawText
from font_cache import get_font


class InputLayout:
    def __init__(self, node, parent, previous):
        self.node = node
        self.children = []
        self.parent = parent
        self.previous = previous
        self.width = INPUT_WIDTH_PX

    def layout(self):
        weight: Literal["bold", "normal"] = self.node.style["font-weight"]
        style: Literal["roman", "italic"] = self.node.style["font-style"]
        family: str = self.node.style["font-family"]

        # Convert normal -> roman style and CSS pixels -> Tk points
        if style == "normal":
            style = Style.ROMAN.value
        size: int = int(float(self.node.style["font-size"][:-2]) * 0.75)

        self.font = get_font(size, weight, style, family)
        self.width = self.font.measure(self.word)
        # Compute x field; y is computed in LineLayout
        if self.previous:
            space: int = self.previous.font.measure(" ")
            self.x: int = self.previous.x + space + self.previous.width
        else:
            self.x = self.parent.x

        self.height = self.font.metrics("linespace")

    def paint(self) -> list:
        cmds = []
        bgcolor = self.node.style.get("background-color", "transparent")
        if bgcolor != "transparent":
            rect = DrawRect(self.self_rect(), bgcolor)
            cmds.append(rect)
        text = ""
        if self.node.tag == "input":
            text = self.node.attributes.get("value", "")
        elif self.node.tag == "button":
            if len(self.node.children) == 1 and isinstance(self.node.children[0], Text):
                text = self.node.children[0].text
            else:
                print("ignoring comments within button")
        color = self.node.style["color"]
        cmds.append(DrawText(self.x, self.y, text, self.font, color))
        return cmds
