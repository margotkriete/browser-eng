import tkinter
from typing import Literal, Optional

FONTS = {}


def get_font(
    size: int,
    weight: Literal["bold", "normal"],
    style: Literal["roman", "italic"],
    family: Optional[str] = None,
) -> tkinter.font.Font:
    key: tuple = (size, weight, style, family)
    if key not in FONTS:
        font: tkinter.font.Font
        if style not in ["roman", "italic"]:
            style = "roman"
        if not family:
            font = tkinter.font.Font(size=size, weight=weight, slant=style)
        else:
            font = tkinter.font.Font(
                size=size, weight=weight, slant=style, family=family
            )
        label: tkinter.Label = tkinter.Label(font=font)
        FONTS[key] = (font, label)
    return FONTS[key][0]
