import glob
from cmc_cs040_preslie.tools.path_utils import is_path_safe


def ls(folder=None):
    '''
    This function behaves just like the ls program in the shell.

    >>> result = ls()
    >>> 'README.md' in result
    True
    >>> 'cmc_cs040_preslie' in result
    True
    >>> 'test_projects' in result
    True
    >>> ls('cmc_cs040_preslie/tools')
    'cmc_cs040_preslie/tools/__pycache__ cmc_cs040_preslie/tools/calculate.py cmc_cs040_preslie/tools/cat.py cmc_cs040_preslie/tools/grep.py cmc_cs040_preslie/tools/ls.py cmc_cs040_preslie/tools/path_utils.py '
    >>> ls('../')
    'Invalid path'
    '''
    if not is_path_safe(folder):
        return 'Invalid path'

    if folder is not None:
        result = ''
        # folder + '/*' ==> tools /*
        # glob is nondeterministic; no guarantees about order of glob results
        # need to convert nondeterministic to deterministic
        # llm we did that by adjusting the temperature
        # best way to make a list deterministic is to sort it
        for path in sorted(glob.glob(folder + '/*')):
            result += path + ' '
        return result
    else:
        result = ''
        for path in sorted(glob.glob('*')):
            result += path + ' '
        return result.strip()


ls_tool_schema = {
    "type": "function",
    "function": {
        "name": "ls",
        "description": "List files in a directory",
        "parameters": {
            "type": "object",
            "properties": {
                "folder": {
                    "type": "string",
                    "description": "The folder to list. If omitted, list the current directory."
                }
            },
            "required": [],
        },
    },
}
