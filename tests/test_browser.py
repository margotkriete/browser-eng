import tkinter

import pytest

from browser import Browser
from constants import HEIGHT, HSTEP, WIDTH
from test_utils import socket
from url import URL

MOCK_URL = "http://test.test/example1"
LOREM_IPSUM = b" Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas tellus metus, luctus id quam at, ornare posuere sapien. Morbi sit amet sollicitudin nunc. Donec luctus nibh ultricies lacus luctus, eget porta orci facilisis. Sed placerat et mauris dignissim porta. Donec sagittis enim dolor, eget dapibus augue semper vel. Proin pellentesque, arcu a tincidunt eleifend, nulla libero porta risus, eget euismod ante quam eget erat. Phasellus hendrerit tortor condimentum ante rhoncus bibendum. Donec vehicula eleifend libero ac vulputate. Sed elementum, sem eu convallis dictum, risus libero blandit purus, sed convallis justo orci non est. Sed efficitur malesuada neque, pulvinar feugiat nulla suscipit vel. Donec augue leo, gravida non feugiat in, gravida a ipsum. Cras dictum purus mauris, id sodales nulla varius a. Phasellus lobortis volutpat volutpat. Phasellus cursus quam quis odio feugiat, a consequat ipsum pharetra. \nMauris in nisi et libero sodales elementum id in ante. Morbi vel blandit risus. Curabitur at lacinia nunc. Suspendisse arcu nulla, elementum id egestas eget, commodo laoreet massa. Aenean tristique, lacus in porta placerat, odio purus consectetur lectus, sed vestibulum ligula augue a est. Aenean varius ante quis bibendum semper. Morbi elit arcu, condimentum id bibendum ac, congue nec risus. Fusce semper erat sed viverra congue. Aenean volutpat risus non elit aliquet hendrerit."
MOCK_BODY_TEXT = b"Body text"


@pytest.fixture
def mock_socket():
    def _mock_socket(url=MOCK_URL, response_body_text=MOCK_BODY_TEXT):
        socket.patch().start()
        socket.respond(url, mock_http_response(response_body_text))
        browser = Browser()
        browser.new_tab(URL(url))
        return browser

    return _mock_socket


def mock_http_response(text):
    return b"HTTP/1.0 200 OK\r\n" + b"Header1: Value1\r\n\r\n" + text


class TestBrowser:
    @pytest.mark.skip
    def test_browser_loads_display_list(self, mock_socket):
        browser = mock_socket()
        assert len(browser.active_tab.display_list) == 2
        first_word = browser.active_tab.display_list[0]
        second_word = browser.active_tab.display_list[1]
        assert first_word.text == "Body"
        assert second_word.text == "text"

        # "Body" should have a smaller x coordinate than "text"
        # First word should begin at HSTEP
        assert first_word.rect.left < second_word.rect.left
        assert first_word.rect.left == HSTEP

        # Words should have the same y coordinate
        assert first_word.rect.top == second_word.rect.top

    @pytest.mark.skip
    def test_browser_resizes_width(self, mock_socket):
        browser = mock_socket(response_body_text=LOREM_IPSUM)
        assert browser.screen_width == WIDTH

        e = tkinter.Event()
        e.char = None
        e.state = None
        e.height = 400
        e.width = 600
        browser.handle_resize(e)
        assert browser.screen_width == e.width

        # All x coordinates should be > HSTEP and < screen width
        assert all(item.left < browser.screen_width for item in browser.display_list)
        assert all(item.left >= HSTEP for item in browser.display_list)

    @pytest.mark.skip
    def test_browser_resizes_height(self, mock_socket):
        browser = mock_socket(response_body_text=LOREM_IPSUM)
        assert browser.screen_height == HEIGHT
        previous_doc_height = browser.display_list[-1].bottom
        e = tkinter.Event()
        e.height = 400
        e.width = 600
        browser.handle_resize(e)

        assert browser.screen_height == e.height
        # display_list coordinates should have shifted with resize
        # display_list[-1][1] is the last y coordinate of the document
        assert browser.display_list[-1].bottom != previous_doc_height

    @pytest.mark.skip
    def test_browser_scrollbar_aligns_after_resize(self, mock_socket):
        browser = mock_socket(response_body_text=LOREM_IPSUM)
        e = tkinter.Event()
        e.height = 400
        e.width = 1200
        browser.resize(e)
        coordinates = browser.get_scrollbar_coordinates()
        assert coordinates.x0 == 1180
        assert coordinates.y0 == 0
        assert coordinates.x1 == 1200
        assert coordinates.y1 == 621

    @pytest.mark.skip
    def test_browser_view_source_renders_tags(self):
        socket.patch().start()
        socket.respond(
            "http://example.org/", mock_http_response(b"<html><body></body></html>")
        )
        browser = Browser()
        browser.load(URL("view-source:http://example.org"))
        assert len(browser.display_list) == 4
        assert browser.display_list[0].text == "<html>"
        assert browser.display_list[1].text == "<body>"
        assert browser.display_list[2].text == "</body>"
        assert browser.display_list[3].text == "</html>"

    @pytest.mark.skip
    def test_browser_without_view_source_does_not_render_tag(self, mock_socket):
        browser = mock_socket(response_body_text=b"<html><body></body></html>")
        assert len(browser.display_list) == 0
