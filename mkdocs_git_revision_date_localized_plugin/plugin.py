import re
from os import environ

from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from mkdocs.utils import string_types
from .util import Util
from datetime import datetime


class GitRevisionDateLocalizedPlugin(BasePlugin):
    config_scheme = (
        ('locale', config_options.Type(string_types, default='')),
        ('type', config_options.Type(string_types, default='date'))
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
        
        # First prio: theme
        if theme_locale:
            self.locale = theme_locale
            return
        
        # Second prio: plugin locale     
        if plugin_locale != '':
            self.locale = plugin_locale
            return
        
        # Third is mkdocs locale setting (might be added in the future)
        if mkdocs_locale:
            self.locale = mkdocs_locale
        
        # If none set then english
        self.locale = 'en'
        return
        

    def on_page_markdown(self, markdown, page, config, files):

        revision_dates = self.util.get_revision_date_for_file(
            path = page.file.abs_src_path,
            locale = self.locale
        )
        revision_date = revision_dates[self.config['type']] 

        page.meta['git_revision_date_localized'] = revision_date
        
        if 'macros' in config['plugins']:
            keys = list(config['plugins'].keys())
            vals = list(config['plugins'].values())
            if keys.index('macros') > vals.index(self):
                return '{{% set git_revision_date = \'{}\' %}}\n'.format(revision_date) + markdown
            else:
                print('WARNING - macros plugin must be placed AFTER the git-revision-date-localized plugin. Skipping markdown modifications')
                return markdown
        else:
            markdown = re.sub(r"\{\{(\s)*git_revision_date_localized(\s)*\}\}",
                          revision_date,
                          markdown,
                          flags=re.IGNORECASE)

            markdown = re.sub(r"\{\{\s*page\.meta\.git_revision_date_localized\s*\}\}",
                          revision_date,
                          markdown,
                          flags=re.IGNORECASE)
            
            return markdown
        
