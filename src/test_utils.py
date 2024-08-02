# mypy: ignore-errors

import io
import tkinter.font
from unittest import mock


"""
The classes in this file are pulled from
https://github.com/browserengineering/book/blob/33177b132c8bca4e02f38b9d88ab8b94605d62c2/src/test.py.

"""


class socket:
    URLs = {}
    Requests = {}

    def __init__(self, *args, **kwargs):
        self.request = b""
        self.connected = False

    def connect(self, host_port):
        self.scheme = "http"
        self.host, self.port = host_port
        self.connected = True

    def send(self, text):
        self.request += text
        self.method, self.path, _ = self.request.decode("latin1").split(" ", 2)

        if self.method == "POST":
            beginning, self.body = self.request.decode("latin1").split("\r\n\r\n")
            headers = [item.split(": ") for item in beginning.split("\r\n")[1:]]
            assert any(name.casefold() == "content-length" for name, value in headers)
            assert all(
                int(value) == len(self.body)
                for name, value in headers
                if name.casefold() == "content-length"
            )

    def makefile(self, mode, encoding=None, newline=None):
        assert self.connected and self.host and self.port
        if self.port == 80 and self.scheme == "http":
            url = self.scheme + "://" + self.host + self.path
        elif self.port == 443 and self.scheme == "https":
            url = self.scheme + "://" + self.host + self.path
        else:
            url = self.scheme + "://" + self.host + ":" + str(self.port) + self.path
        self.Requests.setdefault(url, []).append(self.request)
        assert (
            self.method == self.URLs[url][0]
        ), f"Made a {self.method} request to a {self.URLs[url][0]} URL"
        output = self.URLs[url][1]
        if self.URLs[url][2]:
            assert self.body == self.URLs[url][2], (self.body, self.URLs[url][2])
        stream = io.BytesIO(output)
        if encoding:
            stream = io.TextIOWrapper(stream, encoding=encoding, newline=newline)
            stream.mode = mode
        else:
            assert mode == "b", "If no file encoding is passed, must pass 'b' mode"

        return stream

    def close(self):
        self.connected = False

    @classmethod
    def patch(cls):
        return mock.patch("socket.socket", wraps=cls)

    @classmethod
    def respond(cls, url, response, method="GET", body=None):
        cls.URLs[url] = [method, response, body]

    @classmethod
    def respond_ok(cls, url, response, method="GET", body=None):
        response = ("HTTP/1.0 200 OK\r\n\r\n" + response).encode("utf8")
        cls.URLs[url] = [method, response, body]

    @classmethod
    def serve(cls, html):
        html = html.encode("utf8") if isinstance(html, str) else html
        response = b"HTTP/1.0 200 OK\r\n"
        response += b"Content-Type: text/html\r\n"
        response += b"Content-Length: " + str(len(html)).encode("ascii") + b"\r\n"
        response += b"\r\n" + html
        prefix = "http://test/"
        url = next(
            prefix + str(i) for i in range(1000) if prefix + str(i) not in cls.URLs
        )
        cls.respond(url, response)
        return url

    @classmethod
    def made_request(cls, url):
        return url in cls.Requests

    @classmethod
    def last_request(cls, url):
        return cls.Requests[url][-1]

    @classmethod
    def clear_history(cls):
        cls.Requests = {}


class ssl:
    def wrap_socket(self, s, server_hostname):
        assert s.host == server_hostname
        s.scheme = "https"
        return s

    @classmethod
    def patch(cls):
        return mock.patch("ssl.create_default_context", wraps=cls)


class SilentTk:
    def bind(self, event, callback):
        pass


class TkFont:
    def __init__(self, size=None, weight=None, slant=None, style=None, family=None):
        self.size = size
        self.weight = weight
        self.slant = slant
        self.style = style
        self.family = family

    def measure(self, word):
        return self.size * len(word)

    def metrics(self, name=None):
        all = {
            "ascent": self.size * 0.75,
            "descent": self.size * 0.25,
            "linespace": self.size,
        }
        if name:
            return all[name]
        return all

    def __repr__(self):
        return "Font size={} weight={} slant={} style={} family={}".format(
            self.size, self.weight, self.slant, self.style, self.family
        )


tkinter.font.Font = TkFont


class TkLabel:
    def __init__(self, font):
        pass


tkinter.Label = TkLabel


class SilentCanvas:
    def __init__(self, *args, **kwargs):
        pass

    def create_text(self, x, y, text, **kwargs):
        pass

    def create_rectangle(self, x1, y1, x2, y2, **kwargs):
        pass

    def pack(self, **kwargs):
        pass

    def delete(self, v):
        pass

    def gettags(self, tags):
        pass


tkinter.Canvas = SilentCanvas
