# mkdocs-git-revision-date-plugin

MkDocs plugin for setting revision date from git per markdown file.

## Setup
Install the plugin using pip:

`pip install mkdocs-git-revision-date-plugin`

Activate the plugin in `mkdocs.yml`:
```yaml
plugins:
  - search
  - git-revision-date
```

> **Note:** If you have no `plugins` entry in your config file yet, you'll likely also want to add the `search` plugin. MkDocs enables it by default if there is no `plugins` entry set, but now you have to enable it explicitly.

More information about plugins in the [MkDocs documentation][mkdocs-plugins].

## Usage
The revision date will be displayed in ISO format *(YYYY-mm-dd)*.

### Templates - `page.meta.revision_date`:
#### Example
```django hljs
{% block footer %}
<hr>
<p>{% if config.copyright %}
<small>{{ config.copyright }}<br></small>
{% endif %}
<small>Documentation built with <a href="https://www.mkdocs.org/">MkDocs</a>.</small>
{% if page.meta.revision_date %}
<small><br><i>Updated {{ page.meta.revision_date }}</i></small>
{% endif %}
</p>
{% endblock %}
```
More information about templates [here][mkdocs-template].

More information about blocks [here][mkdocs-block].

### Markdown - `{{ git_revision_date }}`:
#### Example
```md
Page last revised on: {{ git_revision_date }}
```
If using [mkdocs_macro_plugin][mkdocs-macro], it must be included after our plugin.

i.e., mkdocs.yml:
```yaml
plugins:
  - search
  - git-revision-date
  - macros
```


[mkdocs-plugins]: https://www.mkdocs.org/user-guide/plugins/
[mkdocs-template]: https://www.mkdocs.org/user-guide/custom-themes/#template-variables
[mkdocs-block]: https://www.mkdocs.org/user-guide/styling-your-docs/#overriding-template-blocks
[mkdocs-macro]: https://github.com/fralau/mkdocs_macros_plugin

## Options

### `enabled_if_env`

Setting this option will enable the build only if there is an environment variable set to 1. Default is not set.

### `modify_md`

Setting this option to false will disable the use of `{{ git_revision_date }}` in markdown files. Default is true.

### `as_datetime`

Setting this option to True will output git_revision_date as a python `datetime`. This means you can use jinja2 date formatting, for example as `{{ git_revision_date.strftime('%d %B %Y') }}`. Default is false.