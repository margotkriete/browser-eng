from typing import Optional

from block_layout import BlockLayout
from constants import WIDTH, HSTEP, VSTEP


class DocumentLayout:
    def __init__(self, node, width: Optional[int] = WIDTH, rtl: bool = False):
        self.node = node
        self.parent = None
        self.children: list[BlockLayout] = []
        self.width = width
        self.height: int = 0
        self.x: int = 0
        self.y: int = 0
        self.rtl = rtl

    def layout(self):
        child = BlockLayout(self.node, self, None, rtl=self.rtl)
        self.children.append(child)
        self.width = self.width - 2 * HSTEP
        self.x = HSTEP
        self.y = VSTEP
        child.layout()
        self.height = child.height

    def paint(self):
        return []
