# standard lib
import logging
import re

# 3rd party
from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from mkdocs.structure.nav import Page

# package modules
from mkdocs_git_revision_date_localized_plugin.util import Util


class GitRevisionDateLocalizedPlugin(BasePlugin):
    config_scheme = (
        ("fallback_to_build_date", config_options.Type(bool, default=False)),
        ("locale", config_options.Type(str, default=None)),
        ("type", config_options.Type(str, default="date")),
    )

    def __init__(self):
        self.util = Util()

    def on_config(self, config: config_options.Config) -> dict:
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

        # Get locale settings - might be added in future mkdocs versions
        # see: https://github.com/timvink/mkdocs-git-revision-date-localized-plugin/issues/24
        mkdocs_locale = config.get("locale", None)

        # Get locale from plugin configuration
        plugin_locale = self.config.get("locale", None)

        # theme locale
        if "theme" in config and "locale" in config.get("theme"):
            custom_theme = config.get("theme")
            theme_locale = custom_theme._vars.get("locale")
            logging.debug(
                "Locale '%s' extracted from the custom theme: '%s'"
                % (theme_locale, custom_theme.name)
            )
        elif "theme" in config and "language" in config.get("theme"):
            custom_theme = config.get("theme")
            theme_locale = custom_theme._vars.get("language")
            logging.debug(
                "Locale '%s' extracted from the custom theme: '%s'"
                % (theme_locale, custom_theme.name)
            )

        else:
            theme_locale = None
            logging.debug(
                "No locale found in theme configuration (or no custom theme set)"
            )

        # First prio: plugin locale
        if plugin_locale:
            locale_set = plugin_locale
            logging.debug("Using locale from plugin configuration: %s" % locale_set)
        # Second prio: theme locale
        elif theme_locale:
            locale_set = theme_locale
            logging.debug(
                "Locale not set in plugin. Fallback to theme configuration: %s"
                % locale_set
            )
        # Third prio is mkdocs locale (which might be added in the future)
        elif mkdocs_locale:
            locale_set = mkdocs_locale
            logging.debug("Using locale from mkdocs configuration: %s" % locale_set)
        else:
            locale_set = "en"
            logging.debug("No locale set. Fallback to: %s" % locale_set)

        # set locale also in plugin configuration
        self.config["locale"] = locale_set

        return config

    def on_post_page(self, output_content: str, **kwargs) -> str:
        """
        Add timeago.js as a CDN to the HTML page.
        The CDN with latest version timeago.js can be found on
        https://cdnjs.com/libraries/timeago.js

        The `post_template` event is called after the template is rendered,
        but before it is written to disc and can be used to alter the output
        of the page. If an empty string is returned, the page is skipped
        and nothing is written to disc.

        https://www.mkdocs.org/user-guide/plugins/#on_post_page

        Args:
            output_content (str): output of rendered template as string

        Returns:
            str: output of rendered template as string
        """

        if self.config.get("type") != "timeago":
            return output_content

        extra_js = """
          <script src="https://cdnjs.cloudflare.com/ajax/libs/timeago.js/4.0.0-beta.2/timeago.min.js"></script>
          <script src="https://cdnjs.cloudflare.com/ajax/libs/timeago.js/4.0.0-beta.2/timeago.locales.min.js"></script>
          <script>
            var nodes = document.querySelectorAll('.timeago');
            var locale = nodes[0].getAttribute('locale');
            timeago.render(nodes, locale);
          </script>
        """
        idx = output_content.index("</body>")
        return output_content[:idx] + extra_js + output_content[idx:]

    def on_page_markdown(
        self, markdown: str, page: Page, config: config_options.Config, files
    ) -> str:
        """
        Replace jinja2 tags in markdown and templates with the localized dates

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

        revision_dates = self.util.get_revision_date_for_file(
            path=page.file.abs_src_path,
            locale=self.config.get("locale", "en"),
            fallback_to_build_date=self.config.get("fallback_to_build_date"),
        )
        revision_date = revision_dates[self.config["type"]]
        page.meta["git_revision_date_localized"] = revision_date
        return re.sub(
            r"\{\{\s*[page\.meta\.]*git_revision_date_localized\s*\}\}",
            revision_date,
            markdown,
            flags=re.IGNORECASE,
        )


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """Standalone execution and quick tests."""
    pass
