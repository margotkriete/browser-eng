import socket
import ssl
import tkinter

WIDTH, HEIGHT = 800, 600
SCROLL_STEP = 100
TEST_FILE = "/Users/margotkriete/Desktop/test.txt"
HSTEP, VSTEP = 13, 18


class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.window, width=WIDTH, height=HEIGHT)
        self.canvas.pack()
        self.scroll = 0
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<MouseWheel>", self.mousescroll)

    def load(self, url: str) -> None:
        body = url.request()
        text = lex(body)
        self.display_list = layout(text)
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        for x, y, c in self.display_list:
            if y > self.scroll + HEIGHT:
                continue
            if y + VSTEP < self.scroll:
                continue
            self.canvas.create_text(x, y - self.scroll, text=c)

    def scrolldown(self, e):
        self.scroll += SCROLL_STEP
        self.draw()

    def scrollup(self, e):
        if self.scroll >= SCROLL_STEP:
            self.scroll -= SCROLL_STEP
        self.draw()

    def mousescroll(self, e):
        self.scroll -= e.delta
        self.draw()


def layout(text) -> "list[tuple[int, int, str]]":
    cursor_x, cursor_y = HSTEP, VSTEP
    display_list = []
    for c in text:
        if c == "\n":
            cursor_y += VSTEP
            cursor_x = HSTEP
        display_list.append((cursor_x, cursor_y, c))
        cursor_x += HSTEP
        if cursor_x >= WIDTH - HSTEP:
            cursor_y += VSTEP
            cursor_x = HSTEP
    return display_list


class URL:
    def __init__(self, url: str) -> None:
        self.scheme, url = url.split("://", 1)
        assert self.scheme in ["http", "https", "file"]

        if self.scheme == "http" or self.scheme == "file":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443

        if "/" not in url:
            url = url + "/"

        if self.scheme != "file":
            self.host, url = url.split("/", 1)
            self.path = "/" + url
            if ":" in self.host:
                self.host, port = self.host.split(":", 1)
                self.port = int(port)
        else:
            self.host = "localhost"
            self.path = url

    def append_header(self, req, header, val) -> str:
        req += f"{header}: {val}\r\n"
        return req

    def request(self) -> str:
        if self.scheme == "file":
            with open(self.path, encoding="utf-8") as f:
                return f.read()
        else:
            s = (
                socket.socket()
            )  # defaults: addr family AF_INET, type SOCKET_STREAM, protocol IPPROTO_TCP
            s.connect((self.host, self.port))

            if self.scheme == "https":
                ctx = ssl.create_default_context()
                s = ctx.wrap_socket(s, server_hostname=self.host)

            req = f"GET {self.path} HTTP/1.0\r\n"
            req = self.append_header(req, "Host", self.host)
            req = self.append_header(req, "Connection", "close")
            req = self.append_header(req, "User-Agent", "Margot's Browser")
            req += "\r\n"
            s.send(req.encode("utf8"))  # convert to bytes

            response = s.makefile("r", encoding="utf8", newline="\r\n")
            statusline = response.readline()
            version, status, explanation = statusline.split(" ", 2)

            response_headers = {}
            while True:
                line = response.readline()
                if line == "\r\n":
                    break
                header, value = line.split(":", 1)
                response_headers[header.casefold()] = value.strip()

            assert (
                "transfer-encoding" not in response_headers
            )  # update these in exercise
            assert (
                "content-encoding" not in response_headers
            )  # update these in exercise

            content = response.read()
            s.close()
            return content


def lex(body: str) -> str:
    text = ""
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True  # character is in between < >
        elif c == ">":
            in_tag = False
        elif not in_tag:
            text += c
    return text


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        Browser().load(URL(sys.argv[1]))
        tkinter.mainloop()
    else:
        Browser().load(URL(f"file://{TEST_FILE}"))
