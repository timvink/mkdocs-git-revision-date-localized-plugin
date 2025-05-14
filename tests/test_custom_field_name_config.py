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
    
    def test_date_parsing_works_for_custom_field_formats(self):
        """Test date parsing with different formats."""
        # Test parsing dates in different formats
        formats = [
            "2023-01-15",                  # ISO date format
            "2023-01-15T12:30:45+00:00",   # ISO datetime format
            "January 15, 2023",            # Human-readable format
            "15 Jan 2023",                 # Short format
            datetime.datetime(2023, 1, 15),  # Python datetime object
            datetime.date(2023, 1, 15),    # Python date object
        ]
        
        for date_value in formats:
            timestamp = self.plugin.util.parse_date_string(date_value)
            self.assertGreater(timestamp, 0, f"Failed to parse date: {date_value}")
            
            # Convert timestamp back to datetime for verification
            dt = datetime.datetime.fromtimestamp(timestamp)
            self.assertEqual(dt.year, 2023)
            self.assertEqual(dt.month, 1)
            self.assertEqual(dt.day, 15)


if __name__ == '__main__':
    unittest.main()
