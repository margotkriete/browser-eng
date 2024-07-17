This project is a Python implementation of the [Web Browser Engineering](http://browser.engineering) course. The program builds a basic, and currently very incomplete, web browser.

### Requirements

- TODO: add `requirements.txt` file
- Python 3.10+

### Run browser

To request a URL:

```
$ python3 browser.py <URL>
```

To request a file:

```
$ python3 browser.py <FILENAME>
```

### Run tests

Ensure you have `pytest` installed.

To run all tests:

```
$ python3 -m pytest
```

Add `test_browser.py`, `test_url.py`, or `test_layout.py` to run individual test files.

```
$ python3 -m pytest test_browser.py
```
