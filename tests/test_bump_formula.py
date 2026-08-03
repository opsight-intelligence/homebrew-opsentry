"""Tests for the automated formula bump.

The bug being defended against is subtle and has already happened twice by hand:
the formula pins a tag *and* a checksum of that tag's tarball, and updating one
without the other produces a formula that fails to install for everybody. So the
tests run the real `Formula/opsentry.rb` through the edits and assert on the
result, rather than on a fixture that could drift away from the real file.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "scripts"))

import bump_formula as bf  # noqa: E402

REAL_FORMULA = (_ROOT / "Formula" / "opsentry.rb").read_text(encoding="utf-8")
REAL_CHANGELOG = (_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
SHA_A = "a" * 64
SHA_B = "b" * 64


def _pinned_tag(formula: str) -> str:
    import re

    return re.search(r"tags/(v[\d.]+)\.tar\.gz", formula).group(1)


def _pinned_sha(formula: str) -> str:
    import re

    return re.search(r'^\s*sha256\s+"([0-9a-f]{64})"', formula, re.MULTILINE).group(1)


class TestBumpUrl:
    def test_it_repoints_the_real_formula(self):
        current = _pinned_tag(REAL_FORMULA)
        out = bf.bump_url(REAL_FORMULA, current, "v9.9.9")
        assert _pinned_tag(out) == "v9.9.9"

    def test_it_leaves_everything_else_alone(self):
        """Only the url line may change -- the wrapper script and test block in
        this formula are far more fragile than the two lines being edited."""
        current = _pinned_tag(REAL_FORMULA)
        out = bf.bump_url(REAL_FORMULA, current, "v9.9.9")
        changed = [
            (a, b)
            for a, b in zip(REAL_FORMULA.splitlines(), out.splitlines())
            if a != b
        ]
        assert len(changed) == 1
        assert changed[0][0].strip().startswith("url ")

    def test_a_wrong_current_version_raises(self):
        """If the workflow's parse of the current version disagreed with the
        file, replacing nothing and reporting success would be the worst
        outcome: a bumped changelog and an unbumped formula."""
        with pytest.raises(bf.BumpError, match="found 0"):
            bf.bump_url(REAL_FORMULA, "v0.0.1", "v9.9.9")


class TestBumpSha256:
    def test_it_replaces_the_digest(self):
        out = bf.bump_sha256(REAL_FORMULA, SHA_A)
        assert _pinned_sha(out) == SHA_A

    def test_it_changes_exactly_one_line(self):
        out = bf.bump_sha256(REAL_FORMULA, SHA_A)
        changed = [
            a for a, b in zip(REAL_FORMULA.splitlines(), out.splitlines()) if a != b
        ]
        assert len(changed) == 1

    def test_multiple_sha256_stanzas_raise(self):
        """Homebrew `resource` blocks each carry a sha256. This formula has none
        today, but it used to (PyYAML, Jinja2, MarkupSafe); if they return, this
        must fail loudly rather than rewrite a resource's digest with the
        tarball's."""
        two = REAL_FORMULA.replace(
            '  license "Apache-2.0"', f'  sha256 "{SHA_B}"\n  license "Apache-2.0"'
        )
        with pytest.raises(bf.BumpError, match="found 2"):
            bf.bump_sha256(two, SHA_A)

    def test_no_sha256_raises(self):
        stripped = "\n".join(
            line for line in REAL_FORMULA.splitlines() if "sha256" not in line
        )
        with pytest.raises(bf.BumpError, match="found 0"):
            bf.bump_sha256(stripped, SHA_A)


class TestNextPatch:
    @pytest.mark.parametrize(
        "current,expected",
        [("0.1.3", "0.1.4"), ("0.1.9", "0.1.10"), ("1.0.0", "1.0.1")],
    )
    def test_it_bumps_the_patch(self, current, expected):
        assert bf.next_patch(current) == expected

    def test_it_does_not_bump_the_minor_at_nine(self):
        """String-sorted version handling would turn 0.1.9 into 0.2.0."""
        assert bf.next_patch("0.1.9") == "0.1.10"

    @pytest.mark.parametrize("bad", ["0.1", "v0.1.3", "0.1.3-rc1", ""])
    def test_a_malformed_version_raises(self, bad):
        with pytest.raises(bf.BumpError):
            bf.next_patch(bad)


