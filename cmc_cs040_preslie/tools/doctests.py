import subprocess
import sys

from cmc_cs040_preslie.tools.path_utils import is_path_safe


def doctests(path):
    '''
    Run doctests with verbose output for a safe relative path.

    >>> doctests('/etc/passwd')
    'Invalid path'
    '''
    if not is_path_safe(path):
        return 'Invalid path'

    result = subprocess.run(
        [sys.executable, '-m', 'pytest', path, '--doctest-modules', '-v'],
        capture_output=True,
        text=True,
        encoding='utf-8',
    )
    return result.stdout + result.stderr


doctests_tool_schema = {
    "type": "function",
    "function": {
        "name": "doctests",
        "description": "Run verbose doctests for a safe relative file or directory path and return the output.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The safe relative path whose doctests should be run."
                }
            },
            "required": ["path"],
        },
    },
}
