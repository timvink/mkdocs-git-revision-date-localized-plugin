"""
Tests running builds on different fresh mkdocs projects

Note that pytest offers a `tmp_path` fixture that we use here.
You can reproduce locally with:
>>> import tempfile
>>> from pathlib import Path
>>> tmp_path = Path(tempfile.gettempdir()) / 'pytest-testname'
>>> os.mkdir(tmp_path)
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard lib
import logging
import os
import re
import shutil

# MkDocs
from mkdocs.__main__ import build_command
from mkdocs.config import load_config

# other 3rd party
import git
import pytest
from click.testing import CliRunner

# package module
from mkdocs_git_revision_date_localized_plugin.util import Util

# #############################################################################
# ######## Globals #################
# ##################################

PLUGIN_NAME = "git-revision-date-localized"

# custom log level to get plugin info messages
logging.basicConfig(level=logging.INFO)


# #############################################################################
# ########## Helpers ###############
# ##################################
def get_plugin_config_from_mkdocs(mkdocs_path) -> dict:
    # instanciate plugin
    cfg_mkdocs = load_config(mkdocs_path)

    plugins = cfg_mkdocs.get("plugins")
    plugin_loaded = plugins.get(PLUGIN_NAME)

    cfg = plugin_loaded.on_config(cfg_mkdocs)
    logging.info("Fixture configuration loaded: " + str(cfg))

    assert (
        plugin_loaded.config.get("locale") is not None
    ), "Locale should never be None after plugin is loaded"

    logging.info(
        "Locale '%s' determined from %s"
        % (plugin_loaded.config.get("locale"), mkdocs_path)
    )
    return plugin_loaded.config


def setup_clean_mkdocs_folder(mkdocs_yml_path, output_path):
    """
    Sets up a clean mkdocs directory

    outputpath/testproject
    ├── docs/
    └── mkdocs.yml

    Args:
        mkdocs_yml_path (Path): Path of mkdocs.yml file to use
        output_path (Path): Path of folder in which to create mkdocs project

    Returns:
        testproject_path (Path): Path to test project
    """

    testproject_path = output_path / "testproject"

    # Create empty 'testproject' folder
    if os.path.exists(testproject_path):
        logging.warning(
            """This command does not work on windows.
        Refactor your test to use setup_clean_mkdocs_folder() only once"""
        )
        shutil.rmtree(testproject_path)

    # Copy correct mkdocs.yml file and our test 'docs/'
    shutil.copytree("tests/basic_setup/docs", testproject_path / "docs")
    shutil.copyfile(mkdocs_yml_path, testproject_path / "mkdocs.yml")

    return testproject_path


def setup_commit_history(testproject_path):
    """
    Initializes and creates a git commit history
    in a new mkdocs testproject.

    We commit the pages one by one in order
    to create some git depth.

    Args:
        testproject_path (Path): Path to test project

    Returns:
        repo (repo): git.Repo object
    """
    assert not os.path.exists(testproject_path / ".git")

    repo = git.Repo.init(testproject_path, bare=False)
    author = "Test Person <testtest@gmail.com>"

    # Change the working directory
    cwd = os.getcwd()
    os.chdir(testproject_path)

    try:
        repo.git.add("mkdocs.yml")
        repo.git.commit(message="add mkdocs", author=author)

        repo.git.add("docs/first_page.md")
        repo.git.commit(message="first page", author=author)
        file_name = os.path.join(testproject_path, "docs/first_page.md")
        with open(file_name, "w+") as the_file:
            the_file.write("Hello\n")
        repo.git.add("docs/first_page.md")
        repo.git.commit(message="first page update 1", author=author)
        with open(file_name, "w") as the_file:
            the_file.write("# First Test Page Edited\n\nSome Lorem text")
        repo.git.add("docs/first_page.md")
        repo.git.commit(message="first page update 2", author=author)

        repo.git.add("docs/second_page.md")
        repo.git.commit(message="second page", author=author)
        repo.git.add("docs/index.md")
        repo.git.commit(message="homepage", author=author)
        repo.git.add("docs/page_with_tag.md")
        repo.git.commit(message="homepage", author=author)
        os.chdir(cwd)
    except:
        os.chdir(cwd)
        raise

    return repo


def build_docs_setup(testproject_path):
    """
    Runs the `mkdocs build` command

    Args:
        testproject_path (Path): Path to test project

    Returns:
        command: Object with results of command
    """

    # TODO: Try specifying path in CliRunner, this function could be one-liner
    cwd = os.getcwd()
    os.chdir(testproject_path)

    try:
        runner = CliRunner()
        run = runner.invoke(build_command)
        os.chdir(cwd)
        return run
    except:
        os.chdir(cwd)
        raise


def validate_build(testproject_path, plugin_config: dict):
    """
    Validates a build from a testproject

    Args:
        testproject_path (Path): Path to test project
    """
    assert os.path.exists(testproject_path / "site")

    # Make sure index file exists
    index_file = testproject_path / "site/index.html"
    assert index_file.exists(), f"{index_file} does not exist"

    # Make sure with markdown tag has valid
    # git revision date tag
    page_with_tag = testproject_path / "site/page_with_tag/index.html"
    contents = page_with_tag.read_text(encoding="utf8")
    assert re.search(r"Markdown tag\:\s[<span>|\w].+", contents)

    repo = Util(testproject_path)
    date_formats = repo.get_revision_date_for_file(
        path=testproject_path / "docs/page_with_tag.md",
        locale=plugin_config.get("locale"),
        fallback_to_build_date=plugin_config.get("fallback_to_build_date"),
    )

    searches = [re.search(x, contents) for x in date_formats.values()]
    assert any(searches), "No correct date formats output was found"


def validate_mkdocs_file(temp_path: str, mkdocs_yml_file: str):
    """
    Creates a clean mkdocs project
    for a mkdocs YML file, builds and validates it.

    Args:
        temp_path (PosixPath): Path to temporary folder
        mkdocs_yml_file (PosixPath): Path to mkdocs.yml file
    """
    testproject_path = setup_clean_mkdocs_folder(
        mkdocs_yml_path=mkdocs_yml_file, output_path=temp_path
    )
    setup_commit_history(testproject_path)
    result = build_docs_setup(testproject_path)
    assert result.exit_code == 0, "'mkdocs build' command failed"

    # validate build with locale retrieved from mkdocs config file
    validate_build(
        testproject_path, plugin_config=get_plugin_config_from_mkdocs(mkdocs_yml_file)
    )

    return testproject_path


# #############################################################################
# ########### Tests ################
# ##################################
def test_date_formats():
    u = Util()
    assert u._date_formats(1582397529) == {
        "date": "February 22, 2020",
        "datetime": "February 22, 2020 18:52:09",
        "iso_date": "2020-02-22",
        "iso_datetime": "2020-02-22 18:52:09",
        "timeago": "<span class='timeago' datetime='1582397529000' locale='en'></span>",
    }


def test_missing_git_repo(tmp_path):
    """
    When there is no GIT repo, this should fail
    """
    testproject_path = setup_clean_mkdocs_folder(
        mkdocs_yml_path="tests/basic_setup/mkdocs.yml", output_path=tmp_path
    )

    result = build_docs_setup(testproject_path)
    assert (
        result.exit_code == 1
    ), "'mkdocs build' command succeeded while there is no GIT repo"


def test_build_no_options(tmp_path):
    # Enable plugin with no extra options set
    validate_mkdocs_file(tmp_path, "tests/basic_setup/mkdocs.yml")


def test_build_locale_plugin(tmp_path):
    # Enable plugin with plugin locale set to 'nl'
    validate_mkdocs_file(tmp_path, "tests/basic_setup/mkdocs_plugin_locale.yml")


def test_build_locale_mkdocs(tmp_path):
    # Enable plugin with mkdocs locale set to 'fr'
    validate_mkdocs_file(tmp_path, "tests/basic_setup/mkdocs_locale.yml")


def test_material_theme(tmp_path):
    """
    When using mkdocs-material theme, test correct working
    """
    # theme set to 'material' with 'language' set to 'de'
    testproject_path = validate_mkdocs_file(
        tmp_path, "tests/basic_setup/mkdocs_theme_locale.yml"
    )

    # In mkdocs-material, a 'last update' should appear
    # in German because locale is set to 'de'
    index_file = testproject_path / "site/index.html"
    contents = index_file.read_text(encoding="utf8")
    assert re.search(r"Letztes Update\:\s[\w].+", contents)


def test_material_theme_no_locale(tmp_path):
    """
    When using mkdocs-material theme, test correct working
    """
    # theme set to 'material' with 'language' set to 'de'
    testproject_path = validate_mkdocs_file(
        tmp_path, "tests/basic_setup/mkdocs_theme_no_locale.yml"
    )

    # In mkdocs-material, a 'last update' should appear
    # in German because locale is set to 'de'
    index_file = testproject_path / "site/index.html"
    contents = index_file.read_text(encoding="utf8")
    assert re.search(r"Last update\:\s[\w].+", contents)

def test_type_timeago(tmp_path):
    # type: 'timeago'
    testproject_path = validate_mkdocs_file(
        tmp_path, "tests/basic_setup/mkdocs_timeago.yml"
    )


def test_type_datetime(tmp_path):
    # type: 'datetime'
    testproject_path = validate_mkdocs_file(
        tmp_path, "tests/basic_setup/mkdocs_datetime.yml"
    )


def test_type_unknown(tmp_path):
    with pytest.raises(AssertionError):
        testproject_path = validate_mkdocs_file(
            tmp_path, "tests/basic_setup/mkdocs_unknown_type.yml"
        )


def test_low_fetch_depth(tmp_path, caplog):
    """
    On gitlab and github runners, a GIT might have a low fetch
    depth, which means commits are not available.
    This should throw informative errors.
    """

    testproject_path = setup_clean_mkdocs_folder(
        "tests/basic_setup/mkdocs.yml", tmp_path
    )
    repo = setup_commit_history(testproject_path)

    # Create a second, clean folder to clone to
    cloned_folder = tmp_path.parent / "clonedrepo"
    if os.path.exists(cloned_folder):
        shutil.rmtree(cloned_folder)
    os.mkdir(cloned_folder)

    # Clone the local repo with fetch depth of 1
    repo = git.Repo.init(cloned_folder, bare=False)
    origin = repo.create_remote("origin", testproject_path)
    origin.fetch(depth=1, prune=True)
    repo.create_head(
        "master", origin.refs.master
    )  # create local branch "master" from remote "master"
    repo.heads.master.set_tracking_branch(
        origin.refs.master
    )  # set local "master" to track remote "master
    repo.heads.master.checkout()  # checkout local "master" to working tree

    # should not raise warning
    result = build_docs_setup(cloned_folder)
    assert result.exit_code == 0

    # should raise warning
    os.environ["GITLAB_CI"] = "1"
    result = build_docs_setup(cloned_folder)
    assert result.exit_code == 0
    assert "Running on a gitlab runner" in caplog.text

    del os.environ["GITLAB_CI"]
    os.environ["GITHUB_ACTIONS"] = "1"
    result = build_docs_setup(cloned_folder)
    assert result.exit_code == 0
    assert "Running on github actions might" in caplog.text


# TODO: Test correct error messages when GIT is not available
