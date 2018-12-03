from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from .util import Util


class GitRevisionDatePlugin(BasePlugin):
    config_scheme = (
        ('write_file_meta', config_options.Type(bool, default=False)),
    )

    def __init__(self):
        self.write = False
        self.util = Util()

    def on_config(self, config):
        self.write = self.config['write_file_meta']

    def on_page_markdown(self, markdown, page, config, files):
        revision_date = self.util.get_revision_date_for_file(page.file.abs_src_path)

        if not revision_date:
            from datetime import datetime
            revision_date = datetime.now().date()
            print('WARNING -  %s has no git logs, revision date defaulting to today\'s date' % page.file.src_path)

        page.meta['revision_date'] = revision_date
        return markdown