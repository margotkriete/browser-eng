from typing import Optional

from block_layout import BlockLayout
from constants import WIDTH, HSTEP, VSTEP


class DocumentLayout:
    def __init__(self, node):
        self.node = node
        self.parent = None
        self.children = []
        self.width: Optional[int] = None
        self.height: int = None
        self.x: int = 0
        self.y: int = 0

    def layout(self):
        child = BlockLayout(self.node, self, None)
        self.children.append(child)
        self.width = WIDTH - 2 * HSTEP
        self.x = HSTEP
        self.y = VSTEP
        child.layout()
        self.height = child.height

    def paint(self):
        return []
