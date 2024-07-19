from url import URL
from test_utils import socket, ssl
from unittest.mock import mock_open, patch


class TestURL:
    def test_http_parse(self):
        url = URL("http://test.test/example1")
        assert url.scheme == "http"
        assert url.host == "test.test"
        assert url.port == 80
        assert url.path == "/example1"

    def test_https_parse(self):
        url = URL("https://test.test/example1")
        assert url.scheme == "https"
        assert url.host == "test.test"
        assert url.port == 443
        assert url.path == "/example1"

    def test_about_blank_parse(self):
        url = URL("about:blank")
        assert url.scheme == "about"

    def test_file_parse(self):
        url = URL("file://test.txt")
        assert url.scheme == "file"

    def test_request_http(self):
        socket.patch().start()
        url = "http://test.test/example1"
        socket.respond(
            url, b"HTTP/1.0 200 OK\r\n" + b"Header1: Value1\r\n\r\n" + b"Body text"
        )
        body = URL(url).request()
        assert body == "Body text"

    def test_request_https(self):
        socket.patch().start()
        ssl.patch().start()
        url = "https://test.test/example1"
        socket.respond(
            url, b"HTTP/1.0 200 OK\r\n" + b"Header1: Value1\r\n\r\n" + b"Body text"
        )
        body = URL(url).request()
        assert body == "Body text"

    def test_request_file(self):
        with patch("builtins.open", mock_open(read_data="testdata")):
            url = "file://test.txt"
            body = URL(url).request()
            assert body == "testdata"

    def test_malformed_url_returns_about_blank(self):
        socket.patch().start()
        ssl.patch().start()
        url = "about:blank"
        body = URL(url).request()
        assert body is None
