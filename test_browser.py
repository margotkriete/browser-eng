import tkinter

import test_utils
from browser import Browser
from constants import HEIGHT, HSTEP, WIDTH
from test_utils import socket
from url import URL

LOREM_IPSUM = b" Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas tellus metus, luctus id quam at, ornare posuere sapien. Morbi sit amet sollicitudin nunc. Donec luctus nibh ultricies lacus luctus, eget porta orci facilisis. Sed placerat et mauris dignissim porta. Donec sagittis enim dolor, eget dapibus augue semper vel. Proin pellentesque, arcu a tincidunt eleifend, nulla libero porta risus, eget euismod ante quam eget erat. Phasellus hendrerit tortor condimentum ante rhoncus bibendum. Donec vehicula eleifend libero ac vulputate. Sed elementum, sem eu convallis dictum, risus libero blandit purus, sed convallis justo orci non est. Sed efficitur malesuada neque, pulvinar feugiat nulla suscipit vel. Donec augue leo, gravida non feugiat in, gravida a ipsum. Cras dictum purus mauris, id sodales nulla varius a. Phasellus lobortis volutpat volutpat. Phasellus cursus quam quis odio feugiat, a consequat ipsum pharetra. \nMauris in nisi et libero sodales elementum id in ante. Morbi vel blandit risus. Curabitur at lacinia nunc. Suspendisse arcu nulla, elementum id egestas eget, commodo laoreet massa. Aenean tristique, lacus in porta placerat, odio purus consectetur lectus, sed vestibulum ligula augue a est. Aenean varius ante quis bibendum semper. Morbi elit arcu, condimentum id bibendum ac, congue nec risus. Fusce semper erat sed viverra congue. Aenean volutpat risus non elit aliquet hendrerit."


class TestBrowser:
    def mock_url(self, url="http://test.test/example1"):
        return url

    def mock_response(self, text=b"Body text"):
        return b"HTTP/1.0 200 OK\r\n" + b"Header1: Value1\r\n\r\n" + text

    def test_browser_load_display_list(self):
        _ = socket.patch().start()
        socket.respond(self.mock_url(), self.mock_response())
        browser = Browser()
        browser.load(URL(self.mock_url()))

        assert len(browser.display_list) == 2
        first_word = browser.display_list[0]
        second_word = browser.display_list[1]
        assert first_word[2] == "Body"
        assert second_word[2] == "text"

        # "Body" should have a smaller x coordinate than "text"
        # First word should begin at HSTEP
        assert first_word[0] < second_word[0]
        assert first_word[0] == HSTEP

        # Words should have the same y coordinate
        assert first_word[1] == second_word[1]

    def test_browser_load_rtl(self):
        _ = socket.patch().start()
        socket.respond(self.mock_url(), self.mock_response())
        browser = Browser(rtl=True)
        browser.load(URL(self.mock_url()))

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

    def test_browser_resize_width(self):
        _ = socket.patch().start()
        socket.respond(self.mock_url(), self.mock_response(LOREM_IPSUM))
        browser = Browser()
        browser.load(URL(self.mock_url()))

        assert browser.screen_width == WIDTH

        e = tkinter.Event()
        e.height = 400
        e.width = 600
        browser.resize(e)

        assert browser.screen_width == e.width

        # All x coordinates should be > HSTEP and < screen width
        assert all(item[0] < browser.screen_width for item in browser.display_list)
        assert all(item[0] >= HSTEP for item in browser.display_list)

    def test_browser_resize_height(self):
        _ = socket.patch().start()
        socket.respond(self.mock_url(), self.mock_response(LOREM_IPSUM))
        browser = Browser()
        browser.load(URL(self.mock_url()))

        assert browser.screen_height == HEIGHT
        previous_doc_height = browser.display_list[-1][1]
        e = tkinter.Event()
        e.height = 400
        e.width = 600
        browser.resize(e)

        assert browser.screen_height == e.height
        # display_list coordinates should have shifted with resize
        # display_list[-1][1] is the last y coordinate of the document
        assert browser.display_list[-1][1] != previous_doc_height

    def test_browser_scrollbar_align_after_resize(self):
        _ = socket.patch().start()
        socket.respond(self.mock_url(), self.mock_response(LOREM_IPSUM))
        browser = Browser()
        browser.load(URL(self.mock_url()))
        e = tkinter.Event()
        e.height = 400
        e.width = 1200
        browser.resize(e)
        coordinates = browser.get_scrollbar_coordinates()
        assert coordinates.x0 == 1180
        assert coordinates.y0 == 0
        assert coordinates.x1 == 1200
        assert coordinates.y1 == 652