class TestChangelog:
    def test_the_entry_goes_above_the_newest_section(self):
        entry = bf.changelog_entry("0.1.4", "v1.9.0", "2026-08-03")
        out = bf.insert_entry(REAL_CHANGELOG, entry)
        assert out.index("## [0.1.4]") < out.index("## [0.1.3]")

    def test_the_preamble_survives(self):
        """The file opens with an explanation that these versions track the tap
        and not OpSentry. An entry inserted at the top would displace it."""
        entry = bf.changelog_entry("0.1.4", "v1.9.0", "2026-08-03")
        out = bf.insert_entry(REAL_CHANGELOG, entry)
        assert out.startswith("# Changelog")
        assert out.index("Keep a Changelog") < out.index("## [0.1.4]")

    def test_the_entry_names_the_opsentry_version(self):
        entry = bf.changelog_entry("0.1.4", "v1.9.0", "2026-08-03")
        assert "v1.9.0" in entry
        assert "## [0.1.4] - 2026-08-03" in entry

    def test_no_version_heading_raises(self):
        with pytest.raises(bf.BumpError):
            bf.insert_entry("# Changelog\n\nnothing here\n", "entry")

    def test_an_unreleased_section_is_not_displaced(self):
        """Keep a Changelog puts `## [Unreleased]` first. A released version
        filed above it would read as though the release predated the
        unreleased work."""
        doc = (
            "# Changelog\n\npreamble\n\n"
            "## [Unreleased]\n\n### Added\n- pending\n\n"
            "## [0.1.3] - 2026-08-03\n\n### Fixed\n- old\n"
        )
        out = bf.insert_entry(doc, bf.changelog_entry("0.1.4", "v1.9.0", "2026-08-03"))
        assert out.index("## [Unreleased]") < out.index("## [0.1.4]")
        assert out.index("## [0.1.4]") < out.index("## [0.1.3]")
        assert "- pending" in out

    def test_an_unreleased_only_changelog_raises(self):
        """Nothing to anchor against means the file is not in the shape this
        script understands; guessing a position would be worse than failing."""
        with pytest.raises(bf.BumpError, match="released"):
            bf.insert_entry("# Changelog\n\n## [Unreleased]\n\n- x\n", "entry")


class TestValidation:
    def test_an_unbumped_pair_raises(self):
        """current == latest means the workflow's comparison went wrong; writing
        a changelog entry for a no-op change would be worse than failing."""
        with pytest.raises(bf.BumpError, match="nothing to bump"):
            bf._validate("v1.8.4", "v1.8.4", SHA_A)

    @pytest.mark.parametrize("bad", ["1.8.4", "v1.8", "latest", ""])
    def test_a_non_tag_raises(self, bad):
        with pytest.raises(bf.BumpError):
            bf._validate("v1.8.4", bad, SHA_A)

    @pytest.mark.parametrize(
        "bad",
        [
            "not-a-sha",
            "A" * 64,  # uppercase: brew writes lowercase
            "a" * 63,  # truncated
            "",
        ],
    )
    def test_a_malformed_digest_raises(self, bad):
        with pytest.raises(bf.BumpError, match="sha256"):
            bf._validate("v1.8.4", "v1.9.0", bad)


class TestEndToEnd:
    """Run the script the way the workflow runs it, over real copies."""

    @pytest.fixture()
    def tap(self, tmp_path):
        (tmp_path / "Formula").mkdir()
        (tmp_path / "Formula" / "opsentry.rb").write_text(REAL_FORMULA, encoding="utf-8")
        (tmp_path / "VERSION").write_text("0.1.3\n", encoding="utf-8")
        (tmp_path / "CHANGELOG.md").write_text(REAL_CHANGELOG, encoding="utf-8")
        return tmp_path

    def _run(self, tap, **over):
        args = {
            "--formula": str(tap / "Formula" / "opsentry.rb"),
            "--version-file": str(tap / "VERSION"),
            "--changelog": str(tap / "CHANGELOG.md"),
            "--current": _pinned_tag(REAL_FORMULA),
            "--latest": "v1.9.0",
            "--sha256": SHA_A,
            "--today": "2026-08-03",
        }
        args.update(over)
        argv = [x for pair in args.items() for x in pair]
        return bf.main(argv)

    def test_all_three_files_are_updated_together(self, tap):
        assert self._run(tap) == 0
        formula = (tap / "Formula" / "opsentry.rb").read_text(encoding="utf-8")
        assert _pinned_tag(formula) == "v1.9.0"
        assert _pinned_sha(formula) == SHA_A
        assert (tap / "VERSION").read_text(encoding="utf-8").strip() == "0.1.4"
        assert "## [0.1.4]" in (tap / "CHANGELOG.md").read_text(encoding="utf-8")

    def test_a_failure_writes_nothing(self, tap):
        """The whole point of validating before writing: a bad checksum must not
        leave the formula pointing at a new tarball with the old digest."""
        before = {p: (tap / p).read_text(encoding="utf-8") for p in
                  ("Formula/opsentry.rb", "VERSION", "CHANGELOG.md")}
        assert self._run(tap, **{"--sha256": "garbage"}) == 1
        for path, text in before.items():
            assert (tap / path).read_text(encoding="utf-8") == text

    def test_a_stale_current_version_writes_nothing(self, tap):
        before = (tap / "CHANGELOG.md").read_text(encoding="utf-8")
        assert self._run(tap, **{"--current": "v0.0.1"}) == 1
        assert (tap / "CHANGELOG.md").read_text(encoding="utf-8") == before

    def test_the_result_is_valid_ruby(self, tap):
        """A formula that does not parse breaks `brew install` for everyone."""
        ruby = subprocess.run(["which", "ruby"], capture_output=True, text=True)
        if ruby.returncode != 0:
            pytest.skip("ruby not available")
        assert self._run(tap) == 0
        check = subprocess.run(
            ["ruby", "-c", str(tap / "Formula" / "opsentry.rb")],
            capture_output=True,
            text=True,
            check=False,
        )
        assert check.returncode == 0, check.stderr

    def test_running_it_twice_is_refused(self, tap):
        """The second run's --current no longer matches the file, so it fails
        instead of double-bumping the tap version."""
        assert self._run(tap) == 0
        assert self._run(tap) == 1
        assert (tap / "VERSION").read_text(encoding="utf-8").strip() == "0.1.4"
