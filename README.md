![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mkdocs-git-revision-date-localized-plugin)
![PyPI](https://img.shields.io/pypi/v/mkdocs-git-revision-date-localized-plugin)
![PyPI - Downloads](https://img.shields.io/pypi/dm/mkdocs-git-revision-date-localized-plugin)
 
# mkdocs-git-revision-date-localized-plugin

[MkDocs](https://www.mkdocs.org/) plugin that enables displaying the localized date of the last git modification of a markdown file. Forked from [mkdocs-git-revision-date-plugin](https://github.com/zhaoterryy/mkdocs-git-revision-date-plugin). The plugin uses [babel](https://github.com/python-babel/babel/tree/master/babel) and [timeago](https://github.com/hustcc/timeago) to provide different localized date formats.

![example](https://github.com/timvink/mkdocs-git-revision-date-localized-plugin/raw/master/example.png)

(*Example when used together with [mkdocs-material](https://github.com/squidfunk/mkdocs-material) theme*)

## Setup

Install the plugin using pip:

```bash
pip install mkdocs-git-revision-date-localized-plugin
```

Activate the plugin in `mkdocs.yml`:

```yaml
plugins:
  - git-revision-date-localized
```

## Usage

### In supported themes

- [mkdocs-material](https://squidfunk.github.io/mkdocs-material/) offers support for this plugin, see [setup instructions](https://squidfunk.github.io/mkdocs-material/extensions/revision-date/)

### In theme templates

In templates you can use `page.meta.git_revision_date_localized`:

```django hljs
{% if page.meta.git_revision_date_localized %}
  Last update: {{ page.meta.git_revision_date_localized }}
{% endif %}
```

### In markdown pages

In your markdown files you can use `{{ git_revision_date_localized }}`:

```django hljs
Last update: {{ git_revision_date_localized }}
```


## Options

### `type`

Set this option to one of `date`, `datetime`, `iso_date`, `iso_datetime` or `timeago`. Default is `date`. Example outputs:

```bash
28 November, 2019 # type: date
28 November, 2019 13:57:28 # type: datetime
2019-11-28 # type: iso_date
2019-11-28 13:57:26 # type: iso_datetime
20 hours ago # type: timeago
```

### `locale`

Set this option to a two letter [ISO639](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) language code to use a another language. This will overwrite any locale setting in `mkdocs` or your theme. If no locale is set fallback is English (`en`).

### Example

Example of setting both options:

```yaml
# mkdocs.yml
plugins:
  - git-revision-date-localized:
    type: timeago
    locale: nl
```
