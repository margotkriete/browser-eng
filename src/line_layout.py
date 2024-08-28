from typing import Literal

from constants import Style
from draw import DrawText
from font_cache import get_font


class LineLayout:
    def __init__(self, node, parent, previous):
        self.node = node
        self.parent = parent
        self.previous = previous
        self.children = []

    def layout(self):
        self.width = self.parent.width
        self.x = self.parent.x
        if self.previous:
            self.y = self.previous.y + self.previous.height
        else:
            self.y = self.parent.y

        for word in self.children:
            word.layout()

        if not self.children:
            self.height = 0
            return

        max_ascent = max([word.font.metrics("ascent") for word in self.children])

        baseline = self.y + 1.25 * max_ascent
        for word in self.children:
            word.y = baseline - word.font.metrics("ascent")
        max_descent = max([word.font.metrics("descent") for word in self.children])
        self.height = 1.25 * (max_ascent + max_descent)

    def paint(self) -> list:
        return []


class TextLayout:
    def __init__(self, node, word, parent, previous):
        self.node = node
        self.word = word
        self.children = []
        self.parent = parent
        self.previous = previous

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
        color = self.node.style["color"]
        return [DrawText(self.x, self.y, self.word, self.font, color)]
