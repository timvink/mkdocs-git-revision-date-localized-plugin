# Contribution Guidelines

Thanks for considering to contribute to this project! Some guidelines:

- Go through the issue list and if needed create a relevant issue to discuss the change design. On disagreements, maintainer(s) will have the final word.
- You can expect a response from a maintainer within 7 days. If you haven’t heard anything by then, feel free to ping the thread.
- This package tries to be as simple as possible for the user (hide any complexity from the user). New options are only added when there is clear value to the majority of users.
- When issues or pull requests are not going to be resolved or merged, they should be closed as soon as possible. This is kinder than deciding this after a long period. Our issue tracker should reflect work to be done.

## Setup

We use [uv to manage dependencies](https://docs.astral.sh/uv/getting-started/installation/).

## Pre-commit Hooks

We use [prek](https://prek.j178.dev/) to manage pre-commit hooks. To install the hooks:

```bash
uv run prek install
```

To run the hooks on all files:

```bash
uv run prek run --all-files
```

## Unit Tests

To run the unit tests, use:

```python
uv run pytest --cov=mkdocs_git_revision_date_localized_plugin --cov-report term-missing tests/
```

If it makes sense, writing tests for your PRs is always appreciated and will help get them merged.

## Manual testing

To quickly serve a test website with your latest changes to the plugin use the sites in our tests suite.
For example:

```python
uv run mkdocs serve -f tests/fixtures/basic_project/mkdocs.yml
```

## Code Style

Make sure your code *roughly* follows [PEP-8](https://www.python.org/dev/peps/pep-0008/)
and keeps things consistent with the rest of the code.

We run `ruff format` to automatically style the code.

We use Google-style docstrings.

## Creating a Release

Releases are published to PyPI automatically via a GitHub Action triggered by publishing a GitHub release.

1. Make sure you are on `master` and up to date:

    ```bash
    git checkout master
    git pull
    ```

2. Bump the version in `src/mkdocs_git_revision_date_localized_plugin/__init__.py` (e.g. `1.5.1` → `1.5.2`).

3. Commit the version bump:

    ```bash
    git commit -am "Bump version to 1.5.2"
    git push
    ```

4. Tag the commit with the new version (prefixed with `v`) and push the tag:

    ```bash
    git tag v1.5.2
    git push origin v1.5.2
    ```

5. Create a new GitHub release for the tag, accept the auto-generated changelog (clean it up where needed), and publish it. Publishing the release triggers the GitHub Action that builds and uploads the package to PyPI.
