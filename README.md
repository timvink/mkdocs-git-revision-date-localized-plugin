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
Use `page.meta.revision_date` in templates to access the revision date of the current page in ISO format *(YYYY-mm-dd)*.

## Example
```django hljs
{% block footer %}
<hr>
<p>{% if config.copyright %}
<small>{{ config.copyright }}<br></small>
{% endif %}
<small>Documentation built with <a href="http://www.mkdocs.org/">MkDocs</a>.</small>
{% if page.meta.revision_date %}
<small><br><i>Updated {{ page.meta.revision_date }}</i></small>
{% endif %}
</p>
{% endblock %}
```

More information about templates [here][mkdocs-template].

More information about blocks [here][mkdocs-block].

[mkdocs-plugins]: http://www.mkdocs.org/user-guide/plugins/
[mkdocs-template]: https://www.mkdocs.org/user-guide/custom-themes/#template-variables
[mkdocs-block]: https://www.mkdocs.org/user-guide/styling-your-docs/#overriding-template-blocks
