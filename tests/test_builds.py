"""
Tests running builds on different fresh mkdocs projects.

Note that pytest offers a `tmp_path` fixture that we use here.
You can reproduce locally with:
>>> import tempfile
>>> from pathlib import Path
>>> tmp_path = Path(tempfile.gettempdir()) / 'pytest-testname'
>>> os.mkdir(tmp_path)

"""

# standard lib
import logging
import os
import sys
import re
import shutil
from contextlib import contextmanager
from pathlib import Path

# MkDocs
from mkdocs.__main__ import build_command
from mkdocs.config import load_config

# other 3rd party
import git
import pytest
from click.testing import CliRunner

# package module
from mkdocs_git_revision_date_localized_plugin.util import Util
from mkdocs_git_revision_date_localized_plugin.ci import commit_count
from mkdocs_git_revision_date_localized_plugin.dates import get_date_formats

# ##################################
# ######## Globals #################
# ##################################

# custom log level to get plugin info messages
logging.basicConfig(level=logging.INFO)


# ##################################
# ########## Helpers ###############
# ##################################


@contextmanager
def working_directory(path):
    """
    Temporarily change working directory.
    A context manager which changes the working directory to the given
    path, and then changes it back to its previous value on exit.
    Usage:
    ```python
    # Do something in original directory
    with working_directory('/my/new/path'):
        # Do something in new directory
    # Back to old directory
    ```
    """
    prev_cwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_cwd)


def get_plugin_config_from_mkdocs(mkdocs_path) -> dict:
    # instanciate plugin
    cfg_mkdocs = load_config(mkdocs_path)

    plugins = cfg_mkdocs.get("plugins")
    plugin_loaded = plugins.get("git-revision-date-localized")

    cfg = plugin_loaded.on_config(cfg_mkdocs)
    logging.info("Fixture configuration loaded: " + str(cfg))

    if plugin_loaded.config.get("enabled"):
        assert plugin_loaded.config.get("locale") is not None, "Locale should never be None after plugin is loaded"

        logging.info("Locale '%s' determined from %s" % (plugin_loaded.config.get("locale"), mkdocs_path))
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
    if os.path.exists(str(testproject_path)):
        logging.warning(
            """This command does not work on windows.
        Refactor your test to use setup_clean_mkdocs_folder() only once"""
        )
        shutil.rmtree(str(testproject_path))

    # shutil.copytree(str(Path(mkdocs_yml_path).parent), testproject_path)

    # Copy correct mkdocs.yml file and our test 'docs/'
    if "i18n" in mkdocs_yml_path:
        shutil.copytree("tests/fixtures/i18n/docs", str(testproject_path / "docs"))
    else:
        shutil.copytree("tests/fixtures/basic_project/docs", str(testproject_path / "docs"))

    shutil.copyfile("tests/fixtures/basic_project/gen_files.py", str(testproject_path / "gen_files.py"))
    shutil.copyfile(mkdocs_yml_path, str(testproject_path / "mkdocs.yml"))


    if "gen-files" in mkdocs_yml_path:
        shutil.copyfile(str(Path(mkdocs_yml_path).parent / "gen_pages.py"), str(testproject_path / "gen_pages.py"))

    # Copy monorepo files
    if "monorepo" in mkdocs_yml_path:
        shutil.copytree("tests/fixtures/monorepo", str(testproject_path), dirs_exist_ok=True)

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
    assert not (testproject_path / ".git").exists()

    repo = git.Repo.init(testproject_path, bare=False)
    repo.git.checkout("-b", "master")
    author = "Test Person <testtest@gmail.com>"

    with working_directory(testproject_path):
        # page_with_tags contains tags we replace and test
        if os.path.exists("docs/page_with_tag.md"):
            repo.git.add("docs/page_with_tag.md")
            repo.git.commit(
                message="add homepage", author=author, date="1500854705"
            )  # Mon Jul 24 2017 00:05:05 GMT+0000

            file_name = testproject_path / "docs/page_with_tag.md"
            with open(file_name, "a") as the_file:
                the_file.write("test\n")
            repo.git.add("docs/page_with_tag.md")
            repo.git.commit(
                message="update homepage #1", author=author, date="1525475836"
            )  # 	Fri May 04 2018 23:17:16 GMT+0000

            with open(file_name, "a") as the_file:
                the_file.write("awa\n")
            repo.git.add("docs/page_with_tag.md")
            repo.git.commit(
                message="update homepage #2", author=author, date="1642911026"
            )  # 	Sun Jan 23 2022 04:10:26 GMT+0000

        if os.path.exists("docs/page_with_renamed.md"):
            bf_file_name = testproject_path / "docs/page_with_renamed.md"
            af_file_name = testproject_path / "docs/subfolder/page_with_renamed.md"
            # Since git.mv would actually remove the file, move page_with_renamed.md back to docs if it has been moved
            if af_file_name.exists():
                os.replace(af_file_name, bf_file_name)
            repo.git.add("docs/page_with_renamed.md")
            repo.git.commit(
                message="page_with_renamed.md before renamed", author=author, date="1655229469"
            )  #  Tue Jun 14 2022 17:57:49 GMT+0000
            repo.git.mv("docs/page_with_renamed.md", "docs/subfolder/page_with_renamed.md")
            repo.git.commit(
                message="page_with_renamed.md after renamed", author=author, date="1655229515"
            )  #  Tue Jun 14 2022 17:58:35 GMT+0000

        if os.path.exists("docs/first_page.md"):
            repo.git.add("docs/first_page.md")
            repo.git.commit(message="first page", author=author, date="1500854705")  # Mon Jul 24 2017 00:05:05 GMT+0000
            file_name = testproject_path / "docs/first_page.md"
            with open(file_name, "w+") as the_file:
                the_file.write("Hello\n")
            repo.git.add("docs/first_page.md")
            repo.git.commit(
                message="first page update 1", author=author, date="1519964705"
            )  # 	Fri Mar 02 2018 04:25:05 GMT+0000
            with open(file_name, "w") as the_file:
                the_file.write("# First Test Page Edited\n\nSome Lorem text")
            repo.git.add("docs/first_page.md")
            repo.git.commit(
                message="first page update 2", author=author, date="1643911026"
            )  # 	Thu Feb 03 2022 17:57:06 GMT+0000

        repo.git.add("mkdocs.yml")
        repo.git.commit(
            message="add mkdocs", author=author, date="1500854705 -0700"
        )  # Mon Jul 24 2017 00:05:05 GMT+0000

        if Path("docs/second_page.md").exists():
            repo.git.add("docs/second_page.md")
            repo.git.commit(
                message="second page", author=author, date="1643911026"
            )  # 	Thu Feb 03 2022 17:57:06 GMT+0000

        repo.git.add("docs/index.md")
        repo.git.commit(message="homepage", author=author, date="1643911026")  # 	Thu Feb 03 2022 17:57:06 GMT+0000

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
    os.chdir(str(testproject_path))

    try:
        runner = CliRunner()
        run = runner.invoke(build_command)
        os.chdir(cwd)
        return run
    except:
        os.chdir(cwd)
        raise


