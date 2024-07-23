This project is a Python implementation of the [Web Browser Engineering](http://browser.engineering) course. The program builds and launches a basic, and currently very incomplete, web browser.

### Requirements

- TODO: add `requirements.txt` file
- Python 3.10+
- `pytest`

### Run browser

To request a URL:

```
$ python3 browser.py <URL>
```

To request a file:

```
$ python3 browser.py <FILENAME>
```

To view a URL's source code:

```
$ python3 browser.py view-source:<URL>
```

### Run tests

Ensure you have `pytest` installed.

To run all tests:

```
$ python3 -m pytest
```

Test cases are in the `tests` directory. Specify these files to run individual test cases.

```
$ python3 -m pytest tests/test_browser.py
```
