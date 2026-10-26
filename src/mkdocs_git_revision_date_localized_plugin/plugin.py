"""
MkDocs Plugin.

https://www.mkdocs.org/
https://github.com/timvink/mkdocs-git-revision-date-localized-plugin/
"""

import os
import re
import time
from collections import OrderedDict
from pathlib import Path

from mkdocs import __version__ as mkdocs_version
from mkdocs.config import config_options
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.exceptions import ConfigurationError
from mkdocs.plugins import BasePlugin, get_plugin_logger
from mkdocs.structure.files import Files
from mkdocs.structure.nav import Page
from mkdocs.utils import copy_file
from packaging.version import Version

from mkdocs_git_revision_date_localized_plugin.exclude import exclude
from mkdocs_git_revision_date_localized_plugin.util import Util

logger = get_plugin_logger(__name__)

HERE = Path(__file__).parent.absolute()

DATE_TYPES = ("date", "datetime", "iso_date", "iso_datetime", "timeago", "custom")


class GitRevisionDateLocalizedPlugin(BasePlugin):
    """
    Mkdocs plugin to add revision date from Git.

    See https://www.mkdocs.org/user-guide/plugins
    """

    config_scheme = (
        ("fallback_to_build_date", config_options.Type(bool, default=False)),
        ("locale", config_options.Optional(config_options.Type(str))),
        ("type", config_options.Choice(DATE_TYPES, default="date")),
        ("custom_format", config_options.Type(str, default="%d. %B %Y")),
        ("timezone", config_options.Type(str, default="UTC")),
        ("exclude", config_options.Type(list, default=[])),
        ("enable_creation_date", config_options.Type(bool, default=False)),
        ("enabled", config_options.Type(bool, default=True)),
        ("strict", config_options.Type(bool, default=True)),
        ("enable_git_follow", config_options.Type(bool, default=True)),
        ("ignored_commits_file", config_options.Optional(config_options.Type(str))),
        ("enable_parallel_processing", config_options.Type(bool, default=True)),
    )

    def __init__(self):
        super().__init__()
        self.last_revision_commits = {}
        self.created_commits = {}
        self.generated_timestamps = {}
        # Maps each cache key to the path of the file under git. They differ when
        # monorepo moved the file; both paths are cache keys.
        self.cached_source_paths: dict[str, str] = {}
        # HEAD commit and history options the caches above are valid for. A commit
        # made during `mkdocs serve` moves HEAD, which makes some cached timestamps stale.
        self.cached_head_commit = ""
        self.cached_history_options: tuple = ()

    def on_startup(self, *, command: str, dirty: bool) -> None:
        """
        Run on startup.

        Note that "The presence of an on_startup method (even if empty)
        migrates the plugin to the new system where the plugin object is
        kept across builds within one mkdocs serve."

        Args:
            command (str): The mkdocs command being run.
            dirty (bool): Whether the --dirty flag was passed. Note this is set once for
                the whole invocation, not per rebuild.
        """
        # Runs once per invocation, before the first build. The caches then persist
        # across `mkdocs serve` rebuilds and are invalidated in on_config().
        self.last_revision_commits = {}
        self.created_commits = {}
        self.cached_source_paths = {}
        self.cached_head_commit = ""
        self.cached_history_options = ()

    def on_pre_build(self, *, config: MkDocsConfig) -> None:
        # Generated pages get a timestamp per build; start fresh for every (re)build
        self.generated_timestamps = {}

    def on_config(self, config: MkDocsConfig) -> MkDocsConfig | None:
        """
        Determine which locale to use.

        The config event is the first event called on build and
        is run immediately after the user configuration is loaded and validated.
        Any alterations to the config should be made here.
        https://www.mkdocs.org/user-guide/plugins/#on_config

        Args:
            config (MkDocsConfig): global configuration object

        Returns:
            MkDocsConfig | None: global configuration object
        """
        if not self.config.get("enabled"):
            return config

        config_file_path = config.get("config_file_path") or ""
        self.util = Util(config=self.config, mkdocs_dir=os.path.abspath(os.path.dirname(config_file_path)))

        # Support monorepo/techdocs, which copies the docs_dir to a temporary directory
        mono_repo_plugin = config.get("plugins", {}).get("monorepo", None)
        if (
            mono_repo_plugin is not None
            and hasattr(mono_repo_plugin, "originalDocsDir")
            and mono_repo_plugin.originalDocsDir is not None
        ):
            docs_dir = mono_repo_plugin.originalDocsDir
        else:
            docs_dir = config.get("docs_dir") or ""

        # Save last commit timestamp for entire site
        self.last_site_revision_hash, self.last_site_revision_timestamp = self.util.get_git_commit_timestamp(docs_dir)

        self._invalidate_stale_commits(docs_dir)

        # Get locale from plugin configuration
        plugin_locale = self.config.get("locale", None)

        # Get locale from theme configuration
        custom_theme = config.get("theme")
        if custom_theme is not None and "language" in custom_theme:
            theme_locale = (
                custom_theme["language"]
                if Version(mkdocs_version) >= Version("1.6.0")
                else custom_theme._vars.get("language")
            )
            logger.debug(f"Locale '{theme_locale}' extracted from the custom theme: '{custom_theme.name}'")
        elif custom_theme is not None and "locale" in custom_theme:
            theme_locale = (
                custom_theme.locale if Version(mkdocs_version) >= Version("1.6.0") else custom_theme._vars.get("locale")
            )
            logger.debug(f"Locale '{theme_locale}' extracted from the custom theme: '{custom_theme.name}'")
        else:
            theme_locale = None
            logger.debug("No locale found in theme configuration (or no custom theme set)")

        # First prio: plugin locale
        if plugin_locale:
            locale_set = plugin_locale
            logger.debug(f"Using locale from plugin configuration: {locale_set}")
        # Second prio: theme locale
        elif theme_locale:
            locale_set = theme_locale
            logger.debug(f"Locale not set in plugin. Fallback to theme configuration: {locale_set}")
        # Lastly, fallback is English
        else:
            locale_set = "en"
            logger.debug(f"No locale set. Fallback to: {locale_set}")

        # Validate locale
        locale_set = str(locale_set)

        # set locale also in plugin configuration
        self.config["locale"] = locale_set

        # Add pointers to support files for timeago.js
        if self.config.get("type") == "timeago":
            config["extra_javascript"] = ["js/timeago_mkdocs_material.js"] + config["extra_javascript"]
            config["extra_javascript"] = ["js/timeago.min.js"] + config["extra_javascript"]
            config["extra_css"] = ["css/timeago.css"] + config["extra_css"]

        # Compatibility with mkdocs-static-i18n
        plugins = [*OrderedDict(config["plugins"])]
        if "i18n" in plugins:
            if plugins.index("git-revision-date-localized") < plugins.index("i18n"):
                msg = "[git-revision-date-localized] should be defined after the i18n plugin in your mkdocs.yml file. "
                msg += "This is because i18n adds a 'locale' variable to markdown pages that this plugin supports."
                raise ConfigurationError(msg)

        return config

    def _invalidate_stale_commits(self, docs_dir: str) -> None:
        """
        Drop cached page timestamps that commits since the previous build made stale.

        Only matters for `mkdocs serve`, which keeps this plugin object across rebuilds.
        After new commits on top of the cached HEAD, only the files those commits
        touched are dropped; _get_commit() then asks git for them directly. After
        anything else (a branch switch, rebase or amend, or a change to the options that
        decide which commits count) the caches are cleared and on_files() recomputes them.

        Args:
            docs_dir (str): Path to a directory in the repository that holds the docs.
        """
        head_commit = self.util.get_head_commit(docs_dir)
        # Any change to the plugin options (f.e. enable_git_follow) or the ignored commits
        # can change which commit a page gets, so treat it like rewritten history
        history_options = (dict(self.config), tuple(self.util.ignored_commits))
        if head_commit == self.cached_head_commit and history_options == self.cached_history_options:
            return

        changed = None
        if self.cached_head_commit and head_commit and history_options == self.cached_history_options:
            changed = self.util.get_files_changed_between(self.cached_head_commit, head_commit, docs_dir)

        if changed is None:
            self.last_revision_commits = {}
            self.created_commits = {}
            self.cached_source_paths = {}
        else:
            stale = [k for k, src in self.cached_source_paths.items() if self.util.normalize_path(src) in changed]
            for key in stale:
                self.last_revision_commits.pop(key, None)
                self.created_commits.pop(key, None)
                del self.cached_source_paths[key]

        # If every cached page was dropped, the caches are empty and on_files()
        # recomputes all pages, the same as on a first build
        self.cached_head_commit = head_commit
        self.cached_history_options = history_options

    def parallel_compute_commit_timestamps(self, files, original_source: dict | None = None, is_first_commit=False):
        import multiprocessing

        pool = multiprocessing.Pool(processes=min(10, multiprocessing.cpu_count()))
        results = []
        for f in files:
            if not f.is_documentation_page():
                continue
            elif getattr(f, "generated_by", None):
                continue
            elif f.abs_src_path is None:
                continue
            elif exclude(f.src_path, self.config.get("exclude", [])):
                continue
            else:
                temp_abs_src_path = str(Path(f.abs_src_path).absolute())
                abs_src_path = f.abs_src_path

                # Support plugins like monorepo that might have moved the files from the original source that is under git
                if original_source and abs_src_path in original_source:
                    abs_src_path = original_source[abs_src_path]

                assert Path(abs_src_path).exists()
                abs_src_path = str(Path(abs_src_path).absolute())
                result = pool.apply_async(self.util.get_git_commit_timestamp, args=(abs_src_path, is_first_commit))
                # Store both the original path and temp path (if different) so cache lookups work either way
                results.append((abs_src_path, abs_src_path, result))
                if temp_abs_src_path != abs_src_path:
                    results.append((temp_abs_src_path, abs_src_path, result))
        pool.close()
        pool.join()
        cache = self.created_commits if is_first_commit else self.last_revision_commits
        for src_uri, source_path, result in results:
            cache[src_uri] = result.get()
            self.cached_source_paths[src_uri] = source_path

    def on_files(self, files: Files, config: MkDocsConfig):
        """
        Compute commit timestamps for all files in parallel.
        """
        if not self.config.get("enabled") or not self.config.get("enable_parallel_processing"):
            return

        # Support monorepo/techdocs, which copies the docs_dir to a temporary directory
        mono_repo_plugin = config.get("plugins", {}).get("monorepo", None)
        if mono_repo_plugin is not None and hasattr(mono_repo_plugin, "merger") and mono_repo_plugin.merger is not None:
            original_source = mono_repo_plugin.merger.files_source_dir
        else:
            original_source = None

        try:
            # On `mkdocs serve` rebuilds the caches are still filled from an earlier build,
            # unless on_config() cleared them, so this only does work when needed.
            if not self.last_revision_commits:
                self.parallel_compute_commit_timestamps(
                    files=files, original_source=original_source, is_first_commit=False
                )
            # Creation dates need another `git log` per page, so only look them up when they are used
            if self.config.get("enable_creation_date") and not self.created_commits:
                self.parallel_compute_commit_timestamps(
                    files=files, original_source=original_source, is_first_commit=True
                )
        except Exception as e:
            logger.error(
                f"Could not read the git history in parallel: {e.__class__.__name__}: {e}\n"
                "Set 'enable_parallel_processing: false' in the plugin configuration to read it "
                "one file at a time instead, which is slower but avoids multiprocessing entirely."
            )
            raise

    def _get_locale(self, page: Page) -> str:
        """
        Determine the locale to use for a page.

        Args:
            page: mkdocs.nav.Page instance

        Returns:
            str: Locale code.
        """
        # First prio is use mkdocs-static-i18n locale if set
        locale = getattr(page.file, "locale", None)

        # Second prio is a frontmatter variable 'locale' set in the markdown
        if not locale:
            locale = page.meta.get("locale")

        # Finally, if no page locale set, we take the locale determined on_config()
        # (third prio is plugin configuration)
        # (fourth prio is theme configuration)
        # (fifth prio is fallback to English)
        if not locale:
            locale = self.config.get("locale")

        return locale

    def _get_commit(self, page: Page, is_first_commit: bool) -> tuple[str, int]:
        """
        Retrieve the git commit hash and timestamp for a page.

        Uses the timestamps computed on_files() when available, and falls back to
        asking git directly for pages that were not part of that batch.

        Args:
            page: mkdocs.nav.Page instance
            is_first_commit (bool): retrieve the commit that created the file.

        Returns:
            tuple[str, int]: commit hash and commit date in unix timestamp.
        """
        # Generated pages (f.e. by the mkdocs-gen-files plugin) are not in git.
        # Use a single timestamp per page, so the creation date can never be
        # later than the last revision date when the clock ticks between the two calls.
        if getattr(page.file, "generated_by", None):
            return "", self.generated_timestamps.setdefault(page.file.src_uri, int(time.time()))

        # abs_src_path should always be set for documentation pages
        assert page.file.abs_src_path is not None
        abs_src_path = page.file.abs_src_path

        cache = self.created_commits if is_first_commit else self.last_revision_commits
        use_cache = self.config.get("enable_parallel_processing") and cache
        cache_key = str(Path(abs_src_path).absolute())
        if use_cache and cache_key in cache:
            return cache[cache_key]

        # Directly call git if parallel processing is disabled, or the page is not cached
        commit = self.util.get_git_commit_timestamp(path=abs_src_path, is_first_commit=is_first_commit)
        if use_cache:
            # Pages dropped by _invalidate_stale_commits() are cached again here
            cache[cache_key] = commit
            self.cached_source_paths[cache_key] = cache_key
        return commit

    def _render_date(
        self,
        markdown: str,
        page: Page,
        locale: str,
        variable: str,
        commit_hash: str,
        commit_timestamp: int,
    ) -> str:
        """
        Add a date to the page meta information and replace its jinja2 tag in the markdown.

        Args:
            markdown (str): Markdown source text of page as string
            page: mkdocs.nav.Page instance
            locale (str): Locale code of language to use
            variable (str): Name of the jinja2 tag and the page.meta prefix,
                f.e. 'git_revision_date_localized'
            commit_hash (str): Commit hash to expose to developers
            commit_timestamp (int): Commit date in unix timestamp

        Returns:
            str: Markdown source text of page as string
        """
        date_formats = self.util.get_date_formats_for_timestamp(commit_timestamp, locale=locale, add_spans=True)
        date = date_formats[self.config["type"]]

        # timeago output is dynamic, which breaks when you print a page
        # This ensures fallback to type "iso_date"
        # controlled via CSS (see on_post_build() event)
        if self.config["type"] == "timeago":
            date += date_formats["iso_date"]

        # Add to page meta information, for developers
        page.meta[variable] = date
        page.meta[f"{variable}_hash"] = commit_hash
        page.meta[f"{variable}_tag"] = self.util.get_tag_name_for_commit(commit_hash)

        # Include variants without the CSS <span> elements (raw date strings)
        date_formats_raw = self.util.get_date_formats_for_timestamp(commit_timestamp, locale=locale, add_spans=False)
        for date_type, date_string in date_formats_raw.items():
            page.meta[f"{variable}_raw_{date_type}"] = date_string

        # Replace any occurances in the markdown page.
        # A lambda is used as the replacement so that backslashes in the date
        # (possible with a custom_format) are not read as regex escapes.
        return re.sub(
            r"\{\{\s*" + variable + r"\s*\}\}",
            lambda _: date,
            markdown,
            flags=re.IGNORECASE,
        )

    def on_page_markdown(self, markdown: str, page: Page, config: config_options.Config, files, **kwargs) -> str:
        """
        Replace jinja2 tags in markdown and templates with the localized dates.

        The page_markdown event is called after the page's markdown is loaded
        from file and can be used to alter the Markdown source text.
        The meta- data has been stripped off and is available as page.meta
        at this point.

        https://www.mkdocs.org/user-guide/plugins/#on_page_markdown

        Args:
            markdown (str): Markdown source text of page as string
            page: mkdocs.nav.Page instance
            config: global configuration object
            site_navigation: global navigation object

        Returns:
            str: Markdown source text of page as string
        """
        if not self.config.get("enabled"):
            return markdown

        # Exclude pages specified in config
        excluded_pages = self.config.get("exclude", [])
        if exclude(page.file.src_path, excluded_pages):
            logger.debug("Excluding page " + page.file.src_path)
            return markdown

        locale = self._get_locale(page)

        # Last revision date of this page
        last_revision_hash, last_revision_timestamp = self._get_commit(page, is_first_commit=False)
        markdown = self._render_date(
            markdown=markdown,
            page=page,
            locale=locale,
            variable="git_revision_date_localized",
            commit_hash=last_revision_hash,
            commit_timestamp=last_revision_timestamp,
        )

        # Last revision date of the entire site
        markdown = self._render_date(
            markdown=markdown,
            page=page,
            locale=locale,
            variable="git_site_revision_date_localized",
            commit_hash=self.last_site_revision_hash,
            commit_timestamp=self.last_site_revision_timestamp,
        )

        # If creation date not enabled, return markdown
        # This is for speed: prevents another `git log` operation each file
        if not self.config.get("enable_creation_date"):
            return markdown

        # Creation date of this page
        first_revision_hash, first_revision_timestamp = self._get_commit(page, is_first_commit=True)

        if first_revision_timestamp > last_revision_timestamp:
            # See also https://github.com/timvink/mkdocs-git-revision-date-localized-plugin/issues/111
            msg = f"First revision timestamp is older than last revision timestamp for page {page.file.src_path}. "
            msg += "This can be due to a quirk in `git` follow behaviour. You can try to set `enable_git_follow: false` in the plugin configuration."
            logger.warning(msg)
            first_revision_hash, first_revision_timestamp = last_revision_hash, last_revision_timestamp

        return self._render_date(
            markdown=markdown,
            page=page,
            locale=locale,
            variable="git_creation_date_localized",
            commit_hash=first_revision_hash,
            commit_timestamp=first_revision_timestamp,
        )

    def on_post_build(self, *, config: MkDocsConfig) -> None:
        """
        Run on post build.

        Adds the timeago assets to the build.
        """
        # Add timeago files:
        if self.config.get("type") == "timeago" and self.config.get("enabled"):
            files = [
                "js/timeago.min.js",
                "js/timeago_mkdocs_material.js",
                "css/timeago.css",
            ]
            for f in files:
                dest_file_path = Path(config["site_dir"]) / f
                src_file_path = HERE / f
                assert src_file_path.exists()
                copy_file(str(src_file_path), str(dest_file_path))
