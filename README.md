[![Actions Status](https://github.com/timvink/mkdocs-git-revision-date-localized-plugin/workflows/pytest/badge.svg)](https://github.com/timvink/mkdocs-git-revision-date-localized-plugin/actions)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mkdocs-git-revision-date-localized-plugin)
![PyPI](https://img.shields.io/pypi/v/mkdocs-git-revision-date-localized-plugin)
![PyPI - Downloads](https://img.shields.io/pypi/dm/mkdocs-git-revision-date-localized-plugin)
![GitHub contributors](https://img.shields.io/github/contributors/timvink/mkdocs-git-revision-date-localized-plugin)
![PyPI - License](https://img.shields.io/pypi/l/mkdocs-git-revision-date-localized-plugin)

# mkdocs-git-revision-date-localized-plugin

[MkDocs](https://www.mkdocs.org/) plugin that enables displaying the date of the last git modification of a page. The plugin uses [babel](https://github.com/python-babel/babel/tree/master/babel) and [timeago.js](https://github.com/hustcc/timeago.js) to provide different localized date formats. Initial fork from [mkdocs-git-revision-date-plugin](https://github.com/zhaoterryy/mkdocs-git-revision-date-plugin).

![demo](https://github.com/timvink/mkdocs-git-revision-date-localized-plugin/raw/master/demo_screencast.gif)

(*Example when used together with the [mkdocs-material](https://github.com/squidfunk/mkdocs-material) theme*)

Other related MkDocs plugins:

- [mkdocs-git-authors-plugin](https://github.com/timvink/mkdocs-git-authors-plugin) for displaying the authors from git
- [mkdocs-git-committers-plugin](https://github.com/byrnereese/mkdocs-git-committers-plugin) for displaying authors' github user profiles
- [mkdocs-document-dates](https://github.com/jaywhj/mkdocs-document-dates) for displaying dates based on file creation and modification dates.

## Setup

Install the plugin using `pip3` with the following command:

```bash
pip3 install mkdocs-git-revision-date-localized-plugin
```

Next, add the following lines to your `mkdocs.yml`:

```yaml
plugins:
  - search
  - git-revision-date-localized
```

> If you have no `plugins` entry in your config file yet, you'll likely also want to add the `search` plugin. MkDocs enables it by default if there is no `plugins` entry set.

The [mkdocs-material](https://squidfunk.github.io/mkdocs-material/) theme supports `git-revision-date-localized`. After installing the plugin and updating your `mkdocs.yml` you should see the last revision date on the bottom of your pages. Other mkdocs themes require [additional customization](https://timvink.github.io/mkdocs-git-revision-date-localized-plugin/howto/override-a-theme/).

See the [documentation](https://timvink.github.io/mkdocs-git-revision-date-localized-plugin/index.html) on how to fine-tune the appearance and the date format.

### **Note when using build systems like Github Actions**

This plugin needs access to the last commit that touched a specific file to be able to retrieve the date. By default many CI/CD build systems only retrieve the last commit, which means you might need to change your CI/CD settings:

- Github Actions: set `fetch-depth` to `0` (<a href="https://github.com/actions/checkout">docs</a>)</li>
- Gitlab Runners: set `GIT_DEPTH` to `0` (<a href="https://docs.gitlab.com/ee/ci/pipelines/settings.html#limit-the-number-of-changes-fetched-during-clone">docs</a>)</li>
- Bitbucket pipelines: set `clone: depth: full` (<a href="https://support.atlassian.com/bitbucket-cloud/docs/configure-bitbucket-pipelinesyml/">docs</a>)</li>
- Azure Devops pipelines: set `Agent.Source.Git.ShallowFetchDepth` to something very high like `10e99` ([docs](https://docs.microsoft.com/en-us/azure/devops/pipelines/repos/pipeline-options-for-git?view=azure-devops#shallow-fetch))

*Tip*: You can speed up your builds for large codebases by running git garbage collection (`git gc`) occasionly. You can also use _sparse checkouts_ to only apply the fetch-depth 0 for the folders we're interested (credits Martin [in this tweet](https://x.com/squidfunk/status/1705279829770150291)):

```yaml
# example sparse checkout for github actions
- uses: actions/checkout@v4
  with:
    fetch-depth: 0
    sparse-checkout: |
      docs
      includes
```

## Documentation

See [timvink.github.io/mkdocs-git-revision-date-localized-plugin](https://timvink.github.io/mkdocs-git-revision-date-localized-plugin/index.html).

## Contributing

Contributions are very welcome! Please read [CONTRIBUTING.md](https://github.com/timvink/mkdocs-git-revision-date-localized-plugin/blob/master/CONTRIBUTING.md) before putting in any work.
