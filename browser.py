import argparse
import socket
import ssl
import tkinter
from tkinter import ttk

WIDTH, HEIGHT = 800, 600
SCROLL_STEP = 100
TEST_FILE = "/Users/margotkriete/Desktop/test.txt"
HSTEP, VSTEP = 13, 18
PORTS = {"http": 80, "https": 443}


class Browser:
    def __init__(self, right_to_left: bool = False):
        self.window = tkinter.Tk()
        style = ttk.Style()
        style.configure("TScrollbar", background="#002fa7")
        self.scrollbar = ttk.Scrollbar(self.window, style="TScrollbar")
        self.scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.canvas = tkinter.Canvas(
            self.window,
            width=WIDTH,
            height=HEIGHT,
            yscrollcommand=self.scrollbar.set,
            scrollregion=(0, 0, HEIGHT, WIDTH),
        )
        self.scrollbar.config(command=self.scrollbar_handler)
        # self.scrollbar.config(command=self.canvas.yview)
        self.canvas.pack(fill="both", expand=1)
        self.scroll = 0
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<MouseWheel>", self.mousescroll)
        self.window.bind("<Configure>", self.resize)
        self.screen_height = HEIGHT
        self.right_to_left = False

    def _get_max_coordinate(self):
        return self.display_list[len(self.display_list) - 1][1]

    # Exercise 2.4: WIP, does not work properly
    def scrollbar_handler(self, *opts):
        op, quantity = opts[0], opts[1]
        updated_scroll = self.scroll + float(quantity) * HEIGHT
        if updated_scroll < self._get_max_coordinate():
            self.scroll = updated_scroll
            self.draw()

    def load(self, url: str) -> None:
        body = url.request()
        self.text = lex(body)
        self.display_list = layout(self.text, right_to_left=self.right_to_left)
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        for x, y, c in self.display_list:
            if y > self.scroll + self.screen_height:
                continue
            if y + VSTEP < self.scroll:
                continue
            self.canvas.create_text(x, y - self.scroll, text=c)

    def scrolldown(self, e):
        updated_scroll = self.scroll + SCROLL_STEP + self.screen_height
        if updated_scroll < self._get_max_coordinate():
            self.scroll += SCROLL_STEP
            self.draw()

    def scrollup(self, e):
        if self.scroll >= SCROLL_STEP:
            self.scroll -= SCROLL_STEP
        self.draw()

    # Exercise 2.2
    def mousescroll(self, e):
        updated_scroll = self.scroll - e.delta + self.screen_height
        if (updated_scroll < self._get_max_coordinate()) and (
            self.scroll - e.delta > 0
        ):
            self.scroll -= e.delta
            self.draw()

    # Exercise 2.3
    def resize(self, e):
        self.screen_height = e.height
        self.display_list = layout(self.text, e.width, self.right_to_left)
        self.draw()


def layout(
    text: str, width: int = WIDTH, right_to_left: bool = False
) -> "list[tuple[int, int, str]]":
    if right_to_left:
        return layout_right_to_left(text, width)

    cursor_x, cursor_y = HSTEP, VSTEP
    display_list = []
    for c in text:
        if c == "\n":
            cursor_y += VSTEP
            cursor_x = HSTEP
        display_list.append((cursor_x, cursor_y, c))
        cursor_x += HSTEP
        if cursor_x >= width - HSTEP:
            cursor_y += VSTEP
            cursor_x = HSTEP
    return display_list


# Exercise 2.7
def layout_right_to_left(text: str, width: int = WIDTH):
    # TODO
    return


class URL:

    def __init__(self, url: str) -> None:
        try:
            if url.startswith("data"):
                self.scheme, url = url.split(":", 1)
            else:
                self.scheme, url = url.split("://", 1)
        except ValueError:
            self.scheme = "about"
            return

        self.port = PORTS.get(self.scheme, None)

        if "/" not in url:
            url = url + "/"

        if self.scheme in ["http", "https"]:
            self.host, url = url.split("/", 1)
            self.path = "/" + url
            if ":" in self.host:
                self.host, port = self.host.split(":", 1)
                self.port = int(port)
        elif self.scheme == "file":
            self.host = "localhost"
            self.path = url
        else:
            self.media_type, self.data = url.split(",", 1)

    def append_header(self, req, header, val) -> str:
        req += f"{header}: {val}\r\n"
        return req

    def request(self):
        if self.scheme in ["http", "https"]:
            return self._request_http()

        if self.scheme == "data":
            return self._request_data()

        if self.scheme == "file":
            return self._request_file()

        if self.scheme == "about":
            return self._request_about_blank()

    def _request_file(self) -> str:
        with open(self.path, encoding="utf-8") as f:
            return f.read()

    def _request_data(self) -> str:
        return self.data

    # Exercise 2.6
    def _request_about_blank(self) -> str:
        return ""

    def _request_http(self) -> str:
        s = (
            socket.socket()
        )  # defaults: addr family AF_INET, type SOCKET_STREAM, protocol IPPROTO_TCP
        s.connect((self.host, self.port))

        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)

        req = f"GET {self.path} HTTP/1.1\r\n"
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

        assert "transfer-encoding" not in response_headers  # update these in exercise
        assert "content-encoding" not in response_headers  # update these in exercise

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
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-r", help="Lay characters from right to left", action="store_true"
    )
    parser.add_argument(
        "url",
        metavar="URL",
        default=f"file://{TEST_FILE}",
        help="URL to serve",
        nargs="?",
    )
    args = parser.parse_args()
    Browser(right_to_left=args.r).load(URL(args.url))
    tkinter.mainloop()
