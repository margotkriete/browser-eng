from url import URL


class TestURL:
    # def __init__(self, monkeypatch):
    # def mockreturn():
    #     return

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
