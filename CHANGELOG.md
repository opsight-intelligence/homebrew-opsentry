# Changelog

All notable changes to this tap are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Note: this version tracks the **tap**, not OpSentry itself. The OpSentry version a
given formula installs is recorded in each entry below and lives in
[`Formula/opsentry.rb`](Formula/opsentry.rb).

## [0.1.3] - 2026-08-03

### Fixed
- Bumped to OpSentry `v1.8.4`. The formula went stale again within the hour of
  being fixed, because releasing the source repository does not touch this tap —
  which is precisely the gap 0.1.2 described. Until the bump is automated in the
  OpSentry release flow, every release needs a matching PR here.

## [0.1.2] - 2026-08-03

### Fixed
- **Formula pinned to a two-release-old tarball.** `url` fetched
  `v1.8.0` while the source repository had shipped v1.8.1, v1.8.2 and v1.8.3, so
  `brew install opsentry` served older guardrails than `git clone` did. Nothing
  updates this formula when OpSentry releases; that is now tracked as a gap in
  the release process rather than left to be noticed by a user.
- Bumped to `v1.8.3` with a recomputed `sha256`
  (`c196f6cd...`, verified against the tarball GitHub serves).

## [Unreleased]

## [0.1.1] - 2026-08-01
### Added
- `CHANGELOG.md` and `CONTRIBUTING.md` establishing the Git Flow, semantic versioning,
  changelog, and documentation policy for this tap.

### Changed
- `README.md` gains Versioning and Contributing sections.

## [0.1.0] - 2026-06-11
### Added
- `VERSION` file, establishing semantic versioning for the tap itself independently of
  the OpSentry release it packages.

### Fixed
- **`Formula/opsentry.rb`:** rewritten for the community repo layout. The formula now
  installs the full repo tree into `libexec` and ships a thin `bin/opsentry` wrapper
  that dispatches to `install`, `verify`, `update`, `patrol`, and `test`.
- **`Formula/opsentry.rb`:** refreshed the PyYAML, Jinja2, and MarkupSafe resources to
  current stable versions.

## [0.0.2] - 2026-04-11
### Changed
- Formula bumped to package OpSentry 1.8.0.

## [0.0.1] - 2026-04-09
### Added
- Initial Homebrew formula packaging OpSentry 1.7.0.

[Unreleased]: https://github.com/opsight-intelligence/homebrew-opsentry/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/opsight-intelligence/homebrew-opsentry/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/opsight-intelligence/homebrew-opsentry/releases/tag/v0.1.0
