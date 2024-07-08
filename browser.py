import socket


class URL:
    def __init__(self, url: str) -> None:
        # parse URL into host, path
        self.scheme, url = url.split("://", 1)
        assert self.scheme == "http"

        if "/" not in url:
            url = url + "/"
        self.host, url = url.split("/", 1)
        self.path = "/" + url

    def request(self) -> str:
        s = (
            socket.socket()
        )  # defaults: addr family AF_INET, type SOCKET_STREAM, protocol IPPROTO_TCP
        s.connect((self.host, 80))
        req = f"GET {self.path} HTTP/1.0\r\n"
        req += f"Host: {self.host}\r\n"
        req += "\r\n"
        s.send(req.encode("utf8"))  # encode to convert to bytes

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


def show(body):
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True  # character is in between < >
        elif c == ">":
            in_tag = False
        elif not in_tag:
            print(c, end="")  # print non-tag characters


def load(url: str):
    body = url.request()
    show(body)


if __name__ == "__main__":
    import sys

    load(URL(sys.argv[1]))
