"""Utility class for mkdocs plugin."""
import logging
import os
import time
from datetime import datetime

from mkdocs_git_revision_date_localized_plugin.ci import raise_ci_warnings

from babel.dates import format_date, get_timezone
from git import (
    Repo,
    GitCommandError,
    GitCommandNotFound,
    InvalidGitRepositoryError,
    NoSuchPathError,
)

from typing import Any, Dict

logger = logging.getLogger("mkdocs.plugins")


class Util:
    """Utility class.

    This helps find git and calculate relevant dates.
    """

    def __init__(self, config={}):
        """Initialize utility class."""
        self.fallback_enabled = False
        self.config = config
        self.repo_cache = {}

    def _get_repo(self, path: str):
        if not os.path.isdir(path):
            path = os.path.dirname(path)

        if path not in self.repo_cache:
            self.repo_cache[path] = Repo(path, search_parent_directories=True).git
            # Checks if user is running builds on CI
            # and raise appropriate warnings
            raise_ci_warnings(self.repo_cache[path])

        return self.repo_cache[path]

    @staticmethod
    def _date_formats(
        unix_timestamp: float, locale: str = "en", time_zone: str = "UTC"
    ) -> Dict[str, Any]:
        """
        Calculate different date formats / types.

        Args:
            unix_timestamp (float): A timestamp in seconds since 1970.
            locale (str): Locale code of language to use. Defaults to 'en'.
            time_zone (str): Timezone database name (https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).

        Returns:
            dict: Different date formats.
        """
        utc_revision_date = datetime.utcfromtimestamp(int(unix_timestamp))
        loc_revision_date = utc_revision_date.replace(
            tzinfo=get_timezone("UTC")
        ).astimezone(get_timezone(time_zone))

        return {
            "date": format_date(loc_revision_date, format="long", locale=locale),
            "datetime": " ".join(
                [
                    format_date(loc_revision_date, format="long", locale=locale),
                    loc_revision_date.strftime("%H:%M:%S"),
                ]
            ),
            "iso_date": loc_revision_date.strftime("%Y-%m-%d"),
            "iso_datetime": loc_revision_date.strftime("%Y-%m-%d %H:%M:%S"),
            "timeago": '<span class="timeago" datetime="%s" locale="%s"></span>'
            % (loc_revision_date.isoformat(), locale),
        }

    def get_revision_date_for_file(
        self,
        path: str,
        locale: str = "en",
        time_zone: str = "UTC",
        fallback_to_build_date: bool = False,
    ) -> Dict[str, str]:
        """
        Determine localized date variants for a given file.

        Args:
            path (str): Location of a markdown file that is part of a Git repository.
            locale (str, optional): Locale code of language to use. Defaults to 'en'.
            timezone (str): Timezone database name (https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).

        Returns:
            dict: Localized date variants.
        """
        unix_timestamp = None

        # perform git log operation
        try:
            if not self.fallback_enabled:
                # Retrieve author date in UNIX format (%at)
                # https://git-scm.com/docs/git-log#Documentation/git-log.txt-ematem
                realpath = os.path.realpath(path)
                unix_timestamp = self._get_repo(realpath).log(
                    realpath, n=1, date="short", format="%at"
                )
        except (InvalidGitRepositoryError, NoSuchPathError) as err:
            if fallback_to_build_date:
                logger.warning(
                    "[git-revision-date-localized-plugin] Unable to find a git directory and/or git is not installed."
                    " Option 'fallback_to_build_date' set to 'true': Falling back to build date"
                )
            else:
                logger.error(
                    "[git-revision-date-localized-plugin] Unable to find a git directory and/or git is not installed."
                    " To ignore this error, set option 'fallback_to_build_date: true'"
                )
                raise err
        except GitCommandError as err:
            if fallback_to_build_date:
                logger.warning(
                    "[git-revision-date-localized-plugin] Unable to read git logs of '%s'. Is git log readable?"
                    " Option 'fallback_to_build_date' set to 'true': Falling back to build date"
                    % path
                )
            else:
                logger.error(
                    "[git-revision-date-localized-plugin] Unable to read git logs of '%s'. "
                    " To ignore this error, set option 'fallback_to_build_date: true'"
                    % path
                )
                raise err
        except GitCommandNotFound as err:
            if fallback_to_build_date:
                logger.warning(
                    "[git-revision-date-localized-plugin] Unable to perform command: 'git log'. Is git installed?"
                    " Option 'fallback_to_build_date' set to 'true': Falling back to build date"
                )
            else:
                logger.error(
                    "[git-revision-date-localized-plugin] Unable to perform command 'git log'. Is git installed?"
                    " To ignore this error, set option 'fallback_to_build_date: true'"
                )
                raise err

        # create timestamp
        if not unix_timestamp:
            unix_timestamp = time.time()
            if not self.fallback_enabled:
                logger.warning(
                    "[git-revision-date-localized-plugin] '%s' has no git logs, using current timestamp"
                    % path
                )

        date_formats = self._date_formats(
            unix_timestamp=unix_timestamp, time_zone=time_zone, locale=locale
        )

        # Wrap in <span> for styling
        for date_type, date_string in date_formats.items():
            date_formats[date_type] = (
                '<span class="git-revision-date-localized-plugin git-revision-date-localized-plugin-%s">%s</span>'
                % (date_type, date_string)
            )

        return date_formats
