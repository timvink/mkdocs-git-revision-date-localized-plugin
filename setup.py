from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="mkdocs-git-revision-date-localized-plugin",
    version="0.5.2",
    description="Mkdocs plugin that enables displaying the localized date of the last git modification of a markdown file.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="mkdocs git date timeago babel plugin",
    url="https://github.com/timvink/mkdocs-git-revision-date-localized-plugin",
    author="Tim Vink",
    author_email="vinktim@gmail.com",
    license="MIT",
    python_requires=">=3.5",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["mkdocs>=0.17", "GitPython", "jinja2", "babel>=2.7.0"],
    packages=find_packages(),
    entry_points={
        "mkdocs.plugins": [
            "git-revision-date-localized = mkdocs_git_revision_date_localized_plugin.plugin:GitRevisionDateLocalizedPlugin"
        ]
    },
)
