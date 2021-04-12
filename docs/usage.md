# Usage

## In supported themes

The following mkdocs themes have native support:

- [mkdocs-material](https://squidfunk.github.io/mkdocs-material/), see [setup instructions](https://squidfunk.github.io/mkdocs-material/setup/adding-a-git-repository/#revision-date-localized) for details.

## In markdown pages

In your markdown files you can use the <code>\{\{ git_revision_date_localized \}\}</code> tag anywhere you'd like:

<div class="highlight">
    <pre id="__code_42"><span></span><button class="md-clipboard md-icon" title="Copy to clipboard" data-clipboard-target="#__code_42 > code"></button><code>Last update: &#123;{ git_revision_date_localized }}
</code></pre></div>


## In unsupported themes

You can [customize an existing theme](https://www.mkdocs.org/user-guide/styling-your-docs/#customizing-a-theme) by overriding blocks or partials and using the `page.meta.git_revision_date_localized` and/or `page.meta.git_creation_date_localized` tag(s).


### mkdocs theme

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

### mkdocs-material theme

[mkdocs-material](https://squidfunk.github.io/mkdocs-material/) has native support for `git_revision_date_localized`, but not yet for `git_created_date_localized`. You can [extend the mkdocs-material theme](https://squidfunk.github.io/mkdocs-material/customization/#extending-the-theme) by adding overriding a partial as follows:

=== "mkdocs.yml"

    ```yml
    theme:
        name: 'material'
        custom_dir: docs/overrides_material_theme
    ```

=== "docs/overrides/partials/source-date.html"

    ```html
    {% import "partials/language.html" as lang with context %}

    <!-- Last updated date -->
    {% set label = lang.t("source.revision.date") %}
    <hr />
    <div class="md-source-date">
    <small>

        <!-- mkdocs-git-revision-date-localized-plugin -->
        {% if page.meta.git_revision_date_localized %}
        {{ label }}: {{ page.meta.git_revision_date_localized }}

        {% if page.meta.git_creation_date_localized %}
            <br />Created: {{ page.meta.git_creation_date_localized }}
        {% endif %}
        
        <!-- mkdocs-git-revision-date-plugin -->
        {% elif page.meta.revision_date %}
        {{ label }}: {{ page.meta.revision_date }}
        {% endif %}
    </small>
    </div>
    ```

## In custom themes

When writing your own [custom themes](https://www.mkdocs.org/user-guide/custom-themes/) you can use the `page.meta.git_revision_date_localized` jinja tag, like so for example:

```django
{% if page.meta.git_revision_date_localized %}
  Last update: {{ page.meta.git_revision_date_localized }}
{% endif %}
```

## Custom styling

You can style the output using CSS, for example by [including extra css](https://www.mkdocs.org/user-guide/configuration/#extra_css) to your mkdocs site. 

The date outputs are always wrapped in `span` elements with the classes `git-revision-date-localized-plugin` and `git-revision-date-localized-plugin-{type}` (where `{type}` is replaced with the `type` option set in the plugin).

Here's an example:

=== "mkdocs.yml"

    ```yaml
    extra_css:
        css/extra.css
    ```

=== "docs/css/extra.css"

    ```css
    .git-revision-date-localized-plugin { color: red; }
    ```
