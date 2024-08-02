from enum import Enum

SCROLLBAR_WIDTH = 20
HSTEP, VSTEP = 13, 18
WIDTH, HEIGHT = 800, 600
SCROLL_STEP = 100
TEST_FILE = "/Users/margotkriete/Desktop/test.html"
SCROLLBAR_WIDTH = 20
PORTS = {"http": 80, "https": 443}


class Alignment(Enum):
    RIGHT = 1
    CENTER = 2


class Style(Enum):
    ROMAN = "roman"
    ITALIC = "italic"


class Weight(Enum):
    BOLD = "bold"
    NORMAL = "normal"


SELF_CLOSING_TAGS = [
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
]


HEAD_TAGS = [
    "base",
    "basefont",
    "bgsound",
    "noscript",
    "link",
    "meta",
    "title",
    "style",
    "script",
]


SIBLING_TAGS = ["p", "li"]
