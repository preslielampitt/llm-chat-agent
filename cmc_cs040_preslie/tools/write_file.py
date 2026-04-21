from cmc_cs040_preslie.tools.write_files import write_files


def write_file(path, contents, commit_message):
    '''
    Write one UTF-8 file and commit it.

    >>> write_file('/etc/passwd', 'x', 'bad write')
    'Invalid path'
    '''
    return write_files(
        [{'path': path, 'contents': contents}],
        commit_message,
    )


write_file_tool_schema = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": "Write one UTF-8 file, commit it with a docchat commit message, and run doctests if it is a Python file.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The safe relative path to write."
                },
                "contents": {
                    "type": "string",
                    "description": "The UTF-8 contents to write to the file."
                },
                "commit_message": {
                    "type": "string",
                    "description": "The commit message suffix to use after the [docchat] prefix."
                }
            },
            "required": ["path", "contents", "commit_message"],
        },
    },
}
