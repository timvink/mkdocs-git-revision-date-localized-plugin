# mkdocs-git-revision-date-localized-plugin

[MkDocs](https://www.mkdocs.org/) plugin that displays the localized date of the last modification of a markdown file. Forked from [mkdocs-git-revision-date-plugin](https://github.com/zhaoterryy/mkdocs-git-revision-date-plugin)

## Setup

Install the plugin using pip:

```bash
# FIRST VERSION NOT YET PUBLISHED
pip install mkdocs-git-revision-date-localized-plugin
```

Activate the plugin in `mkdocs.yml`:

```yaml
plugins:
  - git-revision-date
```

## Usage

### In theme templates

In templates you can use `page.meta.git_revision_date_localized`:

```django hljs
{% if page.meta.git_revision_date_localized %}
<small><br><i>Updated {{ page.meta.git_revision_date_localized }}</i></small>
{% endif %}
```

### In markdown pages

In your markdown files you can use `{{ git_revision_date_localized }}`:

```django hljs
Updated {{ git_revision_date_localized_iso }}
```

## Localization updates

There are three date formats:

- A date string format (using [babel](https://github.com/python-babel/babel/tree/master/babel)
- A ISO format *(YYYY-mm-dd)*
- A time ago format (using [timeago](https://github.com/hustcc/timeago)

```django hljs
<i>Updated {{ git_revision_date_localized }}</i>
<i>Updated {{ git_revision_date_localized_iso }}</i>
<i>Updated {{ git_revision_date_localized_timeago }}</i>
```

Output:

```
Updated 28 November, 2019
Updated 2019-11-28
Updated 20 hours agon
```

## Options

### `locale`

Set this option to a two letter [ISO639](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) language code to use a another language. This will overwrite any locale setting in `mkdocs` or your theme. If no locale is set fallback is English (`en`).
