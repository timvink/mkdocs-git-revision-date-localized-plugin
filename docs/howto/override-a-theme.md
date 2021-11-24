# Customize a theme

You can [customize an existing theme](https://www.mkdocs.org/user-guide/styling-your-docs/#customizing-a-theme) by overriding blocks or partials. You might want to do this because your theme is not natively supported, or you would like more control on the formatting. Below are some examples to get you started.

## Example: default `mkdocs` theme

To add a revision date to the default `mkdocs` theme, add a `overrides/partials` folder to your `docs` folder and update your `mkdocs.yml` file. 
Then you can extend the base `mkdocs` theme by adding a new file `docs/overrides/content.html`:

=== "mkdocs.yml"

    ```yml
    theme:
        name: mkdocs
        custom_dir: docs/overrides
    ```

=== "docs/overrides/content.html"

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

    {% if page.meta.git_revision_date_localized %}
        <small>Last update: {{ page.meta.git_revision_date_localized }}</small>
    {% endif %}
    {% if page.meta.git_created_date_localized %}
        <small>Created: {{ page.meta.git_created_date_localized }}</small>
    {% endif %}
    ```

## Example: `mkdocs-material` theme

[mkdocs-material](https://squidfunk.github.io/mkdocs-material/) has native support for `git_revision_date_localized` and `git_created_date_localized`. If you want, you can customize further by [extending the mkdocs-material theme](https://squidfunk.github.io/mkdocs-material/customization/#extending-the-theme) and overriding the [`source-file.html`](https://github.com/squidfunk/mkdocs-material/blob/master/src/partials/source-file.html) partial as follows:

=== "mkdocs.yml"

    ```yml
    theme:
        name: 'material'
        custom_dir: docs/overrides_material_theme
    ```

=== "docs/overrides/partials/source-file.html"

    ```html
    {% import "partials/language.html" as lang with context %}

    <!-- Last updated date -->
    {% set label = lang.t("source.file.date.updated") %}
    <hr />
    <div class="md-source-date">
    <small>

        <!-- mkdocs-git-revision-date-localized-plugin -->
        {% if page.meta.git_revision_date_localized %}
        {{ label }}: {{ page.meta.git_revision_date_localized }}

        {% if page.meta.git_creation_date_localized %}
            <br />{{ lang.t("source.file.date.created") }}: {{ page.meta.git_creation_date_localized }} 
        {% endif %}

        <!-- mkdocs-git-revision-date-plugin -->
        {% elif page.meta.revision_date %}
        {{ label }}: {{ page.meta.revision_date }}
        {% endif %}
    </small>
    </div>
    ```

## Available variables

When customizing or [writing your own themes](https://www.mkdocs.org/user-guide/custom-themes/) `mkdocs-revision-date-localized-plugin` will make available the following jinja variables:

- `page.meta.git_revision_date_localized`
- `page.meta.git_creation_date_localized`

To insert these variables in a partial/block/template, use the jinja2 bracks `{{` and `}}`. The values of these variables depend on the plugin options specified, and are wrapped in `<span>` elements. For example, when using `type: timeago` (see [options](../options.md)):

=== "input"

    ```django
    {% if page.meta.git_revision_date_localized %}
    Last update: {{ page.meta.git_revision_date_localized }}
    {% endif %}
    ```

=== "output"

    ```django
    Last update: <span class="timeago" datetime="2021-11-03T12:25:03+01:00" locale="en" timeago-id="5"></span>
    ```

!!! info "Note"

    When `type: timeago` option is used, `mkdocs-revision-date-localized-plugin` adds [timeago.js](https://timeago.org/) to your mkdocs website, which dynamically inserts a value between the `<span>` elements like `2 weeks ago`.


As a developer you might want access to multiple 'raw' date types. These variables also do not have the `<span>` elements. You can use:

- `page.meta.git_revision_date_localized_raw_date`
- `page.meta.git_revision_date_localized_raw_datetime`
- `page.meta.git_revision_date_localized_raw_iso_date`
- `page.meta.git_revision_date_localized_raw_iso_datetime`
- `page.meta.git_revision_date_localized_raw_timeago`

And if you've enable creation date in the config:

- `page.meta.git_creation_date_localized_raw_date`
- `page.meta.git_creation_date_localized_raw_datetime`
- `page.meta.git_creation_date_localized_raw_iso_date`
- `page.meta.git_creation_date_localized_raw_iso_datetime`
- `page.meta.git_creation_date_localized_raw_timeago`