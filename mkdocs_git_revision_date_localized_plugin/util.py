from git import Git
from datetime import datetime
from babel.dates import format_date

class Util:

    def __init__(self):
        self.g = Git()

    def get_revision_date_for_file(self, path: str, locale: str = 'en'):
        """
        Determine localized date variants for a given file
        
        Args:
            path (str): Location of a file that is part of a GIT repository
            locale (str, optional): Locale code of language to use. Defaults to 'en'.
        
        Returns:
            dict: localized date variants 
        """
        
        unix_timestamp = self.g.log(path, n=1, date='short', format='%at')
        
        if not unix_timestamp:
            unix_timestamp = datetime.now().timestamp() 
            print('WARNING - %s has no git logs, using current timestamp' % path)
        
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