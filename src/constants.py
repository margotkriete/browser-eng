from enum import Enum

# Geometry
SCROLLBAR_WIDTH = 20
HSTEP, VSTEP = 13, 18
WIDTH, HEIGHT = 800, 600
SCROLL_STEP = 100
SCROLLBAR_WIDTH = 20

# URL parsing
TEST_FILE = "/Users/margotkriete/Desktop/test.html"
PORTS = {"http": 80, "https": 443}

# HTML parsing
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

# Layout
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


# Styling
class Alignment(Enum):
    RIGHT = 1
    CENTER = 2


class Style(Enum):
    ROMAN = "roman"
    ITALIC = "italic"


class Weight(Enum):
    BOLD = "bold"
    NORMAL = "normal"


# CSS parsing
INHERTIED_PROPERTIES = {
    "font-size": "16px",
    "font-style": "normal",
    "font-weight": "normal",
    "color": "black",
    "font-family": "Times New Roman",
}
