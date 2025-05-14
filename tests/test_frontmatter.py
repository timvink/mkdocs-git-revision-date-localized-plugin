import os
import pytest
from datetime import datetime
from mkdocs_git_revision_date_localized_plugin.util import Util

def test_parse_date_string():
    """Test that parse_date_string correctly converts date strings to timestamps."""
    config = {"locale": "en", "enable_creation_date": True}
    util = Util(config=config, mkdocs_dir="/tmp")
    
    # Test ISO format date string
    date_str = "2023-01-15T12:00:00+02:00"
    ts = util.parse_date_string(date_str)
    # Convert back to datetime for easier assertion
    dt = datetime.fromtimestamp(ts)
    assert dt.year == 2023
    assert dt.month == 1
    assert dt.day == 15
    # Don't test the hour as it varies with local timezone
    
    # Test a common date format
    date_str = "2023-01-15"
    ts = util.parse_date_string(date_str)
    dt = datetime.fromtimestamp(ts)
    assert dt.year == 2023
    assert dt.month == 1
    assert dt.day == 15
    
    # Test invalid date string
    date_str = "not a date"
    ts = util.parse_date_string(date_str)
    assert ts == 0  # Should return 0 for invalid dates