def validate_build(testproject_path, plugin_config: dict = {}):
    """
    Validates a build from a testproject

    Args:
        testproject_path (Path): Path to test project
    """
    assert os.path.exists(str(testproject_path / "site"))

    # Make sure index file exists
    index_file = testproject_path / "site/index.html"
    assert index_file.exists(), "%s does not exist" % index_file

    # Make sure with markdown tag has valid
    # git revision date tag
    if not plugin_config.get("enabled"):
        return

    page_with_tag = testproject_path / "site/page_with_tag/index.html"
    contents = page_with_tag.read_text(encoding="utf8")
    assert re.search(r"renders as\:\s[<span>|\w].+", contents)

    repo = Util(config=plugin_config, mkdocs_dir=testproject_path)
    commit_hash, commit_timestamp = repo.get_git_commit_timestamp(
        path=str(testproject_path / "docs/page_with_tag.md"),
        is_first_commit=False,
    )
    date_formats = repo.get_date_formats_for_timestamp(
        commit_timestamp,
        locale=plugin_config["locale"],
        add_spans=True,
    )

    searches = [x in contents for x in date_formats.values()]
    assert any(searches), "No correct revision date formats output was found"

    if plugin_config.get("enable_creation_date"):
        commit_hash, commit_timestamp = repo.get_git_commit_timestamp(
            path=str(testproject_path / "docs/page_with_tag.md"),
            is_first_commit=True,
        )
        assert commit_timestamp == 1500854705
        date_formats = repo.get_date_formats_for_timestamp(
            commit_timestamp=commit_timestamp,
            locale=plugin_config["locale"],
            add_spans=True,
        )

        searches = [x in contents for x in date_formats.values()]
        assert any(searches), "No correct creation date formats output was found"

        if os.path.exists(str(testproject_path / "docs/subfolder/page_with_renamed.md")):
            commit_hash, commit_timestamp = repo.get_git_commit_timestamp(
                path=str(testproject_path / "docs/subfolder/page_with_renamed.md"), is_first_commit=True
            )
            assert commit_timestamp == 1655229469


