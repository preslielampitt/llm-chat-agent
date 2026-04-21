import os


def get_repo():
    '''
    Return the git repository rooted at the current working directory.
    '''
    from git import Repo

    return Repo(os.getcwd())


def commit_paths(paths, commit_message):
    '''
    Stage the given paths and create a git commit if there are staged changes.
    '''
    repo = get_repo()
    repo.git.add(*paths)
    if repo.git.diff('--cached', '--name-only'):
        repo.index.commit(commit_message)


def commit_removed_paths(paths, commit_message):
    '''
    Stage removals for the given paths and create a git commit if there are staged changes.
    '''
    repo = get_repo()
    repo.index.remove(paths, working_tree=True)
    if repo.git.diff('--cached', '--name-only'):
        repo.index.commit(commit_message)
