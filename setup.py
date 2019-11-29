from setuptools import setup, find_packages

setup(
    name='mkdocs-git-revision-date-plugin',
    version='0.2',
    description='MkDocs plugin for setting revision date from git per markdown file.',
    keywords='mkdocs git meta yaml frontmatter',
    url='https://github.com/zhaoterryy/mkdocs-git-revision-date-plugin/',
    author='Terry Zhao',
    author_email='zhao.terryy@gmail.com',
    license='MIT',
    python_requires='>=3.4',
    install_requires=[
        'mkdocs>=0.17',
        'GitPython',
        'jinja2'
    ],
    packages=find_packages(),
    entry_points={
        'mkdocs.plugins': [
            'git-revision-date = mkdocs_git_revision_date_plugin.plugin:GitRevisionDatePlugin'
        ]
    }
)