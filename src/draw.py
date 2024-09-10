import tkinter.font


class Rect:
    def __init__(self, left, top, right, bottom):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    def contains_point(self, x: int, y: int) -> bool:
        return x >= self.left and x < self.right and y >= self.top and y < self.bottom


class DrawText:
    def __init__(
        self, x1: int, y1: int, text: str, font: tkinter.font.Font, color: str
    ):
        self.rect = Rect(
            x1, y1, x1 + font.measure(text), y1 + font.metrics("linespace")
        )
        self.text = text
        self.font = font
        self.color = color

    def execute(self, scroll, canvas):
        canvas.create_text(
            self.rect.left,
            self.rect.top - scroll,
            text=self.text,
            font=self.font,
            anchor="nw",
            fill=self.color,
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
    def __init__(self, rect: Rect, color: str):
        self.rect = rect
        self.color = color

    def execute(self, scroll, canvas):
        canvas.create_rectangle(
            self.rect.left,
            self.rect.top - scroll,
            self.rect.right,
            self.rect.bottom - scroll,
            width=0,
            fill=self.color,
            tag="text",
        )


class DrawLine:
    def __init__(self, x1: int, y1: int, x2: int, y2: int, color: str, thickness: int):
        self.rect = Rect(x1, y1, x2, y2)
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
