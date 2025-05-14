"""Test the custom frontmatter field name functionality."""

import os
import datetime
import unittest

from mkdocs_git_revision_date_localized_plugin.util import Util
from mkdocs_git_revision_date_localized_plugin.plugin import GitRevisionDateLocalizedPlugin


class TestCustomFieldNameConfig(unittest.TestCase):
    """Test the custom frontmatter field name configuration."""

    def setUp(self):
        """Set up the test."""
        self.plugin = GitRevisionDateLocalizedPlugin()
        
        # Set plugin config
        self.plugin.config = {
            "enabled": True,
            "type": "date",
            "timezone": "UTC",
            "locale": "en"
        }
        
        # Initialize the util object
        self.plugin.util = Util(self.plugin.config, os.path.dirname(os.path.abspath(__file__)))
        
    def test_custom_creation_field_name_config(self):
        """Test custom creation date field name configuration."""
        # Test default value
        self.plugin.config = {"locale": "en"}
        self.assertEqual(self.plugin.config.get("creation_date_field_name", "date"), "date")
        
        # Test setting custom value
        self.plugin.config["creation_date_field_name"] = "created"
        self.assertEqual(self.plugin.config.get("creation_date_field_name"), "created")
        
    def test_custom_update_field_name_config(self):
        """Test custom update date field name configuration."""
        # Test default value
        self.plugin.config = {"locale": "en"}
        self.assertEqual(self.plugin.config.get("update_date_field_name", "lastmod"), "lastmod")
        
        # Test setting custom value
        self.plugin.config["update_date_field_name"] = "modified"
        self.assertEqual(self.plugin.config.get("update_date_field_name"), "modified")
            
            # Check if the custom creation date field was used instead of the standard one
            self.assertIn("created_formatted", page.meta)
            self.assertIn("created_relative", page.meta)
            self.assertIn("date_formatted", page.meta)  # For backward compatibility
            self.assertIn("date_relative", page.meta)   # For backward compatibility
            
            # Verify the date values
            created_ts = self.plugin.util.parse_date_string(page.meta["created"])
            date_ts = self.plugin.util.parse_date_string(page.meta["date"])
            
            # The 'created' field (2023-01-15) is newer than the 'date' field (2022-12-01)
            self.assertGreater(created_ts, date_ts)
            
    def test_custom_update_date_field(self):
        """Test the custom update date field name."""
        # Create a simple page mock with a custom update date field
        page = mock.MagicMock(spec=Page)
        page.meta = {
            "modified": "2023-06-20",  # Custom update date field
            "lastmod": "2023-05-15"    # Standard update date field
        }
        # Mock the file attribute separately
        page.file = mock.MagicMock()
        page.file.src_path = "test.md"
        page.file.abs_src_path = os.path.join(os.path.dirname(__file__), "test.md")
        
        # Mock the get_git_commit_timestamp to avoid git operations
        with mock.patch.object(self.plugin.util, 'get_git_commit_timestamp',
                               return_value=('abcdef', int(datetime.datetime(2020, 1, 1).timestamp()))):
            # Process the page
            self.plugin.on_page_markdown("# Test", page, {}, None)
            
            # Check if the custom update date field was used instead of the standard one
            self.assertIn("modified_formatted", page.meta)
            self.assertIn("modified_relative", page.meta)
            self.assertIn("lastmod_formatted", page.meta)  # For backward compatibility
            self.assertIn("lastmod_relative", page.meta)   # For backward compatibility
            
            # Verify the date values
            modified_ts = self.plugin.util.parse_date_string(page.meta["modified"])
            lastmod_ts = self.plugin.util.parse_date_string(page.meta["lastmod"])
            
            # The 'modified' field (2023-06-20) is newer than the 'lastmod' field (2023-05-15)
            self.assertGreater(modified_ts, lastmod_ts)


if __name__ == '__main__':
    unittest.main()
