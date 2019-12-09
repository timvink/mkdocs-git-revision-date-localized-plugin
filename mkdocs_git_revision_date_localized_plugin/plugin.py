from os import environ

from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from mkdocs.utils import string_types
from jinja2 import Template
from .util import Util
from datetime import datetime


class GitRevisionDateLocalizedPlugin(BasePlugin):
    config_scheme = (
        ('locale', config_options.Type(string_types, default='')),
        ('modify_md', config_options.Type(bool, default=True))
    )

    def __init__(self):
        self.locale = 'en'
        self.util = Util()

    def on_config(self, config):

        # Get locale settings
        mkdocs_locale = config.get('locale')
        plugin_locale = self.config['locale']
        theme_locale = vars(config['theme']).get('_vars', {}).get('locale')
        if theme_locale is None:
            theme_locale = vars(config['theme']).get('_vars', {}).get('language')
        
        # First prio: plugin locale
        if plugin_locale != '':
            if plugin_locale != mkdocs_locale:
                print(f"WARNING - plugin locale setting '{plugin_locale}' will overwrite mkdocs locale '{mkdocs_locale}'")
            self.locale = mkdocs_locale
            return
        
        # Second prio: theme
        if theme_locale:
            self.locale = theme_locale
        # Third is mkdocs locale setting (might be add in the future)
        if mkdocs_locale:
            self.locale = mkdocs_locale
        
        # Final fallback is english
        return
        

    def on_page_markdown(self, markdown, page, config, files):

        revision_dates = self.util.get_revision_date_for_file(
            path = page.file.abs_src_path,
            locale = self.locale
        )

        for variable, date in revision_dates.items():
            page.meta[variable] = date
        
        if 'macros' in config['plugins']:
            keys = list(config['plugins'].keys())
            vals = list(config['plugins'].values())
            if keys.index('macros') > vals.index(self):
                for variable, date in revision_dates.items():
                    markdown = '{{% set' + variable + f" = '{date}' " + ' %}}' + markdown
                return markdown
            else:
                print('WARNING - macros plugin must be placed AFTER the git-revision-date-localized plugin. Skipping markdown modifications')
                return markdown
        else:
            return Template(markdown).render(revision_dates)
        
