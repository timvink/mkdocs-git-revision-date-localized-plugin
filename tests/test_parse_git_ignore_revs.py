from mkdocs_git_revision_date_localized_plugin.util import Util
import pytest
import tempfile
import os

TEST_PARAMS = [
    ("abc123\n", ["abc123"]),
    ("abc123 # comments are ignored\n", ["abc123"]),
    ("\n\n\n\n\nabc123\n\n\n\n\n", ["abc123"]),
]


@pytest.mark.parametrize("test_input,expected", TEST_PARAMS)
def test_parse_git_ignore_revs(test_input, expected):
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False) as fp:
        fp.write(test_input)
        temp_file_name = fp.name
    try:
        assert Util.parse_git_ignore_revs(temp_file_name) == expected
    finally:
        os.remove(temp_file_name)
