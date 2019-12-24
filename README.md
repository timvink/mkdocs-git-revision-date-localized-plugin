[![Actions Status](https://github.com/timvink/mkdocs-git-revision-date-localized-plugin/workflows/pytest/badge.svg)](https://github.com/timvink/mkdocs-git-revision-date-localized-plugin/actions)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mkdocs-git-revision-date-localized-plugin)
![PyPI](https://img.shields.io/pypi/v/mkdocs-git-revision-date-localized-plugin)
![PyPI - Downloads](https://img.shields.io/pypi/dm/mkdocs-git-revision-date-localized-plugin)
[![codecov](https://codecov.io/gh/timvink/mkdocs-git-revision-date-localized-plugin/branch/master/graph/badge.svg)](https://codecov.io/gh/timvink/mkdocs-git-revision-date-localized-plugin)
 
# mkdocs-git-revision-date-localized-plugin

[MkDocs](https://www.mkdocs.org/) plugin that enables displaying the date of the last git modification of a page. The plugin uses [babel](https://github.com/python-babel/babel/tree/master/babel) and [timeago.js](https://github.com/hustcc/timeago.js) to provide different localized date formats. Initial fork from [mkdocs-git-revision-date-plugin](https://github.com/zhaoterryy/mkdocs-git-revision-date-plugin).

![example](https://github.com/timvink/mkdocs-git-revision-date-localized-plugin/raw/master/example.png)

(*Example when used together with [mkdocs-material](https://github.com/squidfunk/mkdocs-material) theme*)

## Setup

Install the plugin using `pip` with the following command:

```bash
pip install mkdocs-git-revision-date-localized-plugin
```

Next, add the following lines to your `mkdocs.yml`:

```yaml
plugins:
  - search
  - git-revision-date-localized
```

> If you have no `plugins` entry in your config file yet, you'll likely also want to add the `search` plugin. MkDocs enables it by default if there is no `plugins` entry set.

## Usage

### In supported themes

- [mkdocs-material](https://squidfunk.github.io/mkdocs-material/) offers support for this plugin, see [setup instructions](https://squidfunk.github.io/mkdocs-material/plugins/revision-date/)

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

To change the date format, set the `type` parameter to one of `date`, `datetime`, `iso_date`, `iso_datetime` or `timeago`. Default is `date`. Example outputs:

```bash
28 November, 2019           # type: date
28 November, 2019 13:57:28  # type: datetime
2019-11-28                  # type: iso_date
2019-11-28 13:57:26         # type: iso_datetime
20 hours ago                # type: timeago
```

### `locale`

Specify a two letter [ISO639](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) language code to display dates in your preferred language.

- When used in combination with `type: date` or `type: datetime`, translation is done using [babel](https://github.com/python-babel/babel) which supports [these locales](http://www.unicode.org/cldr/charts/latest/supplemental/territory_language_information.html)
- When used in combination with `type: timeago` then [timeago.js](https://github.com/hustcc/timeago.js) is added to your website, which supports [these locales](https://github.com/hustcc/timeago.js/tree/master/src/lang). If you specify a locale not supported by timeago.js, the fallback is English (`en`)
- When not set, this plugin will look for `locale` or `language` options set in your theme. If also not set, the fallback is English (`en`)


### Example

Example of setting both options:

```yaml
# mkdocs.yml
plugins:
  - git-revision-date-localized:
    type: timeago
    locale: en
```

Result:

```
20 hours ago
```