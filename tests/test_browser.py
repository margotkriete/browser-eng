import pytest
import tkinter

import test_utils
from browser import Browser
from constants import HEIGHT, HSTEP, WIDTH
from test_utils import socket
from url import URL

MOCK_URL = "http://test.test/example1"
LOREM_IPSUM = b" Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas tellus metus, luctus id quam at, ornare posuere sapien. Morbi sit amet sollicitudin nunc. Donec luctus nibh ultricies lacus luctus, eget porta orci facilisis. Sed placerat et mauris dignissim porta. Donec sagittis enim dolor, eget dapibus augue semper vel. Proin pellentesque, arcu a tincidunt eleifend, nulla libero porta risus, eget euismod ante quam eget erat. Phasellus hendrerit tortor condimentum ante rhoncus bibendum. Donec vehicula eleifend libero ac vulputate. Sed elementum, sem eu convallis dictum, risus libero blandit purus, sed convallis justo orci non est. Sed efficitur malesuada neque, pulvinar feugiat nulla suscipit vel. Donec augue leo, gravida non feugiat in, gravida a ipsum. Cras dictum purus mauris, id sodales nulla varius a. Phasellus lobortis volutpat volutpat. Phasellus cursus quam quis odio feugiat, a consequat ipsum pharetra. \nMauris in nisi et libero sodales elementum id in ante. Morbi vel blandit risus. Curabitur at lacinia nunc. Suspendisse arcu nulla, elementum id egestas eget, commodo laoreet massa. Aenean tristique, lacus in porta placerat, odio purus consectetur lectus, sed vestibulum ligula augue a est. Aenean varius ante quis bibendum semper. Morbi elit arcu, condimentum id bibendum ac, congue nec risus. Fusce semper erat sed viverra congue. Aenean volutpat risus non elit aliquet hendrerit."
MOCK_BODY_TEXT = b"Body text"


@pytest.fixture
def mock_socket():
    def _mock_socket(url=MOCK_URL, rtl=False, response_body_text=MOCK_BODY_TEXT):
        socket.patch().start()
        socket.respond(url, mock_http_response(response_body_text))
        browser = Browser(rtl=rtl)
        browser.load(URL(url))
        return browser

    return _mock_socket


def mock_http_response(text):
    return b"HTTP/1.0 200 OK\r\n" + b"Header1: Value1\r\n\r\n" + text


class TestBrowser:
    def test_browser_load_display_list(self, mock_socket):
        browser = mock_socket()
        assert len(browser.display_list) == 2
        first_word = browser.display_list[0]
        second_word = browser.display_list[1]
        assert first_word.text == "Body"
        assert second_word.text == "text"

        # "Body" should have a smaller x coordinate than "text"
        # First word should begin at HSTEP
        assert first_word.x < second_word.x
        assert first_word.x == HSTEP

        # Words should have the same y coordinate
        assert first_word.y == second_word.y

    def test_browser_load_rtl(self, mock_socket):
        browser = mock_socket(rtl=True)
        assert len(browser.display_list) == 2
        first_word = browser.display_list[0]
        second_word = browser.display_list[1]
        assert first_word.text == "Body"
        assert second_word.text == "text"

        # "Body" should have a smaller x coordinate than "text"
        assert first_word.x < second_word.x
        # Words should have the same y coordinate
        assert first_word.y == second_word.y

        # Using rtl layout, first x coordinate should be > HSTEP if line does not
        # span entire width
        assert first_word.x > HSTEP

    def test_browser_resize_width(self, mock_socket):
        browser = mock_socket(response_body_text=LOREM_IPSUM)
        assert browser.screen_width == WIDTH

        e = tkinter.Event()
        e.height = 400
        e.width = 600
        browser.resize(e)

        assert browser.screen_width == e.width

        # All x coordinates should be > HSTEP and < screen width
        assert all(item.x < browser.screen_width for item in browser.display_list)
        assert all(item.x >= HSTEP for item in browser.display_list)

    def test_browser_resize_height(self, mock_socket):
        browser = mock_socket(response_body_text=LOREM_IPSUM)
        assert browser.screen_height == HEIGHT
        previous_doc_height = browser.display_list[-1].y
        e = tkinter.Event()
        e.height = 400
        e.width = 600
        browser.resize(e)

        assert browser.screen_height == e.height
        # display_list coordinates should have shifted with resize
        # display_list[-1][1] is the last y coordinate of the document
        assert browser.display_list[-1].y != previous_doc_height

    def test_browser_scrollbar_align_after_resize(self, mock_socket):
        browser = mock_socket(response_body_text=LOREM_IPSUM)
        e = tkinter.Event()
        e.height = 400
        e.width = 1200
        browser.resize(e)
        coordinates = browser.get_scrollbar_coordinates()
        assert coordinates.x0 == 1180
        assert coordinates.y0 == 0
        assert coordinates.x1 == 1200
        assert coordinates.y1 == 652
