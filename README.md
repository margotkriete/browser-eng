This project is a Python implementation of the [Web Browser Engineering](http://browser.engineering) course. The program builds and launches a basic (and incomplete) web browser.

### Install requirements

Clone this repo, then run:

```
$ rye init
```

### Run browser

To request a URL:

```
$ rye run python src/browser.py <URL>
```

To request a file:

```
$ rye run python src/browser.py <FILENAME>
```

To view a URL's source code:

```
$ rye run python src/browser.py view-source:<URL>
```

### Run tests

Test cases are in the `tests` directory. To run all tests:

```
$ rye test
```
