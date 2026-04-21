# Project Chat Agent

![doctest](https://github.com/preslielampitt/llm-lab/actions/workflows/doctests.yml/badge.svg)
![integration-test](https://github.com/preslielampitt/llm-lab/actions/workflows/integration-tests.yml/badge.svg)
![Flake8](https://github.com/preslielampitt/llm-lab/actions/workflows/flake8.yml/badge.svg)
[![codecov](https://codecov.io/github/preslielampitt/llm-chat-agent/graph/badge.svg?token=0P1LX0SLH1)](https://codecov.io/github/preslielampitt/llm-chat-agent)
[![PyPI](https://img.shields.io/pypi/v/cmc-cs040-preslie)](https://pypi.org/project/cmc-cs040-preslie/)

Project Chat Agent is a command-line assistant that answers questions about files in the current repository and can use built-in tools such as `ls`, `cat`, `grep`, and `calculate`. It supports both automatic tool use through the language model and manual slash commands for fast, deterministic access to repository information.

![Demo](assets/demo.gif)

## Usage

```bash
docsum-chat
```

Once running, type your messages and press Enter. Use `Ctrl+C` to exit.

For example, you can ask the assistant to explain a project, list files, or inspect source code, and it will use Groq together with built-in tools to answer based on the repository you are currently in. If you want more control, you can run tools yourself with slash commands such as /ls, /cat, /grep, /calculate, and /compact.

You can also use the program outside the interactive chat for quick one-line questions, turn on --debug to see tool calls while they happen, and use Tab to complete slash commands or file paths as you type. For example, /ls .g can complete to /ls .github, and /compact can shorten the current chat history so later responses are faster and more focused.

### Quick Examples

How to ask a one-line question without entering the interactive chat:
```bash
$ chat "what is this project about?"
```

How to use --debug to print tool calls while the assistant works:
```bash
$ chat --debug "what files are in the .github folder?"
```

How to use /ls to list files in a folder and then give the assistant context for a follow-up question:
```bash
$ chat
chat> /ls .github
.github/workflows
chat> what files are in the .github folder?
The `.github` folder contains the `workflows` subdirectory.
```

How to use /cat to load a file into the conversation so the assistant can answer questions about it:
```bash
$ chat
chat> /cat README.md
chat> what does this project do?
This project is a command-line assistant for exploring repositories with tool support.
```

How to use /calculate to evaluate a mathematical expression directly in the chat:
```bash
$ chat
chat> /calculate 2+2
4
```

How to use /grep to search files for matching text or patterns:
```bash
$ chat
chat> /grep def cmc_cs040_preslie/tools/*.py
```

This example shows how /compact can summarize the current chat history to keep the conversation shorter and more efficient:
```bash
$ chat
chat> /compact
```

## Example: Webpage Project

This example shows how the tool can inspect a web project and answer a question based on repository contents:
```bash
$ cd test_projects/preslielampitt.github.io
$ chat
chat> tell me what files are in this project
This project contains HTML, CSS, and related assets for a webpage.
chat> does this project have a stylesheet?
Yes, the project includes a CSS file for styling the page.
```

This example shows how the tool can inspect source code and summarize implementation details:
```bash
$ cd test_projects/markdown-compiler
$ chat
chat> does this project use regular expressions?
I searched the source files and found whether the `re` module is used in the project.
chat> what does this project do?
This project converts markdown input into another output format based on its compiler logic.
```

This example shows how the tool can read project files and answer higher-level questions about the repository:
```bash
$ cd test_projects/ebay-webscraper
$ chat
chat> tell me about this project
This project is designed to collect product information from eBay pages.
chat> what libraries does it use?
I checked the code and identified the main libraries imported by the scraper.
```
