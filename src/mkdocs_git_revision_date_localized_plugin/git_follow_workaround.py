"""
Workaround for `git log --follow` stopping at a rename (git >= 2.56.0).

Since git commit 304812ed33 ("log: improve --follow following renames for non-linear
history", released in git 2.56.0), `git log --follow` can stop at a rename without
reaching the commit that created the file. This happens when the parent of the rename
commit also has an older child on a side branch, and that branch is merged after the
file has changed too much to match its old name. The creation query
(`git log --follow --diff-filter=Ar`) then returns nothing, and the plugin would fall
back to the build time, which is later than the last revision date.

See https://github.com/timvink/mkdocs-git-revision-date-localized-plugin/issues/241

The `mv/log-follow-speedup` series in git restores the full history. Once a git release
with that fix is widely used, this module can be removed. The functions here only run
when the creation query returns nothing, so other pages pay no extra cost.
"""

from git import Git

LOG_OPTIONS = {"date": "unix", "format": "%H %at", "no_show_signature": True, "follow": True}


def oldest_followed_commit(git: Git, path: str) -> str:
    """
    Get the oldest commit that `git log --follow` reaches for a file.

    When --follow stops at a rename, that is the rename commit: later than the real
    creation, but never later than the last revision.

    Args:
        git (Git): git command wrapper for the repository that contains path.
        path (str): Absolute path of the file.

    Returns:
        str: "<hash> <timestamp>" of the oldest followed commit, or "" if git finds no commit.
    """
    lines = git.log("--", path, **LOG_OPTIONS).strip()
    return lines.split("\n")[-1] if lines else ""
