from types import SimpleNamespace
from unittest.mock import patch

import mkdocs_git_revision_date_localized_plugin.plugin as plugin_module
from mkdocs_git_revision_date_localized_plugin.plugin import GitRevisionDateLocalizedPlugin


def test_generated_page_uses_one_timestamp_for_creation_and_last_revision():
    """A clock tick between the two reads must not make creation later than last revision."""
    plugin = GitRevisionDateLocalizedPlugin()
    page = SimpleNamespace(file=SimpleNamespace(generated_by="gen-files", src_uri="reference/api.md"))

    with patch.object(plugin_module, "time") as clock:
        clock.time.side_effect = [1700000000.9, 1700000001.1]
        _, last_revision = plugin._get_commit(page, is_first_commit=False)
        _, created = plugin._get_commit(page, is_first_commit=True)

    assert created == last_revision == 1700000000


def test_generated_page_timestamp_is_reset_on_pre_build():
    plugin = GitRevisionDateLocalizedPlugin()
    page = SimpleNamespace(file=SimpleNamespace(generated_by="gen-files", src_uri="reference/api.md"))

    with patch.object(plugin_module, "time") as clock:
        clock.time.side_effect = [1700000000.0, 1700000100.0]
        _, first_build = plugin._get_commit(page, is_first_commit=False)
        plugin.on_pre_build(config=None)
        _, second_build = plugin._get_commit(page, is_first_commit=False)

    assert (first_build, second_build) == (1700000000, 1700000100)
