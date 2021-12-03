# Apply custom styling

You can change the appearance of the revision dates by [including extra CSS](https://www.mkdocs.org/user-guide/configuration/#extra_css) to your mkdocs site. 

## CSS Classes

To allow for easier styling date outputs are wrapped in `<span>` elements with the classes `git-revision-date-localized-plugin` and `git-revision-date-localized-plugin-{type}`, where `{type}` is replaced with the `type` set in the plugin settings (see [options](../options.md)).

For example when `type: datetime` is set, using the following in a markdown file:

<pre id="__code_42"><span></span><button class="md-clipboard md-icon" title="Copy to clipboard" data-clipboard-target="#__code_42 > code"></button><code>Last update: {{ git_revision_date_localized }&#125;
</code></pre>

Could output the following HTML:

```django
Last update: 
<span class="git-revision-date-localized-plugin git-revision-date-localized-plugin-datetime">28 November, 2019 13:57:28</span>
```

## Customizing a class

Making all revision dates red is as easy as:

=== ":octicons-file-code-16: docs/css/extra.css"

    ```css
    .git-revision-date-localized-plugin { color: red; }
    ```

=== ":octicons-file-code-16: mkdocs.yml"

    ```yaml
    extra_css:
        css/extra.css
    ```

