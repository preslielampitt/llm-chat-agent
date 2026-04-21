# AGENTS.md

This repository contains a command-line chat assistant for exploring and modifying repositories with LLM-guided tools.

When working in this project:
- Prefer reading `README.md` first when asked what the project does.
- Use the built-in tools when they help answer repository questions: `ls`, `cat`, `grep`, `calculate`, `compact`, `doctests`, `write_file`, `write_files`, and `rm`.
- Never use absolute paths or paths containing `..`.
- Treat file edits carefully and prefer the smallest change that solves the problem.
- When writing files, use clear commit messages and keep changes easy to review.
- Prefer short, direct answers unless the user asks for more detail.
- If repository instructions are already available in the chat history, use that context instead of re-reading files unnecessarily.
