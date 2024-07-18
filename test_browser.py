import test_utils
from browser import Browser
from test_utils import socket
from url import URL
from constants import HSTEP


class TestBrowser:
    def test_browser_load(self):
        _ = socket.patch().start()
        url = "http://test.test/example1"
        socket.respond(
            url, b"HTTP/1.0 200 OK\r\n" + b"Header1: Value1\r\n\r\n" + b"Body text"
        )
        browser = Browser()
        browser.load(URL(url))

        assert len(browser.display_list) == 2
        first_word = browser.display_list[0]
        second_word = browser.display_list[1]
        assert first_word[2] == "Body"
        assert second_word[2] == "text"

        # "Body" should have a smaller x coordinate than "text"
        assert first_word[0] < second_word[0]
        assert first_word[0] == HSTEP

        # Words should have the same y coordinate
        assert first_word[1] == second_word[1]

    def test_browser_load_rtl(self):
        _ = socket.patch().start()
        url = "http://test.test/example1"
        socket.respond(
            url, b"HTTP/1.0 200 OK\r\n" + b"Header1: Value1\r\n\r\n" + b"Body text"
        )
        browser = Browser(rtl=True)
        browser.load(URL(url))

        assert len(browser.display_list) == 2
        first_word = browser.display_list[0]
        second_word = browser.display_list[1]
        assert first_word[2] == "Body"
        assert second_word[2] == "text"

        # "Body" should have a smaller x coordinate than "text"
        assert first_word[0] < second_word[0]
        # Words should have the same y coordinate
        assert first_word[1] == second_word[1]

        # Using rtl layout, first x coordinate should be > HSTEP if line does not
        # span entire width
        assert first_word[0] > HSTEP
