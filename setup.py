from setuptools import find_packages, setup

file = open("README.md", "r")
LONG_DESCRIPTION = file.read()
file.close()

file = open("requirements.txt", "r")
DEPENDENCIES = file.readlines()
file.close()

del file

setup(
    name="mkdocs-git-revision-date-localized-plugin",
    version="1.2.0",
    description="Mkdocs plugin that enables displaying the localized date of the last git modification of a markdown file.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    keywords="mkdocs git date timeago babel plugin",
    url="https://github.com/timvink/mkdocs-git-revision-date-localized-plugin",
    author="Tim Vink",
    author_email="vinktim@gmail.com",
    include_package_data=True,
    license="MIT",
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=DEPENDENCIES,
    packages=find_packages(),
    entry_points={
        "mkdocs.plugins": [
            "git-revision-date-localized = mkdocs_git_revision_date_localized_plugin.plugin:GitRevisionDateLocalizedPlugin"
        ]
    },
)
