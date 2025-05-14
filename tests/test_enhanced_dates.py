"""Test the enhanced date functionality."""

import os
import datetime
import unittest
from unittest import mock

from mkdocs.structure.pages import Page
from mkdocs.structure.nav import Section

from mkdocs_git_revision_date_localized_plugin.util import Util
from mkdocs_git_revision_date_localized_plugin.plugin import GitRevisionDateLocalizedPlugin


class TestEnhancedDateFunctionality(unittest.TestCase):
    """Test enhanced date processing."""

    def setUp(self):
        """Set up the test."""
        self.plugin = GitRevisionDateLocalizedPlugin()
        
        # Set plugin config
        self.plugin.config = {
            "enabled": True,
            "include_relative_dates": True,
            "date_format_in_metadata": True,
            "type": "date",
            "timezone": "UTC",
            "locale": "en"
        }
        
        # Create a mock `mkdocs` config with an empty attribute to initialize the Util class
        test_config = mock.Mock()
        test_config.config_file_path = ""
        test_config.data = {}
        
        # Initialize the util object
        self.plugin.util = Util(self.plugin.config, os.path.dirname(os.path.abspath(__file__)))
        
    def test_parse_date_string_enhanced(self):
        """Test the enhanced parse_date_string method."""
        # Test with various date formats
        now = datetime.datetime.now()
        
        # Test with datetime object
        timestamp = self.plugin.util.parse_date_string(now)
        self.assertIsInstance(timestamp, int)
        self.assertTrue(timestamp > 0)
        
        # Test with date object
        date_only = now.date()
        timestamp = self.plugin.util.parse_date_string(date_only)
        self.assertIsInstance(timestamp, int)
        self.assertTrue(timestamp > 0)
        
        # Test with ISO format string
        iso_date = "2023-05-15T10:30:00+00:00"
        timestamp = self.plugin.util.parse_date_string(iso_date)
        self.assertIsInstance(timestamp, int)
        self.assertTrue(timestamp > 0)
        
        # Test with human-readable string
        human_date = "May 15, 2023"
        timestamp = self.plugin.util.parse_date_string(human_date)
        self.assertIsInstance(timestamp, int)
        self.assertTrue(timestamp > 0)

    def test_get_relative_time_string(self):
        """Test the get_relative_time_string method."""
        from datetime import datetime, timezone, timedelta
        
        # Use fixed reference point for testing to avoid time-dependent test failures
        now = datetime(2023, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        
        # Mock datetime.now to return our fixed time
        with mock.patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = now
            
            # Patch the utility's method to use our mocked datetime
            with mock.patch.object(self.plugin.util, 'get_relative_time_string', wraps=self.plugin.util.get_relative_time_string):
                
                # Test with current time
                self.assertEqual(self.plugin.util.get_relative_time_string(now), "just now")
                
                # Test with past dates
                yesterday = now - timedelta(days=1)
                self.assertEqual(self.plugin.util.get_relative_time_string(yesterday), "yesterday")
                
                two_days_ago = now - timedelta(days=2)
                self.assertEqual(self.plugin.util.get_relative_time_string(two_days_ago), "2 days ago")
                
                one_month_ago = now - timedelta(days=35)
                self.assertEqual(self.plugin.util.get_relative_time_string(one_month_ago), "1 month ago")
                
                one_year_ago = now - timedelta(days=400)
                self.assertEqual(self.plugin.util.get_relative_time_string(one_year_ago), "1 year ago")
                
                # Test with future dates
                tomorrow = now + timedelta(days=1)
                self.assertEqual(self.plugin.util.get_relative_time_string(tomorrow), "tomorrow")
                
                future_day = now + timedelta(days=5)
                self.assertEqual(self.plugin.util.get_relative_time_string(future_day), "in 5 days")
                
                future_month = now + timedelta(days=40)
                self.assertEqual(self.plugin.util.get_relative_time_string(future_month), "in 1 month")
                
                future_year = now + timedelta(days=400)
                self.assertEqual(self.plugin.util.get_relative_time_string(future_year), "in 1 year")

    def test_date_parsing_and_relative_time(self):
        """Test date parsing and relative time functionality."""
        # Test parse_date_string with different formats
        date_str = "2023-06-15"
        ts = self.plugin.util.parse_date_string(date_str)
        self.assertTrue(ts > 0, "Should parse date string")
        
        date_obj = datetime.datetime(2022, 1, 1)
        ts = self.plugin.util.parse_date_string(date_obj)
        self.assertTrue(ts > 0, "Should parse datetime object")
        
        human_date = "December 31, 2024"
        ts = self.plugin.util.parse_date_string(human_date)
        self.assertTrue(ts > 0, "Should parse human-readable date string")
        
        # Test relative time string generation
        rel_time = self.plugin.util.get_relative_time_string(ts)
        self.assertTrue(isinstance(rel_time, str), "Should generate relative time string")
        self.assertTrue(len(rel_time) > 0, "Relative time string should not be empty")


if __name__ == '__main__':
    unittest.main()
