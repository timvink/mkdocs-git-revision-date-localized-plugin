"""
MkDocs Plugin.

https://www.mkdocs.org/
https://github.com/timvink/mkdocs-git-revision-date-localized-plugin/
"""

import logging
import re
import os
import time
import multiprocessing
from pathlib import Path

from mkdocs import __version__ as mkdocs_version
from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from mkdocs.structure.nav import Page
from mkdocs.utils import copy_file
from mkdocs.exceptions import ConfigurationError
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.files import Files

from mkdocs_git_revision_date_localized_plugin.util import Util
from mkdocs_git_revision_date_localized_plugin.exclude import exclude

from typing import Any, Dict, Optional
from collections import OrderedDict

from packaging.version import Version

HERE = Path(__file__).parent.absolute()


class GitRevisionDateLocalizedPlugin(BasePlugin):
    """
    Mkdocs plugin to add revision date from Git.

    See https://www.mkdocs.org/user-guide/plugins
    """

    config_scheme = (
        ("fallback_to_build_date", config_options.Type(bool, default=False)),
        ("locale", config_options.Type(str, default=None)),
        ("type", config_options.Type(str, default="date")),
        ("custom_format", config_options.Type(str, default="%d. %B %Y")),
        ("timezone", config_options.Type(str, default="UTC")),
        ("exclude", config_options.Type(list, default=[])),
        ("enable_creation_date", config_options.Type(bool, default=False)),
        ("enabled", config_options.Type(bool, default=True)),
        ("strict", config_options.Type(bool, default=True)),
        ("enable_git_follow", config_options.Type(bool, default=True)),
        ("ignored_commits_file", config_options.Type(str, default=None)),
        ("enable_parallel_processing", config_options.Type(bool, default=True)),
    )

    def __init__(self):
        super().__init__()
        self.last_revision_commits = {}
        self.created_commits = {}

    def on_config(self, config: config_options.Config, **kwargs) -> Dict[str, Any]:
        """
        Determine which locale to use.

        The config event is the first event called on build and
        is run immediately after the user configuration is loaded and validated.
        Any alterations to the config should be made here.
        https://www.mkdocs.org/user-guide/plugins/#on_config

        Args:
            config (dict): global configuration object

        Returns:
            dict: global configuration object
        """
        if not self.config.get("enabled"):
            return config

        assert self.config["type"] in ["date", "datetime", "iso_date", "iso_datetime", "timeago", "custom"]

        self.util = Util(
            config=self.config, mkdocs_dir=os.path.abspath(os.path.dirname(config.get("config_file_path")))
        )

        # Save last commit timestamp for entire site
        # Support monorepo/techdocs, which copies the docs_dir to a temporary directory
        mono_repo_plugin = config.get("plugins", {}).get("monorepo", None)
        if mono_repo_plugin is not None and hasattr(mono_repo_plugin, "originalDocsDir") and mono_repo_plugin.originalDocsDir is not None:
            self.last_site_revision_hash, self.last_site_revision_timestamp = self.util.get_git_commit_timestamp(
                mono_repo_plugin.originalDocsDir
            )
        else:
            self.last_site_revision_hash, self.last_site_revision_timestamp = self.util.get_git_commit_timestamp(
                config.get("docs_dir")
            )

        # Get locale from plugin configuration
        plugin_locale = self.config.get("locale", None)

        # Get locale from theme configuration
        if "theme" in config and "language" in config.get("theme"):
            custom_theme = config.get("theme")
            theme_locale = (
                custom_theme["language"]
                if Version(mkdocs_version) >= Version("1.6.0")
                else custom_theme._vars.get("language")
            )
            logging.debug("Locale '%s' extracted from the custom theme: '%s'" % (theme_locale, custom_theme.name))
        elif "theme" in config and "locale" in config.get("theme"):
            custom_theme = config.get("theme")
            theme_locale = (
                custom_theme.locale if Version(mkdocs_version) >= Version("1.6.0") else custom_theme._vars.get("locale")
            )
            logging.debug("Locale '%s' extracted from the custom theme: '%s'" % (theme_locale, custom_theme.name))
        else:
            theme_locale = None
            logging.debug("No locale found in theme configuration (or no custom theme set)")

        # First prio: plugin locale
        if plugin_locale:
            locale_set = plugin_locale
            logging.debug("Using locale from plugin configuration: %s" % locale_set)
        # Second prio: theme locale
        elif theme_locale:
            locale_set = theme_locale
            logging.debug("Locale not set in plugin. Fallback to theme configuration: %s" % locale_set)
        # Lastly, fallback is English
        else:
            locale_set = "en"
            logging.debug("No locale set. Fallback to: %s" % locale_set)

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

    def parallel_compute_commit_timestamps(self, files, original_source: Optional[Dict] = None, is_first_commit=False):
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
                abs_src_path = f.abs_src_path
                # Support plugins like monorepo that might have moved the files from the original source that is under git
                if original_source and abs_src_path in original_source:
                    abs_src_path = original_source[abs_src_path]
                
                assert Path(abs_src_path).exists()
                abs_src_path = str(Path(abs_src_path).absolute())
                result = pool.apply_async(self.util.get_git_commit_timestamp, args=(abs_src_path, is_first_commit))
                results.append((abs_src_path, result))
        pool.close()
        pool.join()
        if is_first_commit:
            for src_uri, result in results:
                self.created_commits[src_uri] = result.get()
        else:
            for src_uri, result in results:
                self.last_revision_commits[src_uri] = result.get()

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
            if not self.last_revision_commits:
               self.parallel_compute_commit_timestamps(files=files, original_source=original_source, is_first_commit=False)
            if not self.created_commits:
                self.parallel_compute_commit_timestamps(files=files, original_source=original_source, is_first_commit=True)
        except Exception as e:
            logging.warning(f"Parallel processing failed: {str(e)}.\n To fall back to serial processing, use 'enable_parallel_processing: False' setting.")
            raise e
            

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
            logging.debug("Excluding page " + page.file.src_path)
            return markdown

        # Find the locale

        # First prio is use mkdocs-static-i18n locale if set
        try:
            locale = page.file.locale
        except AttributeError:
            locale = None

        # Second prio is a frontmatter variable 'locale' set in the markdown
        if not locale:
            if "locale" in page.meta:
                locale = page.meta["locale"]

        # Finally, if no page locale set, we take the locale determined on_config()
        # (fourth prio is plugin configuration)
        # (firth prio is theme configuration)
        # (sixth prio is fallback to English)
        if not locale:
            locale = self.config.get("locale")

        # Retrieve git commit timestamp
        # Except for generated pages (f.e. by mkdocs-gen-files plugin)
        if getattr(page.file, "generated_by", None):
            last_revision_hash, last_revision_timestamp = "", int(time.time())
        else:
            last_revision_hash, last_revision_timestamp = self.last_revision_commits.get(
                str(Path(page.file.abs_src_path).absolute()), (None, None)
            )
            if last_revision_timestamp is None:
                last_revision_hash, last_revision_timestamp = self.util.get_git_commit_timestamp(
                    path=page.file.abs_src_path,
                    is_first_commit=False,
                )

        # Last revision date
        revision_dates = self.util.get_date_formats_for_timestamp(
            last_revision_timestamp, locale=locale, add_spans=True
        )
        revision_date = revision_dates[self.config["type"]]

        # timeago output is dynamic, which breaks when you print a page
        # This ensures fallback to type "iso_date"
        # controlled via CSS (see on_post_build() event)
        if self.config["type"] == "timeago":
            revision_date += revision_dates["iso_date"]

        # Add to page meta information, for developers
        # Include variants without the CSS <span> elements (raw date strings)
        page.meta["git_revision_date_localized"] = revision_date
        page.meta["git_revision_date_localized_hash"] = last_revision_hash
        page.meta["git_revision_date_localized_tag"] = self.util.get_tag_name_for_commit(last_revision_hash)
        revision_dates_raw = self.util.get_date_formats_for_timestamp(
            last_revision_timestamp, locale=locale, add_spans=False
        )
        for date_type, date_string in revision_dates_raw.items():
            page.meta["git_revision_date_localized_raw_%s" % date_type] = date_string

        # Replace any occurances in markdown page
        markdown = re.sub(
            r"\{\{\s*git_revision_date_localized\s*\}\}",
            revision_date,
            markdown,
            flags=re.IGNORECASE,
        )

        # Also add site last updated information, for developers
        page.meta["git_site_revision_date_localized_hash"] = self.last_site_revision_hash
        page.meta["git_site_revision_date_localized_tag"] = self.util.get_tag_name_for_commit(
            self.last_site_revision_hash
        )
        site_dates = self.util.get_date_formats_for_timestamp(
            self.last_site_revision_timestamp, locale=locale, add_spans=True
        )
        site_date = site_dates[self.config["type"]]
        if self.config["type"] == "timeago":
            site_date += site_dates["iso_date"]
        page.meta["git_site_revision_date_localized"] = site_date
        site_dates_raw = self.util.get_date_formats_for_timestamp(
            self.last_site_revision_timestamp, locale=locale, add_spans=False
        )
        for date_type, date_string in site_dates_raw.items():
            page.meta["git_site_revision_date_localized_raw_%s" % date_type] = date_string

        # Replace any occurances in markdown page
        markdown = re.sub(
            r"\{\{\s*git_site_revision_date_localized\s*\}\}",
            site_date,
            markdown,
            flags=re.IGNORECASE,
        )

        # If creation date not enabled, return markdown
        # This is for speed: prevents another `git log` operation each file
        if not self.config.get("enable_creation_date"):
            return markdown

        # Retrieve git commit timestamp
        # Except for generated pages (f.e. by mkdocs-gen-files plugin)
        if getattr(page.file, "generated_by", None):
            first_revision_hash, first_revision_timestamp = "", int(time.time())
        else:
            first_revision_hash, first_revision_timestamp = self.created_commits.get(
                str(Path(page.file.abs_src_path).absolute()), (None, None)
            )
            if first_revision_timestamp is None:
                first_revision_hash, first_revision_timestamp = self.util.get_git_commit_timestamp(
                    path=page.file.abs_src_path,
                    is_first_commit=True,
                )

        if first_revision_timestamp > last_revision_timestamp:
            # See also https://github.com/timvink/mkdocs-git-revision-date-localized-plugin/issues/111
            msg = "First revision timestamp is older than last revision timestamp for page %s. " % page.file.src_path
            msg += "This can be due to a quirk in `git` follow behaviour. You can try to set `enable_git_follow: false` in the plugin configuration."
            logging.warning(msg)
            first_revision_hash, first_revision_timestamp = last_revision_hash, last_revision_timestamp

        # Creation date formats
        creation_dates = self.util.get_date_formats_for_timestamp(
            first_revision_timestamp, locale=locale, add_spans=True
        )
        creation_date = creation_dates[self.config["type"]]

        # timeago output is dynamic, which breaks when you print a page
        # This ensures fallback to type "iso_date"
        # controlled via CSS (see on_post_build() event)
        if self.config["type"] == "timeago":
            creation_date += creation_dates["iso_date"]

        # Add to page meta information, for developers
        # Include variants without the CSS <span> elements (raw date strings)
        page.meta["git_creation_date_localized_hash"] = first_revision_hash
        page.meta["git_creation_date_localized_tag"] = self.util.get_tag_name_for_commit(first_revision_hash)
        page.meta["git_creation_date_localized"] = creation_date
        creation_dates_raw = self.util.get_date_formats_for_timestamp(
            first_revision_timestamp, locale=locale, add_spans=False
        )
        for date_type, date_string in creation_dates_raw.items():
            page.meta["git_creation_date_localized_raw_%s" % date_type] = date_string

        # Replace any occurances in markdown page
        markdown = re.sub(
            r"\{\{\s*git_creation_date_localized\s*\}\}",
            creation_date,
            markdown,
            flags=re.IGNORECASE,
        )

        return markdown

    def on_post_build(self, config: Dict[str, Any], **kwargs) -> None:
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
