from mkdocs_git_revision_date_localized_plugin.util import Util
import pytest
import tempfile

TEST_PARAMS = [
    (b"abc123\n", ["abc123"]),
    (b"abc123 # comments are ignored\n", ["abc123"]),
    (b"\n\n\n\n\nabc123\n\n\n\n\n", ["abc123"]),
]

@pytest.mark.parametrize("test_input,expected", TEST_PARAMS)
def test_parse_git_ignore_revs(test_input, expected):
    with tempfile.NamedTemporaryFile() as fp:
        fp.write(test_input)
        fp.flush()
        assert Util.parse_git_ignore_revs(fp.name) == expected
