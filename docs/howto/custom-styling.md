# Apply custom styling

You might want to change the appearance of the dates in your theme. You can style the output using CSS, for example by [including extra css](https://www.mkdocs.org/user-guide/configuration/#extra_css) to your mkdocs site. 

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

