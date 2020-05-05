# standard library
import logging
import os
import time
from datetime import datetime

# 3rd party
from babel.dates import format_date
from git import Git, GitCommandError, GitCommandNotFound


class Util:
    def __init__(self, path: str = "./docs"):
        self.repo = Git(path)

        # Checks when running builds on CI
        # See https://github.com/timvink/mkdocs-git-revision-date-localized-plugin/issues/10
        if is_shallow_clone(self.repo):
            n_commits = commit_count(self.repo)

            if os.environ.get("GITLAB_CI") and n_commits < 50:
                # Default is GIT_DEPTH of 50 for gitlab
                logging.warning(
                    """
                       Running on a gitlab runner might lead to wrong git revision dates
                       due to a shallow git fetch depth.
                       Make sure to set GIT_DEPTH to 1000 in your .gitlab-ci.yml file.
                       (see https://docs.gitlab.com/ee/user/project/pipelines/settings.html#git-shallow-clone).
                       """
                )
            if os.environ.get("GITHUB_ACTIONS") and n_commits == 1:
                # Default is fetch-depth of 1 for github actions
                logging.warning(
                    """
                       Running on github actions might lead to wrong git revision dates
                       due to a shallow git fetch depth.
                       Try setting fetch-depth to 0 in your github action
                       (see https://github.com/actions/checkout).
                       """
                )

    @staticmethod
    def _date_formats(unix_timestamp: float, locale="en") -> dict:
        """
        Returns different date formats / types.

        Args:
            unix_timestamp (datetiment): a timestamp in seconds since 1970
            locale (str): Locale code of language to use. Defaults to 'en'.

        Returns:
            dict: different date formats
        """

        # Convert to millisecond timestamp
        unix_timestamp = int(unix_timestamp)
        timestamp_in_ms = unix_timestamp * 1000

        revision_date = datetime.utcfromtimestamp(unix_timestamp)
        logging.debug("Revision date: %s - Locale: %s" % (revision_date, locale))

        return {
            "date": format_date(revision_date, format="long", locale=locale),
            "datetime": format_date(revision_date, format="long", locale=locale)
            + " "
            + revision_date.strftime("%H:%M:%S"),
            "iso_date": revision_date.strftime("%Y-%m-%d"),
            "iso_datetime": revision_date.strftime("%Y-%m-%d %H:%M:%S"),
            "timeago": "<span class='timeago' datetime='%s' locale='%s'></span>"
            % (timestamp_in_ms, locale),
        }

    def get_revision_date_for_file(
        self, path: str, locale: str = "en", fallback_to_build_date: bool = False
    ) -> dict:
        """
        Determine localized date variants for a given file

        Args:
            path (str): Location of a markdownfile that is part of a GIT repository
            locale (str, optional): Locale code of language to use. Defaults to 'en'.

        Returns:
            dict: localized date variants
        """
        # perform git log operation
        try:
            unix_timestamp = self.repo.log(path, n=1, date="short", format="%at")
        except GitCommandError as err:
            if fallback_to_build_date:
                unix_timestamp = None
                logging.warning(
                    "Unable to read git logs of '%s'."
                    " Is git log readable?"
                    " Option 'fallback_to_build_date' enabled: so keep building..." % path
                )
            else:
                logging.error(
                    "Unable to read git logs of '%s'. "
                    "To ignore this error, set option 'fallback_to_build_date: true'"
                    % path
                )
                raise err
        except GitCommandNotFound as err:
            if fallback_to_build_date:
                unix_timestamp = None
                logging.warning(
                    "Unable to perform command: git log. Is git installed?"
                    " Option 'fallback_to_build_date' enabled: so keep building..."
                )
            else:
                logging.error(
                    "Unable to perform command: git log. Is git installed?"
                    "To ignore this error, set option 'fallback_to_build_date: true'"
                )
                raise err

        # create timestamp
        if not unix_timestamp:
            unix_timestamp = time.time()
            logging.warning("%s has no git logs, using current timestamp" % path)

        return self._date_formats(unix_timestamp=unix_timestamp, locale=locale)


def is_shallow_clone(repo: Git) -> bool:
    """
    Helper function to determine if repository
    is a shallow clone.

    References:
    https://github.com/timvink/mkdocs-git-revision-date-localized-plugin/issues/10
    https://stackoverflow.com/a/37203240/5525118

    Args:
        repo (git.Repo): Repository

    Returns:
        bool: If a repo is shallow clone
    """
    return os.path.exists(".git/shallow")


def commit_count(repo: Git) -> bool:
    """
    Helper function to determine the number of commits in a repository

    Args:
        repo (git.Repo): Repository

    Returns:
        count (int): Number of commits
    """
    refs = repo.for_each_ref().split("\n")
    refs = [x.split()[0] for x in refs]

    counts = [int(repo.rev_list(x, count=True, first_parent=True)) for x in refs]
    return max(counts)
