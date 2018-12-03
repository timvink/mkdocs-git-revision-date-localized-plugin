from os import environ

from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from mkdocs.utils import string_types
from .util import Util


class GitRevisionDatePlugin(BasePlugin):
    config_scheme = (
        ('enabled_if_env', config_options.Type(string_types)),
    )

    def __init__(self):
        self.enabled = True
        self.util = Util()

    def on_config(self, config):
        env_name = self.config['enabled_if_env']
        if env_name:
            self.enabled = environ.get(env_name) == '1'
            if not self.enabled:
                print('PDF export is disabled (set environment variable %s to 1 to enable)' % env_name)
                return

    def on_page_markdown(self, markdown, page, config, files):
        if not self.enabled:
            return markdown

        revision_date = self.util.get_revision_date_for_file(page.file.abs_src_path)

        if not revision_date:
            from datetime import datetime
            revision_date = datetime.now().date()
            print('WARNING -  %s has no git logs, revision date defaulting to today\'s date' % page.file.src_path)

        page.meta['revision_date'] = revision_date
        return markdown