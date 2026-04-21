import os

from cmc_cs040_preslie.tools.doctests import doctests
from cmc_cs040_preslie.tools.git_utils import commit_paths
from cmc_cs040_preslie.tools.path_utils import is_path_safe


def write_files(files, commit_message):
    '''
    Write several UTF-8 files, commit them, and run doctests on any Python files.

    >>> write_files([{'path': '/etc/passwd', 'contents': 'x'}], 'bad write')
    'Invalid path'
    '''
    paths = []
    python_paths = []

    for file_info in files:
        path = file_info.get('path')
        contents = file_info.get('contents', '')

        if not is_path_safe(path):
            return 'Invalid path'

        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as handle:
            handle.write(contents)

        paths.append(path)
        if path.endswith('.py'):
            python_paths.append(path)

    commit_paths(paths, f'[docchat] {commit_message}')

    outputs = [f'Wrote {len(paths)} file(s).']
    for path in python_paths:
        outputs.append(f'Doctests for {path}:')
        outputs.append(doctests(path))
    return '\n'.join(outputs)


write_files_tool_schema = {
    "type": "function",
    "function": {
        "name": "write_files",
        "description": "Write multiple UTF-8 files, commit them with a docchat commit message, and run doctests on Python files.",
        "parameters": {
            "type": "object",
            "properties": {
                "files": {
                    "type": "array",
                    "description": "A list of file dictionaries with path and contents keys."
                },
                "commit_message": {
                    "type": "string",
                    "description": "The commit message suffix to use after the [docchat] prefix."
                }
            },
            "required": ["files", "commit_message"],
        },
    },
}
