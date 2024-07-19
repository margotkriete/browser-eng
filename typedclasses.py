import tkinter.font
from dataclasses import dataclass


@dataclass
class ScrollbarCoordinate:
    x0: int
    y0: int
    x1: int
    y1: int


@dataclass
class DisplayListItem:
    x: int
    y: int
    text: str
    font: tkinter.font.Font
