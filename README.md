```markdown
# Project Chat Agent

Project Chat Agent is a command-line assistant that answers questions about files in the current repository and can use built-in tools such as `ls`, `cat`, `grep`, and `calculate`. It supports both automatic tool use through the language model and manual slash commands for fast, deterministic access to repository information.

![doctest](https://github.com/preslielampitt/llm-lab/actions/workflows/doctests.yml/badge.svg)
![integration-test](https://github.com/preslielampitt/llm-lab/actions/workflows/integration-tests.yml/badge.svg)
![Flake8](https://github.com/preslielampitt/llm-lab/actions/workflows/flake8.yml/badge.svg)
![PyPI](https://img.shields.io/pypi/v/cmc-cs040-preslie)
![Coverage](https://img.shields.io/badge/coverage-90%25-green)

## Demo

Animated terminal demo coming soon.

## Installation

```bash
pip install cmc-cs040-preslie
```

## Usage

```bash
chat
```

Once running, type your messages and press Enter. Use `Ctrl+C` to exit.

You can ask normal questions, or run manual slash commands such as `/ls`, `/cat`, `/grep`, and `/calculate`.

## Example: Webpage Project

This example shows how the tool can inspect a web project and answer a question based on repository contents.

```text
$ cd test_projects/webpage
$ chat
chat> tell me what files are in this project
This project contains HTML, CSS, and related assets for a webpage.
chat> does this project have a stylesheet?
Yes, the project includes a CSS file for styling the page.
```

## Example: Markdown Compiler

This example shows how the tool can inspect source code and summarize implementation details.

```text
$ cd test_projects/markdown-compiler
$ chat
chat> does this project use regular expressions?
I searched the source files and found whether the `re` module is used in the project.
chat> what does this project do?
This project converts markdown input into another output format based on its compiler logic.
```

## Example: Ebay Scraper

This example shows how the tool can read project files and answer higher-level questions about the repository.

```text
$ cd test_projects/ebay-scraper
$ chat
chat> tell me about this project
This project is designed to collect product information from eBay pages.
chat> what libraries does it use?
I checked the code and identified the main libraries imported by the scraper.
```

## Features

- Conversational repository assistant powered by Groq
- Automatic tool calling for `calculate`, `ls`, `cat`, and `grep`
- Manual slash commands for direct tool execution
- Path safety checks to block absolute paths and directory traversal
- Doctest-based validation and integration testing

## PyPI

PyPI page: [https://pypi.org/project/cmc-cs040-preslie/](https://pypi.org/project/cmc-cs040-preslie/)
