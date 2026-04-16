# Project Chat Agent

![doctest](https://github.com/preslielampitt/llm-lab/actions/workflows/doctests.yml/badge.svg)
![integration-test](https://github.com/preslielampitt/llm-lab/actions/workflows/integration-tests.yml/badge.svg)
![Flake8](https://github.com/preslielampitt/llm-lab/actions/workflows/flake8.yml/badge.svg)
![PyPI](https://img.shields.io/pypi/v/cmc-cs040-preslie)
<!-- The Coverage badge needs to use coverage.io; the pypi badge should be a link to pypi (or include a link at the top, not at the bottom) -->

Project Chat Agent is a command-line assistant that answers questions about files in the current repository and can use built-in tools such as `ls`, `cat`, `grep`, and `calculate`. It supports both automatic tool use through the language model and manual slash commands for fast, deterministic access to repository information.

![Demo](assets/demo.gif)

<!-- never provide install instructions from pypi;
anyone using github knows how to pip install -->


<!-- all of the "usage" info you included above is reasonable,
but it is better to put it in the context of an example -->
## Example Usage

This example shows how the tool can inspect a web project and answer a question based on repository contents.

```bash
$ cd test_projects/preslielampitt.github.io
$ chat
chat> tell me what files are in this project
This project contains HTML, CSS, and related assets for a webpage.
chat> does this project have a stylesheet?
Yes, the project includes a CSS file for styling the page.
```

This example shows how the tool can inspect source code and summarize implementation details.

```text
$ cd test_projects/markdown-compiler
$ chat
chat> does this project use regular expressions?
I searched the source files and found whether the `re` module is used in the project.
chat> what does this project do?
This project converts markdown input into another output format based on its compiler logic.
```

This example shows how the tool can read project files and answer higher-level questions about the repository.

```text
$ cd test_projects/ebay-webscraper
$ chat
chat> tell me about this project
This project is designed to collect product information from eBay pages.
chat> what libraries does it use?
I checked the code and identified the main libraries imported by the scraper.
```

<!-- the features you listed all read like AI slop;
you want to avoid giving that impression in your technical writing
the way to make it not sound like slop is weave the features into the examples
-->
