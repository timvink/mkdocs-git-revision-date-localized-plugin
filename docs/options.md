# Options

You can customize the plugin by setting options in `mkdocs.yml`. For example:

=== ":octicons-file-code-16: mkdocs.yml"

  ```yaml
  plugins:
    - git-revision-date-localized:
        type: timeago
        custom_format: "%d. %B %Y"
        timezone: Europe/Amsterdam
        locale: en
        fallback_to_build_date: false
        enable_creation_date: true
        exclude:
            - index.md
        enable_git_follow: true
        enabled: true
        strict: true
        ignored_commits_file: .git-blame-ignore-revs
  ```

## `type`

Default is `date`. The format of the date to be displayed. Valid values are `date`, `datetime`, `iso_date`, `iso_datetime`, `timeago` and `custom`. Example outputs:

```yaml
November 28, 2019           # type: date (default)
November 28, 2019 13:57:28  # type: datetime
2019-11-28                  # type: iso_date
2019-11-28 13:57:26         # type: iso_datetime
20 hours ago                # type: timeago
28. November 2019           # type: custom
```

## `custom_format`

Default is `%d. %B %Y`. The date format used when `type: custom`. Passed to python's `strftime`, see the [cheatsheat](https://strftime.org/) for details.

## `timezone`

Default is `UTC`. Specify a time zone database name ([reference](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)). This option is especially relevant when using `type: datetime` and `type: iso_datetime`. Note that when using [timeago](http://timeago.yarp.com/) (with `type: timeago`) any difference in time zones between server and client will be handled automatically.

=== ":octicons-file-code-16: mkdocs.yml"

  ```yaml
  plugins:
    - git-revision-date-localized:
        timezone: Europe/Amsterdam
  ```


## `locale`

Default is `None`. Specify a two letter [ISO639](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) language code (f.e. `en`) or [5-letter language code with added territory/region/country](https://www.mkdocs.org/user-guide/localizing-your-theme/#supported-locales) (`en_US`) to display dates in your preferred language. Note this plugin supports many different ways to [specify the locale](howto/specify-locale.md), but if not specified _anywhere_ the fallback will be English (`en`). `locale` is used to translate timestamps to dates when `type: date` or `type: datetime` (using [babel](https://github.com/python-babel/babel)) as well as to translate datetimes to a relative timeago string when `type: timeago` (using [timeago.js](https://github.com/hustcc/timeago.js)).

Example outputs:

```yaml
# `locale: en`
April 27, 2021                # with `type: date` (default)
April 27, 2021 13:11:28       # with `type: datetime`
2 weeks ago                   # with `type: timeago`
# `locale: es`
27 de marzo de 2021           # with `type: date`
27 de marzo de 2021 13:57:28  # with `type: datetime`
hace 2 semanas                # with `type: timeago`
```

=== ":octicons-file-code-16: mkdocs.yml"

  ```yaml
  plugins:
    - git-revision-date-localized:
        locale: en_US
  ```

!!! note

    When using `type: timeago`, [timeago.js](https://github.com/hustcc/timeago.js) is added to your website, which supports [these locales](https://github.com/hustcc/timeago.js/tree/master/src/lang). If you specify a locale not supported by timeago.js, the fallback is English (`en`). It might happen that your specific locale is supported by babel (used by date formats) but not by timeago. In that case open an issue with this plugin.


## `fallback_to_build_date`

Default is `false`. Enables falling back to the time when `mkdocs build` was executed *when git is not available*. This means the revision date will be incorrect, but this can be acceptable if you want your project to also successfully build in environments with no access to GIT.

=== ":octicons-file-code-16: mkdocs.yml"

  ```yaml
  plugins:
    - git-revision-date-localized:
        fallback_to_build_date: true
  ```


## `enable_creation_date`

Default is `false` (because it has a small effect on build time). Enables a *Created* date variables, see [available variables](available-variables.md). This will also add a created date at the bottom of each page in `mkdocs-material` as it has native support (see [overriding a theme](howto/override-a-theme.md)).

=== ":octicons-file-code-16: mkdocs.yml"

  ```yaml
  plugins:
    - git-revision-date-localized:
        enable_creation_date: true
  ```

## `exclude`

Default is empty. Specify a list of page source paths (one per line) that should not have a revision date included (excluded from processing by this plugin). This can be useful for example to remove the revision date from the front page. The source path of a page is relative to your `docs/` folder. You can also use [globs](https://docs.python.org/3/library/glob.html) instead of full source paths. To exclude `docs/subfolder/page.md` specify in your `mkdocs.yml` a line under `exclude:` with `- subfolder/page.md`. Some examples:

=== ":octicons-file-code-16: mkdocs.yml"

  ```yaml
  plugins:
    - git-revision-date-localized:
        exclude:
          - index.md
          - subfolder/page.md
          - another_page.md
          - folder/*
  ```

## `enable_git_follow`

Default is `true`. When enabled it will use `git log --follow` to find the git history. This means git will follow changes if you rename or move the file also.
Despite being a sensible default, there is a known bug with `--follow`: if you have committed an empty version of a file, then `git log --follow` can follow the wrong trail and give wrong results (see [this blogpost](https://blog.plover.com/prog/git-log-follow.html)).

When disabled (by setting it to `false`), each file's history will only consist of its current name and path, it's history from the previous paths or names will not be included.

## `enabled`

Default is `true`. Enables you to deactivate this plugin. A possible use case is local development where you might want faster build times and/or do not have git available. It's recommended to use this option with an environment variable together with a default fallback (introduced in `mkdocs` v1.2.1, see [docs](https://www.mkdocs.org/user-guide/configuration/#environment-variables)). Example:

=== ":octicons-file-code-16: mkdocs.yml"

  ```yaml
  plugins:
    - git-revision-date-localized:
        enabled: !ENV [ENABLED_GIT_REVISION_DATE, True]
  ```

Which enables you to disable the plugin locally using:

```bash
export ENABLED_GIT_REVISION_DATE=false
mkdocs serve
```

## `strict`

Default is `true`. When enabled, the logs will show warnings when something is wrong but a fallback has been used. When disabled, the logger will use the INFO level instead.

- If you want to raise an error when a warning is logged, use [mkdocs strict mode](https://www.mkdocs.org/user-guide/configuration/#strict) (with `mkdocs build --strict`).
- If you are already using [mkdocs strict mode](https://www.mkdocs.org/user-guide/configuration/#strict), but do not care about these warnings, you can set `strict: false` to ensure no errors are raised.

=== ":octicons-file-code-16: mkdocs.yml"

  ```yaml
  plugins:
    - git-revision-date-localized:
        strict: true
  ```

## `ignored_commits_file`

Default is `None`. You can specify a file path (relative to your `mkdocs.yml` directory) that contains a list of commit hashes to ignore
when determining the revision date. The format of the file is the same as the format of
git `blame.ignoreRevsFile`. This can be useful to ignore specific commits that apply formatting updates or other mass changes to the documents.


=== ":octicons-file-code-16: mkdocs.yml"

  ```yaml
  plugins:
    - git-revision-date-localized:
        ignored_commits_file: .git-blame-ignore-revs
  ```

## `enable_parallel_processing`

Default is `true`. When enabled, the plugin will use `multiprocessing` to iterate through all site files in parallel. Disable if you encounter any errors (and open an issue!).

=== ":octicons-file-code-16: mkdocs.yml"

  ```yaml
  plugins:
    - git-revision-date-localized:
        enable_parallel_processing: True
  ```
