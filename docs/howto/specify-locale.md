# Specify a locale

`locale` is a two letter [ISO639](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) language code (f.e. `en`) or [5-letter language code with added territory/region/country](https://www.mkdocs.org/user-guide/localizing-your-theme/#supported-locales) (`en_US`) that `git-revision-date-localized` uses to display dates in your preferred language.

For example:

```yaml
April 27, 2021                # `locale: en` with `type: date` (default)
April 27, 2021 13:11:28       # `locale: en` with `type: datetime`
2 weeks ago                   # `locale: en` with `type: timeago`
27 de marzo de 2021           # `locale: es` with `type: date`
27 de marzo de 2021 13:57:28  # `locale: es` with `type: datetime`
hace 2 semanas                # `locale: es` with `type: timeago`
```

You can set the `locale` in different locations, both for your entire site and on a per-page basis. If specified multiple times `git-revision-date-localized` will use the `locale` that is most specific to a page.

Here's the order of priority:

## 1. Page locale set by the `i18n` plugin

The [mkdocs-static-i18n](https://github.com/ultrabug/mkdocs-static-i18n) plugin helps you support multiple language versions of your site. When enabled, `i18n` will add a `locale` attribute to each markdown page that `git-revision-date-localized` will use.

## 2. Page locale set by metadata

The [Metadata](https://python-markdown.github.io/extensions/meta_data/) extension adds the ability to attach arbitrary key-value pairs to a document via front matter written in YAML syntax before the Markdown. Enable it in your `mkdocs.yml`:

```yaml
# mkdocs.yml
markdown_extensions:
  - meta
```

If set `git-revision-date-localized` will use the `locale` key in a markdown page's frontmatter, for example:

```md
---
locale: en
---

# Page title
```

## 3. Site locale set by your theme

Some [MkDocs Themes](https://github.com/mkdocs/mkdocs/wiki/MkDocs-Themes) support [localization](https://www.mkdocs.org/user-guide/localizing-your-theme/) by setting a `locale` or `language` option. See for example the [Changing the language](https://squidfunk.github.io/mkdocs-material/setup/changing-the-language/) section of [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).

Example:

```yaml
# mkdocs.yml
theme:
  language: en
```

## 4. Site locale set by this plugin

Of course `locale` is an [option](../options.md) for this plugin also.

```yaml
plugins:
- git-revision-date-localized:
    locale: en
```

## 5. Fallback locale

If no `locale` is specified anywhere, the fallback is English with the US date format (`en`).

!!! info "Supported locales"

    - When used in combination with `type: date` or `type: datetime`, translation is done using [babel](https://github.com/python-babel/babel) which supports [these locales](http://www.unicode.org/cldr/charts/latest/supplemental/territory_language_information.html)

    - When used in combination with `type: timeago` then [timeago.js](https://github.com/hustcc/timeago.js) is added to your website, which supports [these locales](https://github.com/hustcc/timeago.js/tree/master/src/lang). If you specify a locale not supported by timeago.js, the fallback is English (`en`)
