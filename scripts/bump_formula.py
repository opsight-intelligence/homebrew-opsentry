#!/usr/bin/env python3
"""Point the formula at a new OpSentry release.

Used by `.github/workflows/bump-formula.yml`, which supplies the version it
found and the checksum it computed. Kept as a script rather than inline shell in
the workflow for one reason: this logic can be run and tested on a laptop, and
a `sed` expression buried in a YAML block scalar cannot.

The edits are pure string functions taking and returning text, so the tests
exercise them without touching the filesystem or the network. Only `main` reads
or writes files.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
TAG = re.compile(r"^v\d+\.\d+\.\d+$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


class BumpError(RuntimeError):
    """The formula, version file, or changelog was not in the expected shape."""


def bump_url(formula: str, current: str, latest: str) -> str:
    """Repoint the `url` line from tag `current` to tag `latest`.

    Anchored on the `tags/<v>.tar.gz` fragment rather than the bare version
    string, so a version that also appeared in a comment or in the `test do`
    block could not be rewritten by accident.
    """
    needle = f"tags/{current}.tar.gz"
    if formula.count(needle) != 1:
        raise BumpError(
            f"expected exactly one {needle!r} in the formula, "
            f"found {formula.count(needle)}"
        )
    return formula.replace(needle, f"tags/{latest}.tar.gz")


def bump_sha256(formula: str, sha: str) -> str:
    """Replace the formula's `sha256` stanza.

    Matches only a `sha256 "..."` line at the start of a line (allowing
    indentation). Homebrew resource blocks can each carry their own `sha256`;
    requiring exactly one match means this fails loudly rather than silently
    rewriting the wrong one if resources are ever added back.
    """
    pattern = re.compile(r'^(\s*sha256\s+)"[0-9a-f]{64}"', re.MULTILINE)
    matches = pattern.findall(formula)
    if len(matches) != 1:
        raise BumpError(
            f"expected exactly one sha256 stanza in the formula, found {len(matches)}"
        )
    return pattern.sub(lambda m: f'{m.group(1)}"{sha}"', formula, count=1)


def next_patch(version: str) -> str:
    """Bump the patch component of the tap's own version."""
    if not SEMVER.match(version):
        raise BumpError(f"tap VERSION {version!r} is not MAJOR.MINOR.PATCH")
    major, minor, patch = version.split(".")
    return f"{major}.{minor}.{int(patch) + 1}"


def changelog_entry(tap_version: str, latest: str, today: str) -> str:
    """Render the Keep a Changelog entry for one automated bump."""
    return (
        f"## [{tap_version}] - {today}\n"
        f"\n"
        f"### Fixed\n"
        f"- Bumped the formula to OpSentry `{latest}` with a recomputed "
        f"`sha256`, so `brew install opsentry` serves the current release.\n"
        f"  Opened automatically by the `bump-formula` workflow.\n"
        f"\n"
    )


def insert_entry(changelog: str, entry: str) -> str:
    """Insert an entry above the newest released version section.

    Anchors on a `## [` heading rather than the top of the file, so the
    preamble -- which explains that these versions track the tap and not
    OpSentry -- stays on top.

    An `## [Unreleased]` heading is skipped rather than displaced. Keep a
    Changelog puts it first, and a released version filed above it would read as
    though the release came before the unreleased work. This file currently has
    it out of position, which is exactly why the rule is enforced here instead
    of relying on where it happens to sit.
    """
    heading = re.compile(r"^## \[(?!Unreleased\])", re.MULTILINE | re.IGNORECASE)
    match = heading.search(changelog)
    if match is None:
        raise BumpError("no released '## [<version>]' heading found in the changelog")
    index = match.start()
    return changelog[:index] + entry + changelog[index:]


def _validate(current: str, latest: str, sha: str) -> None:
    for name, value in (("current", current), ("latest", latest)):
        if not TAG.match(value):
            raise BumpError(f"--{name} {value!r} is not a vMAJOR.MINOR.PATCH tag")
    if current == latest:
        raise BumpError(f"--current and --latest are both {current!r}; nothing to bump")
    if not SHA256.match(sha):
        raise BumpError(f"--sha256 {sha!r} is not 64 lowercase hex characters")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--formula", type=Path, required=True)
    parser.add_argument("--version-file", type=Path, required=True)
    parser.add_argument("--changelog", type=Path, required=True)
    parser.add_argument("--current", required=True, help="tag the formula pins now")
    parser.add_argument("--latest", required=True, help="tag to move it to")
    parser.add_argument("--sha256", required=True, help="digest of the new tarball")
    parser.add_argument(
        "--today",
        default=datetime.now(timezone.utc).date().isoformat(),
        help="date for the changelog entry (overridable so tests are stable)",
    )
    args = parser.parse_args(argv)

    try:
        _validate(args.current, args.latest, args.sha256)

        formula = args.formula.read_text(encoding="utf-8")
        formula = bump_url(formula, args.current, args.latest)
        formula = bump_sha256(formula, args.sha256)

        tap_version = next_patch(args.version_file.read_text(encoding="utf-8").strip())

        changelog = insert_entry(
            args.changelog.read_text(encoding="utf-8"),
            changelog_entry(tap_version, args.latest, args.today),
        )
    except (BumpError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    # Written only after every edit has succeeded, so a failure partway through
    # cannot leave the formula bumped but the changelog untouched.
    args.formula.write_text(formula, encoding="utf-8")
    args.version_file.write_text(f"{tap_version}\n", encoding="utf-8")
    args.changelog.write_text(changelog, encoding="utf-8")

    print(f"formula {args.current} -> {args.latest}; tap version -> {tap_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
