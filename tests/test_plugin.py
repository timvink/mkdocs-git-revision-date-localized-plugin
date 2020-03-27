#! python3  # noqa E265

"""
    Test for the plugin class (subclass of mkdocs.BasePlugin).

    Usage from the repo root folder:

        # all tests
        python -m unittest tests.test_plugin

        # specific test
        python -m unittest tests.test_plugin.TestMkdocsPlugin.
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
from pathlib import Path
import logging
import unittest

# MkDocs
from mkdocs.config import load_config

# package
from mkdocs_git_revision_date_localized_plugin.plugin import (
    GitRevisionDateLocalizedPlugin,
)


# #############################################################################
# ######## Globals #################
# ##################################

# make this test module easily reusable
PLUGIN_NAME = "git-revision-date-localized"

# custom log level to get plugin info messages
logging.basicConfig(level=logging.INFO)

# #############################################################################
# ########## Helpers ###############
# ##################################


# #############################################################################
# ########## Classes ###############
# ##################################


class TestMkdocsPlugin(unittest.TestCase):
    """MkDocs plugin module."""

    # -- Standard methods --------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        """Executed when module is loaded before any test."""
        cls.fixtures_mkdocs_config_files = sorted(
            Path("tests/basic_setup").glob("*.yml")
        )

        cls.fixtures_config_cases_ok = {
            "default_explicit": {
                "type": "date",
                "locale": "en",
                "fallback_to_build_date": False,
            },
            # locale variations
            "default_no_locale": {"type": "date", "fallback_to_build_date": False},
            "custom_locale": {"locale": "fr"},
            # type variations
            "type_datetime": {"type": "datetime"},
            "type_iso_date": {"type": "iso_date"},
            "type_iso_datetime": {"type": "iso_datetime"},
            "type_timeago": {"type": "timeago"},
            # falbback variations
            "fallback_true": {"fallback_to_build_date": True},
        }

        cls.fixtures_config_cases_bad = {
            "invalid_option_name": {"language": "en",},
            # "invalid_value": {"type": "calendar", "locale": "nl"},
            "invalid_value_type": {"type": 1, "locale": "de"},
        }

    def setUp(self):
        """Executed before each test."""
        pass

    def tearDown(self):
        """Executed after each test."""
        pass

    @classmethod
    def tearDownClass(cls):
        """Executed after the last test."""
        pass

    # -- TESTS ---------------------------------------------------------

    # -- GET --
    def test_plugin_instanciation(self):
        """Simple test plugin instanciation"""
        # instanciate
        plg = GitRevisionDateLocalizedPlugin()

        # default values
        self.assertIsInstance(plg.config, dict)
        self.assertEqual(plg.config, {})

    def test_plugin_load_configs_ok(self):
        """Test inherited plugin load_config method on good configurations"""
        # instanciate
        plg = GitRevisionDateLocalizedPlugin()

        # parse fixtures configurations alone
        for i in self.fixtures_config_cases_ok:
            cfg = self.fixtures_config_cases_ok.get(i)
            out_cfg = plg.load_config(options=cfg)

            # check if config loader returned no errors
            self.assertIsInstance(out_cfg, tuple)
            [self.assertListEqual(v, []) for v in out_cfg]
            self.assertEqual(all([len(i) == 0 for i in out_cfg]), True)

            # try associating mkdocs configuration
            for i in self.fixtures_mkdocs_config_files:
                out_cfg_mkdocs = plg.load_config(
                    options=cfg, config_file_path=str(i.resolve())
                )

                # check if config loader returned no errors
                self.assertIsInstance(out_cfg_mkdocs, tuple)
                [self.assertListEqual(v, []) for v in out_cfg_mkdocs]
                self.assertEqual(all([len(i) == 0 for i in out_cfg_mkdocs]), True)

    def test_plugin_load_configs_bad(self):
        """Test inherited plugin load_config method on bad configurations"""
        # instanciate
        plg = GitRevisionDateLocalizedPlugin()

        # simulate a complete configuration
        for i in self.fixtures_config_cases_bad:
            cfg = self.fixtures_config_cases_bad.get(i)
            out_cfg = plg.load_config(options=cfg)

            # check if config loader returned no errors
            self.assertIsInstance(out_cfg, tuple)
            self.assertEqual(all([len(i) == 0 for i in out_cfg]), False)

            # try associating mkdocs configuration
            for i in self.fixtures_mkdocs_config_files:
                out_cfg_mkdocs = plg.load_config(
                    options=cfg, config_file_path=str(i.resolve())
                )

                # check if config loader returned no errors
                self.assertIsInstance(out_cfg_mkdocs, tuple)
                self.assertEqual(all([len(i) == 0 for i in out_cfg_mkdocs]), False)

    def test_plugin_on_config(self):
        """Test inherited plugin on_config method"""
        # load try associating mkdocs configuration
        for i in self.fixtures_mkdocs_config_files:
            # logging.info("Using Mkdocs configuration: %s " % i.resolve())
            cfg_mkdocs = load_config(str(i))

            # get mkdocs locale config - expected as future feature
            mkdocs_locale = cfg_mkdocs.get("locale", None)

            # get our plugin config and copy it
            plugin_loaded_from_mkdocs = cfg_mkdocs.get("plugins").get(PLUGIN_NAME)
            cfg_before_on_config = plugin_loaded_from_mkdocs.config.copy()

            # get theme configuration
            theme = cfg_mkdocs.get("theme")  # -> Theme

            # look for the theme locale/language
            if "locale" in theme._vars:
                theme_locale = theme._vars.get("locale")
            elif "language" in theme._vars:
                theme_locale = theme._vars.get("language")
            else:
                theme_locale = None

            # execute on_config with global mkdocs loaded configuration and save config
            plugin_loaded_from_mkdocs.on_config(cfg_mkdocs)
            cfg_after_on_config = plugin_loaded_from_mkdocs.config.copy()

            # -- CASES for LOCALE ---------------------------------------
            result_locale = cfg_after_on_config.get("locale")
            # if locale set in plugin configuration = it the one!
            if cfg_before_on_config.get("locale"):
                self.assertEqual(result_locale, cfg_before_on_config.get("locale"))
            # if locale set in theme: it should be used
            elif theme_locale and not cfg_before_on_config.get("locale"):
                self.assertEqual(result_locale, theme_locale)
            # if locale not set in plugin nor in theme but in mkdocs = mkdocs
            elif (
                mkdocs_locale
                and not cfg_before_on_config.get("locale")
                and not theme_locale
            ):
                self.assertEqual(result_locale, mkdocs_locale)
            # if locale is not set at all = default = "en"
            else:
                self.assertEqual(result_locale, "en")


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    unittest.main()
