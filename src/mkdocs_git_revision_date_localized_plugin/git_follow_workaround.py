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
when the creation query returns nothing, so other pages pay no extra cost: three to four
git calls per rename continued past.
"""

import os

from git import Git, GitCommandError

# Names from history must not be read as glob patterns (f.e. "old[1].md")
LITERAL_PATHSPECS = {"GIT_LITERAL_PATHSPECS": "1"}


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
    for _ in range(max_renames):
        followed = _follow(git, rev, path)
        if not followed:
            break
        oldest, name_at_oldest = followed[-1]
        oldest_hash = oldest.split(" ")[0]

        # --follow can cross newer renames before it stops, so compare with the name the
        # file had in the oldest commit, not with path
        old_name = _renamed_from(git, oldest_hash, name_at_oldest)
        if old_name is None:
            # The oldest commit did not rename the file, so it is the best answer git gives
            break
        path = os.path.join(toplevel, old_name)
        rev = f"{oldest_hash}^"
        created = git.log(
            rev,
            "--",
            path,
            diff_filter="Ar",
            follow=True,
            date="unix",
            format="%H %at",
            no_show_signature=True,
            env=LITERAL_PATHSPECS,
        ).strip()
        if created:
            return created.split("\n")[-1]
    return oldest


def _follow(git: Git, rev: str, path: str) -> list[tuple[str, str]]:
    """
    Get the commits `git log --follow` reaches from rev, newest first.

    Returns:
        list[tuple[str, str]]: ("<hash> <timestamp>", file name relative to the repository
            root in that commit) per commit.
    """
    # With -z and --name-only, each commit is "<format>\0\n<name>\0". \x01 marks the
    # format, so a merge commit without a name cannot shift the pairing.
    out = git.log(
        rev,
        "--",
        path,
        follow=True,
        name_only=True,
        z=True,
        date="unix",
        format="%x01%H %at",
        no_show_signature=True,
        env=LITERAL_PATHSPECS,
    )
    commits = []
    for token in out.split("\0"):
        token = token.lstrip("\n")
        if token.startswith("\x01"):
            commits.append([token[1:], ""])
        elif token and commits and not commits[-1][1]:
            commits[-1][1] = token
    return [(commit, name) for commit, name in commits]


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
