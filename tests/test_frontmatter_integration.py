import unittest
from unittest import mock
from pathlib import Path
from mkdocs_git_revision_date_localized_plugin.plugin import GitRevisionDateLocalizedPlugin
from mkdocs.structure.pages import Page
import os

class TestFrontmatterDates(unittest.TestCase):
    def setUp(self):
        self.plugin = GitRevisionDateLocalizedPlugin()
        self.plugin.config = {
            "enabled": True,
            "type": "date",
            "timezone": "UTC",
            "locale": "en",
            "fallback_to_build_date": False,
            "enable_creation_date": True
        }
        self.plugin.util = mock.MagicMock()
        self.plugin.last_revision_commits = {}
        self.plugin.created_commits = {}
        self.plugin.last_site_revision_timestamp = 123456
        self.plugin.last_site_revision_hash = "abcdef"
        
    def test_frontmatter_dates_priority(self):
        # Mock page with frontmatter containing date and lastmod
        page = mock.MagicMock()
        page.file.src_path = "test.md"
        page.file.abs_src_path = "/tmp/test.md"
        page.meta = {
            "date": "2022-01-01T12:00:00+00:00",
            "lastmod": "2023-02-02T12:00:00+00:00"
        }
        
        # Mock the util.parse_date_string method
        creation_timestamp = 1641038400  # 2022-01-01T12:00:00+00:00
        revision_timestamp = 1675339200  # 2023-02-02T12:00:00+00:00
        self.plugin.util.parse_date_string.side_effect = lambda d: creation_timestamp if d == "2022-01-01T12:00:00+00:00" else revision_timestamp
        
        # Setup date formatting responses
        self.plugin.util.get_date_formats_for_timestamp.return_value = {"date": "Jan 1, 2022"}
        
        # Mock git dates (these should not be used)
        self.plugin.util.get_git_commit_timestamp.return_value = ("git_hash", 9999999999)
        
        # Process the page markdown
        markdown = "# Test\n\nSome content with {{ git_revision_date_localized }} and {{ git_creation_date_localized }}"
        self.plugin.on_page_markdown(markdown, page, {}, None)
        
        # Verify parse_date_string was called with frontmatter dates
        self.plugin.util.parse_date_string.assert_any_call("2022-01-01T12:00:00+00:00")
        self.plugin.util.parse_date_string.assert_any_call("2023-02-02T12:00:00+00:00")
        
        # Verify git_commit_timestamp wasn't called (we're using frontmatter dates)
        self.plugin.util.get_git_commit_timestamp.assert_not_called()
        
        # Verify proper timestamps were used for date formatting
        call_args_list = self.plugin.util.get_date_formats_for_timestamp.call_args_list
        timestamps_used = [call[0][0] for call in call_args_list]
        
        # The list should contain both timestamps (revision and creation)
        self.assertIn(creation_timestamp, timestamps_used)
        self.assertIn(revision_timestamp, timestamps_used)
        
        # Check that the util.parse_date_string was called with the frontmatter dates
        self.plugin.util.parse_date_string.assert_any_call("2023-02-02T12:00:00+00:00")  # lastmod
        self.plugin.util.parse_date_string.assert_any_call("2022-01-01T12:00:00+00:00")  # date
        
        # The git_commit_timestamp should not be called for either date
        self.plugin.util.get_git_commit_timestamp.assert_not_called()
        
        # Check that meta fields were set correctly
        self.assertEqual(page.meta["git_creation_date_localized_hash"], "")  # No hash for frontmatter dates
        self.assertEqual(page.meta["git_revision_date_localized_hash"], "")  # No hash for frontmatter dates

if __name__ == '__main__':
    unittest.main()
