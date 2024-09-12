This project is a Python implementation of the [Web Browser Engineering](http://browser.engineering) course. The program builds and launches a basic (and incomplete) web browser.

It can request web pages, parse HTML and some CSS, and supports multiple tabs. You can navigate by clicking links, but the browser cannot parse JavaScript or send information to a server.

### Install requirements

Ensure you have [rye](https://rye.astral.sh/) installed. Clone this repo, then run:

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
