import tkinter.font
from dataclasses import dataclass
from typing import Optional


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


@dataclass
class LineItem:
    x: int
    text: str
    font: tkinter.font.Font
