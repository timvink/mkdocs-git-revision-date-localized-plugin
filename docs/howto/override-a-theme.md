# Customize a theme

You can [customize an existing theme](https://www.mkdocs.org/user-guide/styling-your-docs/#customizing-a-theme) by overriding blocks or partials. You might want to do this because your theme is not natively supported, or you would like more control on the formatting. Below are two examples to help get you started.

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
    </small>
    </div>
    ```

