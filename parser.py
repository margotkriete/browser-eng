import re


class Text:
    def __init__(self, text: str, parent):
        self.text: str = text
        # Children here is never used? TODO: remove?
        self.children: list[str] = []
        self.parent = parent


class Element:
    def __init__(self, tag: str, parent):
        self.tag = tag
        self.children: list[str] = []
        self.parent = parent


class HTMLParser:
    def __init__(self, body: str):
        self.body: str = body
        self.unfinished = []

    def parse(self, body: str, view_source: bool = False) -> list[Element | Text]:
        buffer = ""
        out: list[Element | Text] = []
        in_tag = False

        title = re.search("<title>(.*)</title>", body)
        title_text = ""
        if title:
            title_text = title.group(1)
        body = body.replace(title_text, "")
        # body = body.replace("&gt;", ">")
        # body = body.replace("&lt;", "<")

        if view_source:
            out.append(Text(body))
            return out

        for c in body:
            if c == "<":
                in_tag = True  # word is in between < >
                if buffer:
                    out.append(Text(buffer))
                buffer = ""
            elif c == ">":
                in_tag = False
                out.append(Element(buffer))
                buffer = ""
            else:
                buffer += c
        if not in_tag and buffer:
            out.append(Text(buffer))
        return out
