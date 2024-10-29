This project is a Python implementation of the [Web Browser Engineering](http://browser.engineering) course. The program builds and launches a basic (and incomplete) web browser from scratch in Python, using `tkinter` to build the GUI.

It can request web pages, parse HTML and some CSS, and supports multiple tabs. You can navigate by clicking links, but the browser cannot yet parse JavaScript or send information to a server.

![Preview image](preview-image.png)

## Installation

Ensure you have [rye](https://rye.astral.sh/) installed. Clone this repo, then run:

```
$ rye init
```

## Usage

You can run the browser by running the following commands from the root directory.

To launch the browser with `URL` as the homepage:

```
$ rye run python src/browser.py <URL>
```

To launch the browser and display a HTML file:

```
$ rye run python src/browser.py <FILENAME>
```

To launch the browser and display the source code of `URL`:

```
$ rye run python src/browser.py view-source:<URL>
```

### Run tests

Test cases are in the `tests` directory. To run all tests:

```
$ rye test
```

## Architecture

The browser uses `tkinter` as the GUI; its main loop is initiated in `browser.py`.

### Classes

Classes are mostly found in respective `<classname>.py` files.

| Class                     | Description                                                                                                                                                  |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `Chrome`                  | Paints the browser chrome, which includes tab rectangles, new tab buttons, and the address bar.                                                              |
| `Browser`                 | Runs the `tkinter` event loop, which launches and runs the web browser. Delegates click and input events to the active tab. Handles browser window resizing. |
| `Tab`                     | Handles navigation and rendering of the current tab. Much rendering logic is in `load()` method in `tab.py`.                                                 |
| `URL`                     | Parses URL strings, connects to URL host using `socket`/`ssl` libraries, sends HTTP requests, and reads HTTP responses.                                      |
| `LineLayout`/`TextLayout` | Handles layout (coordinates, nodes) for lines and text. `LineLayout` contains `TextLayout` children.                                                         |
| `InputLayout`             | Handles layout for input elements.                                                                                                                           |
| `BlockLayout`             | Handles layout for block layout items. These can hold text elements (e.g. `<b>` nodes) or block elements (e.g.`<p>` nodes).                                  |
| `DocumentLayout`          | Holds a collection of `BlockLayout` objects. A tab has exactly one `DocumentLayout` object.                                                                  |
| `HTMLParser`              | Lexes HTML text into strings, and parses those strings into a tree of elements and text nodes.                                                               |
| `CSSParser`               | Parses CSS stylesheets and applies default styling to the browser.                                                                                           |
| `Draw`                    | Handles drawing of Tkinter rectangles and text.                                                                                                              |
