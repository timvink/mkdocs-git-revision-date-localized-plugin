"""
Time `mkdocs serve`-style builds with this plugin on a generated site.

Builds a temporary git repository with many pages, then runs the build sequence
that `mkdocs serve` runs in one process: on_startup once, an initial build, and
rebuilds that reuse the same plugin object. Only build time is measured; the
dev server and file watcher are left out.

Run from the repository root, on each branch you want to compare:

    uv run python scripts/benchmark_serve_rebuild.py --pages 500 --rebuilds 5

Times are wall-clock seconds; each line shows the median over --rebuilds runs.
"""

import argparse
import logging
import statistics
import tempfile
import time
from pathlib import Path

import git
from mkdocs.commands.build import build
from mkdocs.config import load_config

AUTHOR = "Bench Person <bench@example.com>"


def make_site(root: Path, n_pages: int) -> git.Repo:
    docs = root / "docs"
    docs.mkdir(parents=True)
    (root / "mkdocs.yml").write_text(
        "site_name: bench\nplugins:\n  - git-revision-date-localized:\n      enable_creation_date: true\n"
    )
    repo = git.Repo.init(root)
    with repo.config_writer() as cw:
        cw.set_value("commit", "gpgsign", "false")
        cw.set_value("gc", "auto", "0")

    # Spread the pages over several commits so each file has some history
    batch_size = 10
    for start in range(0, n_pages, batch_size):
        for i in range(start, min(start + batch_size, n_pages)):
            (docs / f"page_{i}.md").write_text(f"# Page {i}\n\n{{{{ git_revision_date_localized }}}}\n")
        repo.git.add(A=True)
        repo.git.commit(message=f"pages {start}", author=AUTHOR, date=str(1600000000 + start))
    return repo


def timed_build(config_file: str, dirty: bool) -> float:
    config = load_config(config_file)
    start = time.perf_counter()
    build(config, dirty=dirty)
    return time.perf_counter() - start


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pages", type=int, default=500)
    parser.add_argument("--rebuilds", type=int, default=5)
    parser.add_argument("--dirty", action="store_true", help="simulate `mkdocs serve --dirty`")
    args = parser.parse_args()

    logging.disable(logging.WARNING)

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        repo = make_site(root, args.pages)
        config_file = str(root / "mkdocs.yml")

        config = load_config(config_file)
        config.plugins.on_startup(command="serve", dirty=args.dirty)
        start = time.perf_counter()
        build(config, dirty=args.dirty)
        initial = time.perf_counter() - start

        page = root / "docs/page_0.md"
        no_commit, after_commit = [], []
        for i in range(args.rebuilds):
            # A save without a commit: the common case while writing
            page.write_text(page.read_text() + "edit\n")
            no_commit.append(timed_build(config_file, args.dirty))

            # A save followed by a commit
            page.write_text(page.read_text() + "edit\n")
            repo.git.commit(page, message=f"edit {i}", author=AUTHOR, date=str(1700000000 + i))
            after_commit.append(timed_build(config_file, args.dirty))

    mode = "serve --dirty" if args.dirty else "serve"
    print(f"{mode}, {args.pages} pages, median of {args.rebuilds} rebuilds")
    print(f"  initial build            {initial:7.2f}s")
    print(f"  rebuild, no new commit   {statistics.median(no_commit):7.2f}s")
    print(f"  rebuild after a commit   {statistics.median(after_commit):7.2f}s")


if __name__ == "__main__":
    main()
