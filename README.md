This project is a Python implementation of the [Web Browser Engineering](http://browser.engineering) course. The program builds and launches a basic, and currently very incomplete, web browser.

### Install requirements

```
$ pyenv python3 -m pip install requirements.txt
```

### Run browser

To request a URL:

```
$ python3 src/browser.py <URL>
```

To request a file:

```
$ python3 src/browser.py <FILENAME>
```

To view a URL's source code:

```
$ python3 src/browser.py view-source:<URL>
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
