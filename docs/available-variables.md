# Available variables

This plugin offers the following variables:

| timestamp | description |
|:-----------|:------------|
| `git-revision-date-localized` | Last git commit that touched a file. Enabled by default. |
| `git-creation-date-localized` | First git commit that touched a file. Enable in [options](options.md). |
| `git_site_revision_date_localized` | Last git commit that touched any file in the `docs/` folder. Enabled by default. |

You can use these variables wrapped in curly brackets (`{{` and `}}`) anywhere in a markdown file, like so:

<pre id="__code_42"><span></span><button class="md-clipboard md-icon" title="Copy to clipboard" data-clipboard-target="#__code_42 > code"></button><code>This page was last updated: *&#123;{ git_revision_date_localized }}*
</code></pre>

Example output: This page was last updated *{{ git_revision_date_localized }}*.

Changing the `type`, `timezone` and/or `locale` in the [options](options.md) will effect the output of these variables. To change the styling see [Applying custom styling](howto/custom-styling.md).

## Variables for overriding themes

If you do not want to include revision dates manually in each markdown file, or if you would like more control on the formatting, you can [override a theme](howto/override-a-theme.md). You can use the same three variables but with a `page.meta.` prefix:

- `page.meta.git-revision-date-localized`
- `page.meta.git-creation-date-localized`
- `page.meta.git_revision_date_localized_raw_date`

To allow for more flexibility when overriding a theme there are also variables for each different `type` available (regardless of the setting for `type` in [options](options.md)), where the output is also not wrapped in `<span>` elements (so you can do the CSS styling yourself): 

- `page.meta.git_revision_date_localized_raw_date`
- `page.meta.git_revision_date_localized_raw_datetime`
- `page.meta.git_revision_date_localized_raw_iso_date`
- `page.meta.git_revision_date_localized_raw_iso_datetime`
- `page.meta.git_revision_date_localized_raw_timeago`
- `page.meta.git_site_revision_date_localized_raw_datetime`
- `page.meta.git_site_revision_date_localized_raw_iso_date`
- `page.meta.git_site_revision_date_localized_raw_date`
- `page.meta.git_site_revision_date_localized_raw_iso_datetime`
- `page.meta.git_site_revision_date_localized_raw_timeago`

And if you've enable creation date in the config:

- `page.meta.git_creation_date_localized_raw_date`
- `page.meta.git_creation_date_localized_raw_datetime`
- `page.meta.git_creation_date_localized_raw_iso_date`
- `page.meta.git_creation_date_localized_raw_iso_datetime`
- `page.meta.git_creation_date_localized_raw_timeago`
