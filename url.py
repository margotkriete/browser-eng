import socket
import ssl


PORTS = {"http": 80, "https": 443}


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

        content = response.read()
        s.close()
        return content
