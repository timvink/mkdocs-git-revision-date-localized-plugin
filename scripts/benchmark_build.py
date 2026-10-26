"""
Benchmark a full `mkdocs build` with this plugin, with creation dates off and on.

The script creates a temporary git repository with N pages spread over several
commits, then times `mkdocs.commands.build.build` a few times per configuration
and reports the median wall-clock time in seconds. It also reports the median
CPU time (user + sys) of child processes: the multiprocessing workers and the
`git` processes they run. CPU time varies less than wall time on a busy machine.

Run it from the repository root:

    uv run python scripts/benchmark_build.py
    uv run python scripts/benchmark_build.py --pages 1000 --repeats 5

To compare against another version of the plugin, copy this script outside the
repository and run it with that version installed.
"""

import argparse
import logging
import resource
import statistics
import subprocess
import tempfile
import time
from pathlib import Path

from mkdocs.commands.build import build
from mkdocs.config import load_config

MKDOCS_YML = """\
site_name: benchmark
plugins:
  - git-revision-date-localized:
      enable_creation_date: {enable_creation_date}
"""


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


def create_repo(repo: Path, pages: int, commits: int) -> None:
    """Create a git repo whose pages are added over `commits` commits, then edited once."""
    docs = repo / "docs"
    docs.mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    for key, value in [
        ("user.name", "Benchmark"),
        ("user.email", "benchmark@example.com"),
        ("commit.gpgsign", "false"),
        ("gc.auto", "0"),
    ]:
        git(repo, "config", key, value)

    (docs / "index.md").write_text("# Home\n")
    per_commit = max(1, pages // commits)
    for start in range(0, pages, per_commit):
        for i in range(start, min(start + per_commit, pages)):
            (docs / f"page_{i:05d}.md").write_text(f"# Page {i}\n\nCreated {{{{ git_creation_date_localized }}}}\n")
        git(repo, "add", "docs")
        git(repo, "commit", "-q", "-m", f"Add pages from {start}")

    # Edit every other page so creation and last revision commits differ
    for i in range(0, pages, 2):
        with open(docs / f"page_{i:05d}.md", "a") as f:
            f.write("\nEdited {{ git_revision_date_localized }}\n")
    git(repo, "add", "docs")
    git(repo, "commit", "-q", "-m", "Edit pages")


def children_cpu_seconds() -> float:
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    return usage.ru_utime + usage.ru_stime


def time_builds(repo: Path, enable_creation_date: bool, repeats: int) -> tuple[list[float], list[float]]:
    """Return the wall-clock and child CPU seconds of each build."""
    config_file = repo / "mkdocs.yml"
    config_file.write_text(MKDOCS_YML.format(enable_creation_date=str(enable_creation_date).lower()))
    wall, cpu = [], []
    for _ in range(repeats):
        config = load_config(str(config_file), site_dir=str(repo / "site"))
        start_wall, start_cpu = time.perf_counter(), children_cpu_seconds()
        # MkDocs reuses plugin instances across load_config() calls, and build() does not
        # call on_startup. Call it like `mkdocs build` does, so the plugin clears its
        # commit caches and every build reads the git history again.
        config.plugins.on_startup(command="build", dirty=False)
        build(config)
        config.plugins.on_shutdown()
        wall.append(time.perf_counter() - start_wall)
        cpu.append(children_cpu_seconds() - start_cpu)
    return wall, cpu


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--pages", type=int, default=500, help="number of pages (default: 500)")
    parser.add_argument("--commits", type=int, default=10, help="commits to spread the pages over (default: 10)")
    parser.add_argument("--repeats", type=int, default=3, help="builds per configuration (default: 3)")
    args = parser.parse_args()

    # Pages without a git history or with a newer creation date log warnings; keep the output readable
    logging.getLogger("mkdocs").setLevel(logging.ERROR)

    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "repo"
        create_repo(repo, args.pages, args.commits)
        print(f"{args.pages} pages, {args.commits} commits, {args.repeats} builds per configuration")
        print(f"{'enable_creation_date':<22}{'wall median (s)':>17}{'wall min (s)':>14}{'child CPU median (s)':>22}")
        for enable_creation_date in (False, True):
            wall, cpu = time_builds(repo, enable_creation_date, args.repeats)
            print(
                f"{str(enable_creation_date).lower():<22}{statistics.median(wall):>17.2f}"
                f"{min(wall):>14.2f}{statistics.median(cpu):>22.2f}"
            )


if __name__ == "__main__":
    main()
