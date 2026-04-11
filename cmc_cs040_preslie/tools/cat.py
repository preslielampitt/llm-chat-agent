def cat(filename):
    '''
    Opens a file and returns its contents as a string.

    >>> isinstance(cat('chat.py'), str)
    True
    >>> cat('this_file_does_not_exist.txt')
    'File not found'
    >>> cat('cmc_cs040_preslie/__pycache__/chat.cpython-314.pyc')
    'File is not a readable text file'
    >>> cat('.github/workflows')
    'Error reading file'
    '''
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return 'File not found'
    except UnicodeDecodeError:
        return 'File is not a readable text file'
    except Exception:
        return 'Error reading file'