def validate_mkdocs_file(temp_path: str, mkdocs_yml_file: str):
    """
    Creates a clean mkdocs project
    for a mkdocs YML file, builds and validates it.

    Args:
        temp_path (PosixPath): Path to temporary folder
        mkdocs_yml_file (PosixPath): Path to mkdocs.yml file
    """
    testproject_path = setup_clean_mkdocs_folder(mkdocs_yml_path=mkdocs_yml_file, output_path=temp_path)
    setup_commit_history(testproject_path)
    result = build_docs_setup(testproject_path)
    assert result.exit_code == 0, f"'mkdocs build' command failed with output:\n{result.stdout}"

    # validate build with locale retrieved from mkdocs config file
    validate_build(testproject_path, plugin_config=get_plugin_config_from_mkdocs(mkdocs_yml_file))

    return testproject_path


MKDOCS_FILES = [
    "basic_project/mkdocs_creation_date.yml",
    "basic_project/mkdocs_custom_type.yml",
    "basic_project/mkdocs_datetime.yml",
    "basic_project/mkdocs_exclude.yml",
    "basic_project/mkdocs_fallback_to_build_date.yml",
    "basic_project/mkdocs_locale.yml",
    "basic_project/mkdocs_meta.yml",
    "basic_project/mkdocs_no_parallel.yml",
    "basic_project/mkdocs_plugin_locale.yml",
    "basic_project/mkdocs.yml",
    "basic_project/mkdocs_theme_timeago_locale.yml",
    "basic_project/mkdocs_theme_language.yml",
    "basic_project/mkdocs_theme_locale_and_language.yml",
    "basic_project/mkdocs_theme_locale_disabled.yml",
    "basic_project/mkdocs_theme_timeago.yml",
    "basic_project/mkdocs_theme_locale.yml",
    "basic_project/mkdocs_theme_no_locale.yml",
    "basic_project/mkdocs_theme_timeago_override.yml",
    "basic_project/mkdocs_theme_timeago_instant.yml",
    "basic_project/mkdocs_timeago_locale.yml",
    "basic_project/mkdocs_timeago.yml",
    "basic_project/mkdocs_with_override.yml",
    "techdocs-core/mkdocs.yml",
    # 'i18n/mkdocs.yml'
]

INVALID_MKDOCS_FILES = [
    ("basic_project/mkdocs_unknown_type.yml", "AssertionError"),
    ("i18n/mkdocs_wrong_order.yml", "should be defined after the i18n plugin in your mkdocs.yml"),
]


# ##################################
# ########### Tests ################
# ##################################


