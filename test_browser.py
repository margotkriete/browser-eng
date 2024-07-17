from browser import Browser
from test_utils import socket
from url import URL


class TestBrowser:
    def test_browser_load(self):
        _ = socket.patch().start()
        url = "http://test.test/example1"
        socket.respond(
            url, b"HTTP/1.0 200 OK\r\n" + b"Header1: Value1\r\n\r\n" + b"Body text"
        )
        browser = Browser()
        browser.load(URL(url))
        assert browser.display_list is not None
