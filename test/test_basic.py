import re
import yaml
from click.testing import CliRunner
from mkdocs.__main__ import build_command
from pytest import mark

def load_config(mkdocs_path):
    return yaml.load(open(mkdocs_path, 'rb'), Loader=yaml.Loader)
    
def build_docs_setup(mkdocs_path, output_path):
    runner = CliRunner()
    return runner.invoke(build_command, 
                ['--config-file', 
                 mkdocs_path, 
                 '--site-dir', 
                 str(output_path)])

def built_site_tests(path):
    # Make sure there is proper output
    index_file = path/'index.html'
    assert index_file.exists(),  f"{index_file} does not exist"
    
    # Make sure there is some output for the tag 
    contents = index_file.read_text()
    assert re.search(r"Markdown tag\:\s[\w].+", contents)
    
def test_basic_working(tmp_path):

    # No config
    result = build_docs_setup('test/basic_setup/mkdocs.yml', tmp_path)
    assert result.exit_code == 0, "'mkdocs build' command failed"
    built_site_tests(tmp_path)

    # Locales set
    result = build_docs_setup('test/basic_setup/mkdocs_plugin_locale.yml', tmp_path)
    assert result.exit_code == 0, "'mkdocs build' command failed"
    built_site_tests(tmp_path)

    result = build_docs_setup('test/basic_setup/mkdocs_locale.yml', tmp_path)
    assert result.exit_code == 0, "'mkdocs build' command failed"
    built_site_tests(tmp_path)

    # With the mkdocs-material theme:
    result = build_docs_setup('test/basic_setup/mkdocs_theme_locale.yml', tmp_path)
    assert result.exit_code == 0, "'mkdocs build' command failed"
    built_site_tests(tmp_path)
    
    # In mkdocs-material, a 'last update' should appear 
    # in Dutch because locale is set to nl
    index_file = tmp_path/'index.html'
    built_site_tests(tmp_path)
    contents = index_file.read_text()
    assert re.search(r"Letztes Update\:\s[\w].+", contents) 
    
    # Test timeago
    result = build_docs_setup('test/basic_setup/mkdocs_timeago.yml', tmp_path)
    assert result.exit_code == 0, "'mkdocs build' command failed"
    index_file = tmp_path/'index.html'
    contents = index_file.read_text()
    assert re.search("<span class='timeago'", contents) 
    