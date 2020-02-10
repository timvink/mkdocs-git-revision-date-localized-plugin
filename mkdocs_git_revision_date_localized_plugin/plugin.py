import re
from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from .util import Util

class GitRevisionDateLocalizedPlugin(BasePlugin):
    config_scheme = (
        ('locale', config_options.Type(str, default='')),
        ('type', config_options.Type(str, default='date'))
    )

    def __init__(self):
        self.locale = 'en'
        self.util = Util()
        
    def on_config(self, config):
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

        # Get locale settings
        mkdocs_locale = config.get('locale', '')
        plugin_locale = self.config['locale']
        theme_locale = vars(config['theme']).get('_vars', {}).get('locale', '')
        if theme_locale == '':
            theme_locale = vars(config['theme']).get('_vars', {}).get('language','')
        
        # First prio: plugin locale     
        if plugin_locale != '':
            self.locale = plugin_locale
        # Second prio: theme locale
        elif theme_locale != '':
            self.locale = theme_locale        
        # Third prio is mkdocs locale (which might be added in the future)
        elif mkdocs_locale != '':
            self.locale = mkdocs_locale
        else:
            self.locale = 'en'
            
        return config
    
    def on_post_page(self, output_content, **kwargs):
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

        if self.config['type'] != 'timeago':
            return output_content
        
        extra_js = """
          <script src="https://cdnjs.cloudflare.com/ajax/libs/timeago.js/4.0.0-beta.2/timeago.min.js"></script>
          <script src="https://cdnjs.cloudflare.com/ajax/libs/timeago.js/4.0.0-beta.2/timeago.locales.min.js"></script>
          <script>
            const nodes = document.querySelectorAll('.timeago');
            const locale = nodes[0].getAttribute('locale');
            timeago.render(nodes, locale);
          </script>
        """
        idx = output_content.index("</body>")
        return output_content[:idx] + extra_js + output_content[idx:]
        
    def on_page_markdown(self, markdown, page, config, files):
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
            path = page.file.abs_src_path,
            locale = self.locale
        )
        revision_date = revision_dates[self.config['type']] 
        page.meta['git_revision_date_localized'] = revision_date
        
        return re.sub(r"\{\{\s*[page\.meta\.]*git_revision_date_localized\s*\}\}",
                        revision_date,
                        markdown,
                        flags=re.IGNORECASE)
        
