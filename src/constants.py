from enum import Enum

SCROLLBAR_WIDTH = 20
HSTEP, VSTEP = 13, 18
WIDTH, HEIGHT = 800, 600
SCROLL_STEP = 100
TEST_FILE = "/Users/margotkriete/Desktop/test.html"
SCROLLBAR_WIDTH = 20
PORTS = {"http": 80, "https": 443}
INLINE_LAYOUT = "inline"
BLOCK_LAYOUT = "block"
BLOCK_ELEMENTS = [
    "html",
    "body",
    "article",
    "section",
    "nav",
    "aside",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hgroup",
    "header",
    "footer",
    "address",
    "p",
    "hr",
    "pre",
    "blockquote",
    "ol",
    "ul",
    "menu",
    "li",
    "dl",
    "dt",
    "dd",
    "figure",
    "figcaption",
    "main",
    "div",
    "table",
    "form",
    "fieldset",
    "legend",
    "details",
    "summary",
]


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

HEAD_TAG = "head"
HTML_TAG = "html"
BODY_TAG = "body"
CLOSING_HTML_TAG = "/html"
CLOSING_HEAD_TAG = "/head"


SIBLING_TAGS = ["p", "li"]

# TODO: fill out missing "text-like" elements - look at spec
TEXT_LIKE_TAGS = ["b", "i"]
