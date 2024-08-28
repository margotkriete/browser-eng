import tkinter.font


class DrawText:
    def __init__(
        self, x1: int, y1: int, text: str, font: tkinter.font.Font, color: str
    ):
        self.top = y1
        self.left = x1
        self.text = text
        self.font = font
        self.bottom = y1 + font.metrics("linespace")
        self.color = color

    def execute(self, scroll: int, canvas):
        canvas.create_text(
            self.left,
            self.top - scroll,
            text=self.text,
            font=self.font,
            fill=self.color,
            anchor="nw",
            tag="text",
        )


class DrawOutline:
    def __init__(self, rect, color: str, thickness: int):
        self.rect = rect
        self.color = color
        self.thickness = thickness

    def execute(self, scroll, canvas: tkinter.Canvas):
        canvas.create_rectangle(
            self.rect.left,
            self.rect.top - scroll,
            self.rect.right,
            self.rect.bottom - scroll,
            width=self.thickness,
            outline=self.color,
        )


class DrawRect:
    def __init__(self, x1: int, y1: int, x2: int, y2: int, color: str):
        self.top = y1
        self.left = x1
        self.bottom = y2
        self.right = x2
        self.color = color

    def execute(self, scroll, canvas):
        canvas.create_rectangle(
            self.left,
            self.top - scroll,
            self.right,
            self.bottom - scroll,
            width=0,
            fill=self.color,
            tag="text",
        )


class DrawLine:
    def __init__(self, x1: int, y1: int, x2: int, y2: int, color: str, thickness: int):
        self.rect = ChromeRect(x1, y1, x2, y2)
        self.color = color
        self.thickness = thickness

    def execute(self, scroll, canvas):
        canvas.create_line(
            self.rect.left,
            self.rect.top - scroll,
            self.rect.right,
            self.rect.bottom - scroll,
            fill=self.color,
            width=self.thickness,
        )


# TODO: can this be a dataclass?
class ChromeRect:
    def __init__(self, left, top, right, bottom):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom
