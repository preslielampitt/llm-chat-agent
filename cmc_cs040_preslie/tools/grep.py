import glob
import re

def _is_safe_path(path):
    return not (
        path.startswith("/")
        or ".." in path.split("/")
    )


def grep(pattern, path):
    '''
    Search for lines matching a regex in files matched by a glob.

    >>> grep('hello', 'chat.py')
    ''
    >>> grep('def', 'tools/*.py') != ''
    True
    >>> grep('abc', '../secret.txt')
    'Invalid path'
    '''
    if not _is_safe_path(path):
        return 'Invalid path'

    try:
        result = []

        for filename in sorted(glob.glob(path)):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    for line in f:
                        if re.search(pattern, line):

                            result.append(line.rstrip('\n'))
            except FileNotFoundError:
                continue
            except UnicodeDecodeError:
                continue

        return '\n'.join(result)
    except re.error:
        return 'Invalid regex'


grep_tool_schema = {
    "type": "function",
    "function": {
        "name": "grep",
        "description": "Search for lines matching a regular expression in one or more files.",
        "parameters": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "The regular expression to search for.",
                },
                "path": {
                    "type": "string",
                    "description": "A relative file path or glob pattern to search.",
                },
            },
            "required": ["pattern", "path"],
        },
    },
}