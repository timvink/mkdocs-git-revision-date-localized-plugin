# Getting started

This plugin offers the following timestamps:

| timestamp | description |
|-----------|-------------|
| git-revision-date-localized | Last git commit that touched a file. Enabled by default. |
| git-creation-date-localized | First git commit that touched a file. Enable in [options](options.md) |

## Supported themes

The following mkdocs themes have native support, which means no additional setup is required other than enabling the plugin (see [setup](index.md#setup)). The timestamps will appear at the bottom of the page.

| theme | git-revision-date-localized | git-creation-date-localized | docs |
|-------|-------------------|-------------------|------|
| [mkdocs-material](https://squidfunk.github.io/mkdocs-material/) | :white_check_mark: | :white_check_mark:| [setup](https://squidfunk.github.io/mkdocs-material/setup/adding-a-git-repository/#revision-date-localized) |


If your theme is not supported, it's easy to [customize the theme](override-a-theme.md).

## Using markdown tags

You can also choose to use the <code>\{\{ git_revision_date_localized \}\}</code> and <code>\{\{ git_creation_date_localized \}\}</code> tags directly in a markdown file. For example, this page was last updated {{ git_revision_date_localized }} !

<div class="highlight">
    <pre id="__code_42"><span></span><button class="md-clipboard md-icon" title="Copy to clipboard" data-clipboard-target="#__code_42 > code"></button><code>This page was last updated: &#123;{ git_revision_date_localized }}
</code></pre></div>


