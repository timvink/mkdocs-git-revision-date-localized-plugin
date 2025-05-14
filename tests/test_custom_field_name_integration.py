"""Integration tests for the custom frontmatter field name functionality."""

import os
import tempfile
import unittest
import shutil
import datetime
from pathlib import Path
from unittest import mock

import mkdocs.config as config
from mkdocs.config.base import load_config
from mkdocs.structure.pages import Page
from mkdocs.structure.files import File, Files

from mkdocs_git_revision_date_localized_plugin.plugin import GitRevisionDateLocalizedPlugin
from mkdocs_git_revision_date_localized_plugin.util import Util


class TestCustomFieldNameIntegration(unittest.TestCase):
    """Test the custom frontmatter field name in a real MkDocs setup."""
    
    def setUp(self):
        """Create a temporary directory for the test."""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(self.test_dir))
        
        # Create a simple MkDocs project
        self.docs_dir = os.path.join(self.test_dir, 'docs')
        os.makedirs(self.docs_dir)
        
        # Initialize our plugin explicitly instead of relying on the config
        self.plugin = GitRevisionDateLocalizedPlugin()
        self.plugin.config = {
            'enabled': True,
            'type': 'date',
            'timezone': 'UTC',
            'locale': 'en',
            'custom_format': '%d %B %Y',  # Add this to avoid None error
            'creation_date_field_name': 'created',
            'update_date_field_name': 'modified',
            'include_relative_dates': True,
            'date_format_in_metadata': True
        }
        
        # Add required attributes for plugin functionality
        self.plugin.last_site_revision_hash = "abc123"
        self.plugin.last_site_revision_timestamp = int(datetime.datetime(2023, 5, 1).timestamp())
        self.plugin.last_revision_commits = {}
        
        # Create mkdocs.yml file
        self.mkdocs_yml = os.path.join(self.test_dir, 'mkdocs.yml')
        with open(self.mkdocs_yml, 'w') as f:
            f.write("""
site_name: Test Site
docs_dir: docs
""")
            
        # Create a page with custom field names in frontmatter
        self.page_path = os.path.join(self.docs_dir, 'test_page.md')
        with open(self.page_path, 'w') as f:
            f.write("""---
title: Test Page
created: 2023-01-15
modified: 2023-05-20
---

# Test Page

This is a test page.
""")

    def test_integration_with_custom_field_names(self):
        """Test that custom field names work in a real MkDocs setup."""
        # Load the MkDocs configuration
        cfg = load_config(self.mkdocs_yml)
        
        # We're using the pre-configured plugin instance from setup
        plugin = self.plugin
        
        # Initialize the util object if it's not already initialized
        if not hasattr(plugin, 'util') or plugin.util is None:
            plugin.util = Util(plugin.config, os.path.dirname(os.path.abspath(__file__)))
            
        # Verify plugin configuration
        self.assertEqual(plugin.config.get('creation_date_field_name'), 'created')
        self.assertEqual(plugin.config.get('update_date_field_name'), 'modified')
        self.assertTrue(plugin.config.get('include_relative_dates'))
        self.assertTrue(plugin.config.get('date_format_in_metadata'))
        
        # Create a mock page object
        file_obj = File(
            path='test_page.md',
            src_dir=self.docs_dir,
            dest_dir=os.path.join(self.test_dir, 'site'),
            use_directory_urls=True
        )
        files = Files([file_obj])
        page = Page(
            title='Test Page',
            file=file_obj,
            config=cfg
        )
        
        # Add meta information from the page
        with open(self.page_path, 'r') as f:
            page.markdown = f.read()
            # Parse frontmatter manually
            import yaml
            # Extract YAML between the --- markers
            content = page.markdown.split('---')
            if len(content) > 1:
                try:
                    page.meta = yaml.safe_load(content[1])
                except:
                    page.meta = {}
            else:
                page.meta = {}
        
        # Mock the git functionality to avoid repository issues
        with mock.patch.object(plugin.util, 'get_git_commit_timestamp', 
                               return_value=('abcdef', int(datetime.datetime(2023, 1, 1).timestamp()))):
            # Extract frontmatter into meta
            plugin.on_page_markdown(page.markdown, page, cfg, files)
        
        # Verify that the custom field names have been processed
        self.assertIn('created', page.meta)
        self.assertIn('modified', page.meta)
        
        # With date_format_in_metadata, we should have these fields
        if plugin.config.get('date_format_in_metadata'):
            self.assertIn('created_formatted', page.meta)
            self.assertIn('modified_formatted', page.meta)
            
            # Verify that backwards compatibility is maintained
            self.assertIn('date_formatted', page.meta)
            self.assertIn('lastmod_formatted', page.meta)
        
        # With include_relative_dates, we should have these fields
        if plugin.config.get('include_relative_dates'):
            self.assertIn('created_relative', page.meta)
            self.assertIn('modified_relative', page.meta)
            
            # Verify that backwards compatibility is maintained
            self.assertIn('date_relative', page.meta)
            self.assertIn('lastmod_relative', page.meta)


if __name__ == '__main__':
    unittest.main()
