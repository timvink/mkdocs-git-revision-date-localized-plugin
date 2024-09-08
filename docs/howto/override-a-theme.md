# Customize a theme

You can [customize an existing theme](https://www.mkdocs.org/user-guide/styling-your-docs/#customizing-a-theme) by overriding blocks or partials. You might want to do this because your theme is not natively supported, or you would like more control on the formatting. Below are some examples to help get you started.

## Example: default `mkdocs` theme

To add a revision date to the default `mkdocs` theme, add a `overrides/partials` folder to your `docs` folder and update your `mkdocs.yml` file. 
Then you can extend the base `mkdocs` theme by adding a new file `docs/overrides/content.html`:

=== ":octicons-file-code-16: mkdocs.yml"

    ```yaml
    theme:
        name: mkdocs
        custom_dir: docs/overrides
    ```

=== ":octicons-file-code-16: docs/overrides/content.html"

    ```html
    <!-- Overwrites content.html base mkdocs theme, taken from 
    https://github.com/mkdocs/mkdocs/blob/master/mkdocs/themes/mkdocs/content.html -->

    {% if page.meta.source %}
        <div class="source-links">
        {% for filename in page.meta.source %}
            <span class="label label-primary">{{ filename }}</span>
        {% endfor %}
        </div>
    {% endif %}

    {{ page.content }}

    <!-- This section adds support for localized revision dates -->
    {% if page.meta.git_revision_date_localized %}
        <small>Last update: {{ page.meta.git_revision_date_localized }}</small>
    {% endif %}
    {% if page.meta.git_created_date_localized %}
        <small>Created: {{ page.meta.git_created_date_localized }}</small>
    {% endif %}
    ```

## Example: `mkdocs-material` theme

[mkdocs-material](https://squidfunk.github.io/mkdocs-material/) has built-in support for `git_revision_date_localized` and `git_created_date_localized`. You can see that when viewing their [`source-file.html`](https://github.com/squidfunk/mkdocs-material/blob/master/src/partials/source-file.html) partial. 

If you want, you can customize further by [extending the mkdocs-material theme](https://squidfunk.github.io/mkdocs-material/customization/#extending-the-theme) and overriding the `source-file.html` partial as follows:

=== ":octicons-file-code-16: mkdocs.yml"

    ```yaml
    theme:
        name: 'material'
        custom_dir: docs/overrides
    ```

=== ":octicons-file-code-16: docs/overrides/partials/source-file.html"

    ```html
    {% import "partials/language.html" as lang with context %}

    <!-- taken from 
    https://github.com/squidfunk/mkdocs-material/blob/master/src/partials/source-file.html -->
    
    <hr />
    <div class="md-source-file">
    <small>

        <!-- mkdocs-git-revision-date-localized-plugin -->
        {% if page.meta.git_revision_date_localized %}
        {{ lang.t("source.file.date.updated") }}:
        {{ page.meta.git_revision_date_localized }}
        {% if page.meta.git_creation_date_localized %}
            <br />
            {{ lang.t("source.file.date.created") }}:
            {{ page.meta.git_creation_date_localized }}
        {% endif %}

        <!-- mkdocs-git-revision-date-plugin -->
        {% elif page.meta.revision_date %}
        {{ lang.t("source.file.date.updated") }}:
        {{ page.meta.revision_date }}
        {% endif %}
    </small>
    </div>
    ```

[mkdocs-material](https://squidfunk.github.io/mkdocs-material/) also supports [custom translations](https://squidfunk.github.io/mkdocs-material/setup/changing-the-language/#custom-translations) that you can use to specify alternative translations for `source.file.date.updated` ("Last updated") and `source.file.date.created` ("Created"). 

## Example: List last updated pages

Let's say we want to insert a list of the last 10 updated pages into our home page.

We can use the [mkdocs template variables](https://www.mkdocs.org/dev-guide/themes/#template-variables) together with [jinja2 filters](https://jinja.palletsprojects.com/en/latest/templates/#filters) to
[extend the mkdocs-material theme](https://squidfunk.github.io/mkdocs-material/customization/#extending-the-theme). [@simbo](https://github.com/simbo) provided this example that overrides `main.html`:

=== ":octicons-file-code-16: mkdocs.yml"

    ```yaml
    theme:
        name: 'material'
        custom_dir: docs/overrides
    ```

=== ":octicons-file-code-16: docs/overrides/main.html"

    ```jinja2
    {% extends "base.html" %}
    {% block site_nav %}
    {{ super() }}
    {% if page and page.file and page.file.src_path == "index.md" %}
        <div class="md-sidebar md-sidebar--secondary" data-md-component="sidebar" data-md-type="navigation">
        <div class="md-sidebar__scrollwrap">
            <div class="md-sidebar__inner">
            <nav class="md-nav md-nav--secondary md-nav--integrated" aria-label="Recently updated" data-md-level="0">
                <div class="md-nav__title">Recently updated</div>
                <ul class="md-nav__list" data-md-scrollfix>
                {% for file in (
                    pages
                    | selectattr("page.meta.git_revision_date_localized_raw_iso_datetime")
                    | selectattr("page.meta.git_creation_date_localized_raw_iso_datetime")
                    | sort(attribute="page.title")
                    | sort(attribute="page.meta.git_creation_date_localized_raw_iso_datetime", reverse=true)
                    | sort(attribute="page.meta.git_revision_date_localized_raw_iso_datetime", reverse=true)
                    )[:10]
                %}
                    <li class="md-nav__item">
                    <a class="md-nav__link" href="{{ file.url }}" style="display:block">
                        {{ file.page.title }}
                        <br/>
                        <small>
                        <span class="git-revision-date-localized-plugin git-revision-date-localized-plugin-timeago">
                            <span class="timeago" datetime="{{ file.page.meta.git_revision_date_localized_raw_iso_datetime }}" locale="en"></span>
                        </span>
                        </small>
                    </a>
                    </li>
                {% endfor %}
                </ul>
            </nav>
            </div>
        </div>
        </div>
    {% endif %}
    {% endblock %}
    ```

## Example: Populate `sitemap.xlm`

Having a correct lastmod in your `sitemap.xlm` is important for SEO, as it indicates to Search engines when to re-index pages, see [this blog from Bing](https://blogs.bing.com/webmaster/february-2023/The-Importance-of-Setting-the-lastmod-Tag-in-Your-Sitemap).

[`@thesuperzapper`](https://github.com/thesuperzapper) shared this [override](https://squidfunk.github.io/mkdocs-material/customization/?h=overri#extending-the-theme) in [mkdocs-git-revision-date-localized-plugin#120](https://github.com/timvink/mkdocs-git-revision-date-localized-plugin/issues/120):

```html
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{%- for file in pages -%}
    {% if not file.page.is_link and (file.page.abs_url or file.page.canonical_url) %}
    <url>
         <loc>{% if file.page.canonical_url %}{{ file.page.canonical_url|e }}{% else %}{{ file.page.abs_url|e }}{% endif %}</loc>
         {#- NOTE: we exclude `lastmod` for pages using a template, as their update time is not correctly detected #}
         {%- if not file.page.meta.template and file.page.meta.git_revision_date_localized_raw_iso_datetime %}
         <lastmod>{{ (file.page.meta.git_revision_date_localized_raw_iso_datetime + "+00:00") | replace(" ", "T") }}</lastmod>
         {%- endif %}
         <changefreq>daily</changefreq>
    </url>
    {%- endif -%}
{% endfor %}
</urlset>
```
