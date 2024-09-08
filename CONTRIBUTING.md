# Contribution Guidelines

Thanks for considering to contribute to this project! Some guidelines:

- Go through the issue list and if needed create a relevant issue to discuss the change design. On disagreements, maintainer(s) will have the final word.
- You can expect a response from a maintainer within 7 days. If you haven’t heard anything by then, feel free to ping the thread.
- This package tries to be as simple as possible for the user (hide any complexity from the user). New options are only added when there is clear value to the majority of users.
- When issues or pull requests are not going to be resolved or merged, they should be closed as soon as possible. This is kinder than deciding this after a long period. Our issue tracker should reflect work to be done.

## Unit Tests

Make sure to install an editable version before running the tests:

```python
pip install -r requirement_dev.txt
pip install -e .
pytest --cov=mkdocs_git_revision_date_localized_plugin --cov-report term-missing tests/
```

If it makes sense, writing tests for your PRs is always appreciated and will help get them merged.

## Manual testing

To quickly serve a test website with your latest changes to the plugin use the sites in our tests suite.
For example:

```python
pip install -r tests/test_requirements.txt
pip install -e .
mkdocs serve -f tests/fixtures/basic_project/mkdocs.yml
```

## Code Style

Make sure your code *roughly* follows [PEP-8](https://www.python.org/dev/peps/pep-0008/)
and keeps things consistent with the rest of the code.

We use Google-style docstrings.