@pytest.mark.parametrize("mkdocs_file", MKDOCS_FILES, ids=lambda x: f"mkdocs file: {x}")
def test_tags_are_replaced(tmp_path, mkdocs_file):
    """
    Make sure the {{ }} tags are replaced properly.
    """
    if sys.platform.startswith("win") and ("monorepo" in mkdocs_file or "techdocs" in mkdocs_file):
        pytest.skip("monorepo plugin windows issue (even without this plugin)")
    testproject_path = setup_clean_mkdocs_folder(mkdocs_yml_path=f"tests/fixtures/{mkdocs_file}", output_path=tmp_path)
    setup_commit_history(testproject_path)
    result = build_docs_setup(testproject_path)
    assert result.exit_code == 0, "'mkdocs build' command failed"

    plugin_config = get_plugin_config_from_mkdocs(str(testproject_path / "mkdocs.yml"))
    tags_file = testproject_path / "site/page_with_tag/index.html"
    contents = tags_file.read_text(encoding="utf8")

    # validate the build
    validate_build(testproject_path, plugin_config=plugin_config)

    if plugin_config.get("enabled") == False:
        return True

    if plugin_config.get("type") == "timeago":
        pytest.skip("Not necessary to test the JS library")

    # Make sure count_commits() works
    # We created 11 commits in setup_commit_history()
    with working_directory(testproject_path):
        u = Util(config={}, mkdocs_dir=os.getcwd())
        assert commit_count(u._get_repo("docs/page_with_tag.md")) == 11

    # the revision date was in 'setup_commit_history' was set to 1642911026 (Sun Jan 23 2022 04:10:26 GMT+0000)
    # Assert {{ git_revision_date_localized }} is replaced
    date_formats_revision_date = get_date_formats(
        1642911026,
        locale=plugin_config.get("locale"),
        time_zone=plugin_config.get("timezone"),
        custom_format=plugin_config.get("custom_format"),
    )
    for k, v in date_formats_revision_date.items():
        assert v is not None

    date = date_formats_revision_date.get(plugin_config.get("type"))
    assert re.search(rf"{date}\<\/span.+", contents)

    # The last site revision was set in setup_commit_history to 1643911026 (Thu Feb 03 2022 17:57:06 GMT+0000)
    # Assert {{ git_site_revision_date_localized }} is replaced
    date_formats_revision_date = get_date_formats(
        1643911026,
        locale=plugin_config.get("locale"),
        time_zone=plugin_config.get("timezone"),
        custom_format=plugin_config.get("custom_format"),
    )
    for k, v in date_formats_revision_date.items():
        assert v is not None
    date = date_formats_revision_date.get(plugin_config.get("type"))
    assert re.search(rf"{date}\<\/span.+", contents)

    # Note {{ git_creation_date_localized }} is only replaced when configured in the config
    if plugin_config.get("enable_creation_date"):
        # The creation of page_with_tag.md was set in setup_commit_history to 1500854705 ( Mon Jul 24 2017 00:05:05 GMT+0000 )
        date_formats_revision_date = get_date_formats(
            1500854705,
            locale=plugin_config.get("locale"),
            time_zone=plugin_config.get("timezone"),
            custom_format=plugin_config.get("custom_format"),
        )
        for k, v in date_formats_revision_date.items():
            assert v is not None
        date = date_formats_revision_date.get(plugin_config.get("type"))
        assert re.search(rf"{date}\<\/span.+", contents)


def test_git_not_available(tmp_path, recwarn):
    """
    When there is no GIT repo, this should fail
    """

    testproject_path = setup_clean_mkdocs_folder("tests/fixtures/basic_project/mkdocs.yml", tmp_path)
    result = build_docs_setup(testproject_path)
    assert result.exit_code == 1, "'mkdocs build' command succeeded while there is no GIT repo"

    # assert there's a no error when fallback to build date is set to true
    testproject_path = setup_clean_mkdocs_folder(
        "tests/fixtures/basic_project/mkdocs_fallback_to_build_date.yml", tmp_path
    )
    result = build_docs_setup(testproject_path)
    assert result.exit_code == 0


def test_build_material_theme(tmp_path):
    """
    When using mkdocs-material theme, test correct working
    """
    # theme set to 'material' with 'language' set to 'de'
    testproject_path = validate_mkdocs_file(tmp_path, "tests/fixtures/basic_project/mkdocs_theme_language.yml")

    # In mkdocs-material, a 'last update' should appear
    # in German because locale is set to 'de'
    index_file = testproject_path / "site/index.html"
    contents = index_file.read_text(encoding="utf8")
    assert re.search(r"Letztes Update", contents)


def test_material_theme_locale(tmp_path):
    """
    When using mkdocs-material theme, test correct working
    """
    # theme set to 'material' with 'locale' set to 'de'
    testproject_path = validate_mkdocs_file(tmp_path, "tests/fixtures/basic_project/mkdocs_theme_locale.yml")

    # In mkdocs-material, a 'last update' should appear
    # in english instead of German because you should use 'language' and not locale.
    # The date will be in german though
    index_file = testproject_path / "site/index.html"
    contents = index_file.read_text(encoding="utf8")
    assert re.search(r"Last update", contents)


def test_material_theme_locale_disabled(tmp_path):
    """
    When using mkdocs-material theme, test correct working
    """
    # theme set to 'material' with 'locale' set to 'de'
    testproject_path = validate_mkdocs_file(tmp_path, "tests/fixtures/basic_project/mkdocs_theme_locale_disabled.yml")

    # In mkdocs-material, a 'last update' should appear
    # in english instead of German because you should use 'language' and not locale.
    # The date will be in german though
    index_file = testproject_path / "site/index.html"
    contents = index_file.read_text(encoding="utf8")
    assert re.search(r"Last update", contents) is None


