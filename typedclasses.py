import tkinter.font
from dataclasses import dataclass


class Text:
    def __init__(self, text: str):
        self.text = text


class Tag:
    def __init__(self, tag: str):
        self.tag = tag


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
    parent: Tag
