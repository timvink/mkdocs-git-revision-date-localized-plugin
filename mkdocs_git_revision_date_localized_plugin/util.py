import os
import logging
from git import Git
from datetime import datetime
from babel.dates import format_date

class Util:

    def __init__(self, path = "."):
        self.repo = Git(path)

    @staticmethod
    def _date_formats(unix_timestamp, locale = 'en'):
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
        
        return {
            'date' : format_date(revision_date, format="long", locale=locale), 
            'datetime' : format_date(revision_date, format="long", locale=locale) + ' ' +revision_date.strftime("%H:%M:%S"),
            'iso_date' : revision_date.strftime("%Y-%m-%d"), 
            'iso_datetime' : revision_date.strftime("%Y-%m-%d %H:%M:%S"), 
            'timeago' : "<span class='timeago' datetime='%s' locale='%s'></span>" % (timestamp_in_ms, locale)
        }
        

    def get_revision_date_for_file(self, path, locale = 'en'):
        """
        Determine localized date variants for a given file
        
        Args:
            path (str): Location of a markdownfile that is part of a GIT repository
            locale (str, optional): Locale code of language to use. Defaults to 'en'.
        
        Returns:
            dict: localized date variants 
        """
        
        unix_timestamp = self.repo.log(path, n=1, date='short', format='%at')
        

        if not unix_timestamp:
            
            if os.environ.get('GITLAB_CI'):
                raise EnvironmentError("""Cannot access git commit for '%s'. 
                       Try setting GIT_DEPTH to 1000 in your .gitlab-ci.yml file.
                       (see https://docs.gitlab.com/ee/user/project/pipelines/settings.html#git-shallow-clone).
                       Or disable mkdocs-git-revision-date-localized-plugin when using gitlab runners.
                       """ % path)

            if os.environ.get('GITHUB_ACTIONS'):
                raise EnvironmentError("""Cannot access git commit for '%s'. 
                       Try setting fetch-depth to 1 in your github action
                       (see https://github.com/actions/checkout).
                       Or disable mkdocs-git-revision-date-localized-plugin when using github actions.
                       """ % path)

            unix_timestamp = datetime.utcnow().timestamp()
            logging.warning('%s has no git logs, using current timestamp' % path)
            

        
        return self._date_formats(unix_timestamp)
