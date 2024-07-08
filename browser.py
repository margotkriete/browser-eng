import socket
import ssl


TEST_FILE = "/Users/margotkriete/Desktop/test.txt"


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


def show(body: str) -> None:
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True  # character is in between < >
        elif c == ">":
            in_tag = False
        elif not in_tag:
            print(c, end="")  # print non-tag characters


def load(url: str) -> None:
    body = url.request()
    show(body)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        load(URL(sys.argv[1]))
    else:
        load(URL(f"file://{TEST_FILE}"))
