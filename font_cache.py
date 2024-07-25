import tkinter
from typing import Optional

FONTS = {}


def get_font(
    size: int, weight: str, style: str, family: Optional[str] = None
) -> tkinter.font.Font:
    key: tuple = (size, weight, style, family)
    if key not in FONTS:
        font: tkinter.font.Font = tkinter.font.Font(
            size=size, weight=weight, slant=style, family=family
        )
        label: tkinter.Label = tkinter.Label(font=font)
        FONTS[key] = (font, label)
    return FONTS[key][0]
