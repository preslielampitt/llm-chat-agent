def is_path_safe(path):
    '''
    Return True if a path stays within the current directory and does not use an absolute path or `..`.

    >>> is_path_safe(None)
    True
    >>> is_path_safe('chat.py')
    True
    >>> is_path_safe('tools/cat.py')
    True
    >>> is_path_safe('/etc/passwd')
    False
    >>> is_path_safe('../secret.txt')
    False
    >>> is_path_safe('tools/../secret.txt')
    False
    '''
    if path is None:
        return True
    return not path.startswith('/') and '..' not in path.split('/')
