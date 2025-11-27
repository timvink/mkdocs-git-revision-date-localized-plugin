# Use in Alpine Linux Docker

When using this plugin in a Docker container based on Alpine Linux, you may encounter the following error:

```text
LookupError: Unknown timezone UTC
```

This happens because Alpine Linux, being a minimal distribution, does not include timezone data by default. The [babel](https://github.com/python-babel/babel) library used by this plugin requires timezone information to function correctly.

## Solution

Install the `tzdata` package in your Alpine-based Docker image:

```dockerfile
# Install timezone data
RUN apk add --no-cache tzdata
```

!!! example "Example Dockerfile"

    ```dockerfile
    FROM python:3.12-alpine

    # Install timezone data for babel/mkdocs-git-revision-date-localized-plugin
    RUN apk add --no-cache tzdata git

    # Install MkDocs and plugins
    RUN pip install mkdocs mkdocs-material mkdocs-git-revision-date-localized-plugin

    WORKDIR /docs
    ```

!!! tip "Why this is needed"

    The Python `zoneinfo` module relies on system-level timezone data to resolve timezone names like "UTC". Without the `tzdata` package installed, Alpine Linux does not have this data available, causing the `LookupError`.
