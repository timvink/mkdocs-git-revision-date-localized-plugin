import re
import yaml
import shutil
import pytest

from mkdocs_git_revision_date_localized_plugin.util import Util

from click.testing import CliRunner
from mkdocs.__main__ import build_command

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
    

def test_date_formats():
    u = Util()
    assert u._date_formats(1582397529) == {
        'date': 'February 22, 2020',
        'datetime': 'February 22, 2020 18:52:09',
        'iso_date': '2020-02-22',
        'iso_datetime': '2020-02-22 18:52:09',
        'timeago': "<span class='timeago' datetime='1582397529000' locale='en'></span>"
    }

def test_basic_locale_builds(tmp_path):
    """
    Test some different settings in mkdocs.yml
    """
    # No config
    result = build_docs_setup('tests/basic_setup/mkdocs.yml', tmp_path)
    assert result.exit_code == 0, "'mkdocs build' command failed"
    built_site_tests(tmp_path)

    # Plugin locale set
    result = build_docs_setup('tests/basic_setup/mkdocs_plugin_locale.yml', tmp_path)
    assert result.exit_code == 0, "'mkdocs build' command failed"
    built_site_tests(tmp_path)

    # Mkdocs locale set
    result = build_docs_setup('tests/basic_setup/mkdocs_locale.yml', tmp_path)
    assert result.exit_code == 0, "'mkdocs build' command failed"
    built_site_tests(tmp_path)
    
    
def test_material_theme(tmp_path):
    """
    Test correct working of mkdocs material theme
    """
    # With the mkdocs-material theme:
    result = build_docs_setup('tests/basic_setup/mkdocs_theme_locale.yml', tmp_path)
    assert result.exit_code == 0, "'mkdocs build' command failed"
    built_site_tests(tmp_path) 
    
    # In mkdocs-material, a 'last update' should appear 
    # in German because locale is set to 'de'
    index_file = tmp_path/'index.html'
    built_site_tests(tmp_path)
    contents = index_file.read_text()
    assert re.search(r"Letztes Update\:\s[\w].+", contents) 
    
    
def test_type_builds(tmp_path):
    """
    Test the different 'type' parameters
    """
    
    # type: 'timeago'
    result = build_docs_setup('tests/basic_setup/mkdocs_timeago.yml', tmp_path)
    assert result.exit_code == 0, "'mkdocs build' command failed but should have succeeded"
    index_file = tmp_path/'index.html'
    contents = index_file.read_text()
    assert re.search("<span class='timeago'", contents) 
    
    # type: 'datetime'
    result = build_docs_setup('tests/basic_setup/mkdocs_datetime.yml', tmp_path)
    assert result.exit_code == 0, "'mkdocs build' command failed but should have succeeded"
    built_site_tests(tmp_path)
    
    # unknown type
    result = build_docs_setup('tests/basic_setup/mkdocs_unknown_type.yml', tmp_path)
    assert result.exit_code == 1, "'mkdocs build' command succeeded but should have failed"

    
def test_low_fetch_depth(tmp_path):
    """
    On gitlab and github runners, a GIT might have a low fetch 
    depth, which means commits are not available. 
    This should throw informative errors.
    """
    
    pass
    
    # Test correct error messages when GIT is not available
    #target_dir = os.path.join(tmp_path, 'nogit')
    #shutil.copytree(os.path.join(os.getcwd(), 'test/basic_setup'), 
    #                target_dir)
    
    # ...
    #result = build_docs_setup(os.path.join(target_dir,'mkdocs.yml'), target_dir)

    #with pytest.warns(UserWarning):
    #    assert result.exit_code == 0, "'mkdocs build' command failed"
    