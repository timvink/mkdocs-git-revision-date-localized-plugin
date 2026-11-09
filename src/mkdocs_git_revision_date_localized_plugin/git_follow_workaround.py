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

- oldest_followed_commit: one extra `git log`; returns the rename commit (too late).
- find_creation_past_renames: also continues past each rename under the old name and
  returns the real creation commit; two to three extra git calls per rename.
"""

import os
from pathlib import Path

from git import Git, GitCommandError

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


def find_creation_past_renames(git: Git, path: str, max_renames: int = 10) -> str:
    """
    Find the commit that created a file, continuing past renames where --follow stops.

    When the oldest commit `git log --follow` reaches renamed the file, search again from
    that commit's parent under the old name, first with the creation query and then with
    --follow, so renames further back are continued past as well.

    Args:
        git (Git): git command wrapper for the repository that contains path.
        path (str): Absolute path of the file.
        max_renames (int): Maximum number of renames to continue past.

    Returns:
        str: "<hash> <timestamp>" of the creation commit, or of the oldest commit found
            when the creation commit cannot be reached, or "" if git finds no commit.
    """
    toplevel = os.path.realpath(git.rev_parse(show_toplevel=True))
    rev = "HEAD"
    oldest = ""
    for _ in range(max_renames + 1):
        followed = git.log(rev, "--", path, **LOG_OPTIONS).strip()
        if not followed:
            break
        oldest = followed.split("\n")[-1]
        oldest_hash = oldest.split(" ")[0]

        old_path = _renamed_from(git, oldest_hash, Path(os.path.relpath(path, toplevel)).as_posix())
        if old_path is None:
            # The oldest commit did not rename the file, so it is the best answer git gives
            break
        path = os.path.join(toplevel, old_path)
        rev = f"{oldest_hash}^"
        created = git.log(rev, "--", path, diff_filter="Ar", **LOG_OPTIONS).strip()
        if created:
            return created.split("\n")[-1]
    return oldest


def _renamed_from(git: Git, commit: str, relative_path: str) -> str | None:
    """
    Get the path a file had before commit renamed (or copied) it.

    Args:
        git (Git): git command wrapper for the repository.
        commit (str): commit hash.
        relative_path (str): path of the file after commit, relative to the repository root.

    Returns:
        str | None: the old path relative to the repository root, or None when commit did
            not rename the file or has no parent.
    """
    try:
        # Compare with the first parent; -z gives NUL separated, unquoted paths
        changes = git.diff_tree("-r", "-M", "-z", "--name-status", f"{commit}^", commit).split("\0")
    except GitCommandError:
        # A root commit has no parent
        return None
    i = 0
    while i + 1 < len(changes):
        status = changes[i]
        if status[:1] in ("R", "C"):
            if i + 2 < len(changes) and changes[i + 2] == relative_path:
                return changes[i + 1]
            i += 3
        else:
            i += 2
    return None