def test_material_theme_no_locale(tmp_path):
    """
    When using mkdocs-material theme, test correct working
    """
    # theme set to 'material' with 'language' set to 'de'
    testproject_path = validate_mkdocs_file(tmp_path, "tests/fixtures/basic_project/mkdocs_theme_no_locale.yml")

    # In mkdocs-material, a 'last update' should appear
    # in english because default locale is set to 'en'
    index_file = testproject_path / "site/index.html"
    contents = index_file.read_text(encoding="utf8")
    assert re.search(r"Last update", contents)


@pytest.mark.parametrize("mkdocs_file, error", INVALID_MKDOCS_FILES)
def test_type_unknown(mkdocs_file, error, tmp_path):
    """
    Make sure invalid mkdocs.yml specification raise the correct errors.
    """
    testproject_path = setup_clean_mkdocs_folder(
        mkdocs_yml_path=f"tests/fixtures/{mkdocs_file}",  # mkdocs_file, # tmp_path, ,
        output_path=tmp_path,
    )
    # Setup git commit history
    assert not os.path.exists(str(testproject_path / ".git"))
    testproject_path = str(testproject_path)

    repo = git.Repo.init(testproject_path, bare=False)
    author = "Test Person <testtest@gmail.com>"

    with working_directory(testproject_path):
        # page_with_tags contains tags we replace and test
        repo.git.add(".")
        repo.git.commit(message="add all", author=author, date="1500854705")  # Mon Jul 24 2017 00:05:05 GMT+0000

    result = build_docs_setup(testproject_path)
    assert result.exit_code == 1

    assert error in result.stdout or error in str(result.exc_info[0])


def test_exclude_pages(tmp_path):
    """
    When using mkdocs-material theme, test correct working
    """
    # theme set to 'material' with 'locale' set to 'de'
    testproject_path = validate_mkdocs_file(tmp_path, "tests/fixtures/basic_project/mkdocs_exclude.yml")

    # Make sure revision date does not exist in excluded pages
    first_page = testproject_path / "site/first_page/index.html"
    contents = first_page.read_text(encoding="utf8")
    assert not re.search(r"Last update\:\s[<span class].+", contents)

    sub_page = testproject_path / "site/subfolder/page_in_subfolder/index.html"
    contents = sub_page.read_text(encoding="utf8")
    assert not re.search(r"Last update\:\s[<span class].+", contents)


def test_git_in_docs_dir(tmp_path):
    """
    In https://github.com/timvink/mkdocs-git-revision-date-localized-plugin/pull/31
    a use case is described where `.git` dir lives in `docs/`
    """

    testproject_path = setup_clean_mkdocs_folder("tests/fixtures/basic_project/mkdocs.yml", tmp_path)

    # Setup git repo in the 'docs' dir
    testproject_docs = str(testproject_path / "docs")
    repo = git.Repo.init(testproject_docs, bare=False)
    author = "Test Person <testtest@gmail.com>"

    # Change the working directory
    cwd = os.getcwd()
    os.chdir(testproject_docs)

    try:
        repo.git.add("page_with_tag.md")
        repo.git.commit(message="homepage", author=author)
        os.chdir(cwd)
    except:
        os.chdir(cwd)
        raise

    # Build project
    result = build_docs_setup(testproject_path)
    assert result.exit_code == 0
    validate_build(
        testproject_path,
        plugin_config=get_plugin_config_from_mkdocs(str(testproject_path / "mkdocs.yml")),
    )


def test_low_fetch_depth(tmp_path, caplog):
    """
    On gitlab and github runners, a GIT might have a low fetch
    depth, which means commits are not available.
    This should throw informative errors.
    """

    testproject_path = setup_clean_mkdocs_folder("tests/fixtures/basic_project/mkdocs.yml", tmp_path)
    repo = setup_commit_history(testproject_path)

    # Create a second, clean folder to clone to
    cloned_folder = str(tmp_path.parent / "clonedrepo")
    if os.path.exists(cloned_folder):
        shutil.rmtree(cloned_folder)
    # os.mkdir(cloned_folder)

    # Clone the local repo with fetch depth of 1
    repo = git.Repo.init(cloned_folder, bare=False)
    try:
        repo.heads.main.rename("master", force=True)
    except:
        pass
    origin = repo.create_remote("origin", str(testproject_path))
    origin.fetch(depth=1, prune=True)
    repo.create_head("master", origin.refs.master)  # create local branch "master" from remote "master"
    repo.heads.master.set_tracking_branch(origin.refs.master)  # set local "master" to track remote "master
    repo.heads.master.checkout()  # checkout local "master" to working tree

    # should not raise warning
    result = build_docs_setup(cloned_folder)
    assert result.exit_code == 0

    # should raise warning
    os.environ["GITLAB_CI"] = "1"
    result = build_docs_setup(cloned_folder)
    assert result.exit_code == 0
    assert "Running on a GitLab runner" in caplog.text

    del os.environ["GITLAB_CI"]
    os.environ["GITHUB_ACTIONS"] = "1"
    result = build_docs_setup(cloned_folder)
    assert result.exit_code == 0
    assert "Running on GitHub Actions might" in caplog.text


@pytest.mark.skip(reason="waiting for PR from mkdocs-genfiles-plugin to be merged first")
def test_mkdocs_genfiles_plugin(tmp_path):
    """
    Make sure the mkdocs-gen-files plugin works correctly.
    """
    testproject_path = setup_clean_mkdocs_folder(
        mkdocs_yml_path=f"tests/fixtures/mkdocs-gen-files/mkdocs.yml", output_path=tmp_path
    )
    setup_commit_history(testproject_path)
    result = build_docs_setup(testproject_path)
    assert result.exit_code == 0, f"'mkdocs build' command failed with {result.stdout}"

    # validate the build
    plugin_config = get_plugin_config_from_mkdocs(str(testproject_path / "mkdocs.yml"))
    validate_build(testproject_path, plugin_config)


def test_ignored_commits(tmp_path):
    testproject_path = setup_clean_mkdocs_folder("tests/fixtures/basic_project/mkdocs_ignored_commits.yml", tmp_path)
    repo = setup_commit_history(testproject_path)

    # First test that the middle commit doesn't show up by default
    # January 23, 2022 is the date of the most recent commit
    with open(str(testproject_path / "ignored-commits.txt"), "wt", encoding="utf-8") as fp:
        fp.write("")

    result = build_docs_setup(testproject_path)
    assert result.exit_code == 0

    page_with_tag = testproject_path / "site/page_with_tag/index.html"
    contents = page_with_tag.read_text(encoding="utf8")
    assert "January 23, 2022" in contents

    # Now mark the most recent change to page_with_tag as ignored
    # May 4, 2018 is the date of the second most recent commit
    commit_hash = repo.git.log("docs/page_with_tag.md", format="%H", n=1)

    with open(str(testproject_path / "ignored-commits.txt"), "wt", encoding="utf-8") as fp:
        fp.write(commit_hash)

    # should not raise warning
    result = build_docs_setup(testproject_path)
    assert result.exit_code == 0

    page_with_tag = testproject_path / "site/page_with_tag/index.html"
    contents = page_with_tag.read_text(encoding="utf8")
    assert "May 4, 2018" in contents


@pytest.mark.skipif(sys.platform.startswith("win"), reason="monorepo plugin did not work for me on windows (even without this plugin)")
def test_monorepo_compat(tmp_path):
    testproject_path = setup_clean_mkdocs_folder("tests/fixtures/monorepo/mkdocs.yml", tmp_path)
    setup_commit_history(testproject_path)
    result = build_docs_setup(testproject_path)
    assert result.exit_code == 0, f"'mkdocs build' command failed with:\n\n{result.stdout}"

@pytest.mark.skipif(sys.platform.startswith("win"), reason="monorepo plugin did not work for me on windows (even without this plugin)")
def test_monorepo_compat_reverse_order(tmp_path):
    testproject_path = setup_clean_mkdocs_folder("tests/fixtures/monorepo/mkdocs_reverse_order.yml", tmp_path)
    setup_commit_history(testproject_path)
    result = build_docs_setup(testproject_path)
    assert result.exit_code == 0, f"'mkdocs build' command failed with:\n\n{result.stdout}"


def test_genfiles_plugin(tmp_path):
    testproject_path = setup_clean_mkdocs_folder("tests/fixtures/basic_project/mkdocs_plugin_genfiles.yml", tmp_path)
    setup_commit_history(testproject_path)

    result = build_docs_setup(testproject_path)
    assert result.exit_code == 0, f"'mkdocs build' command failed with:\n\n{result.stdout}"

    page_with_tag = testproject_path / "site/foo/index.html"
    contents = page_with_tag.read_text(encoding="utf8")
    assert "Bar, world!" in contents