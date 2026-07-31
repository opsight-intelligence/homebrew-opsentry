# Contributing

This repository is the Homebrew tap for OpSentry. It packages releases of
[opsight-intelligence/opsentry](https://github.com/opsight-intelligence/opsentry);
guardrail changes belong in that repo, not here.

## Branching model (Git Flow)

| Branch | Role |
|--------|------|
| `main` | Production. Only ever updated by merging `release/*` or `hotfix/*`. |
| `develop` | Integration branch. Default target for PRs. |
| `feature/<name>` | Branched from `develop`, merged back into `develop`. |
| `bugfix/<name>` | Non-urgent fixes. Branched from `develop`. |
| `release/<version>` | Cut from `develop`, merged into `main` **and** back into `develop`. |
| `hotfix/<version>` | Cut from `main` for urgent fixes, merged into `main` **and** `develop`. |

Never commit directly to `main` or `develop`.

## Versioning

The `VERSION` file tracks the **tap**, not OpSentry. A formula bump that packages a new
upstream OpSentry release is a change to this tap and gets its own tap version.

- **MAJOR** — breaking changes to the installed CLI surface (renamed or removed subcommands)
- **MINOR** — packaging a new upstream OpSentry minor/major, new subcommands, new dependencies
- **PATCH** — upstream patch bumps, resource refreshes, checksum corrections, docs

Every commit bumps `VERSION`. Releases that land on `main` are tagged `v<version>`.

## Required with every change

A change is not complete until all four land in the same commit:

1. **Formula** — the change itself
2. **`VERSION`** — bumped per SemVer
3. **`CHANGELOG.md`** — entry under `## [Unreleased]`, recording which upstream OpSentry
   version the formula packages
4. **Docs** — `README.md` updated for any change to install steps or available subcommands

## Bumping the packaged OpSentry version

1. Update `url` in `Formula/opsentry.rb` to the new upstream tag
2. Recompute the checksum and update `sha256`
3. Verify locally: `brew install --build-from-source Formula/opsentry.rb && brew test opsentry`
4. Bump `VERSION`, add the changelog entry, update `README.md` if the CLI surface changed

## Commit messages

Conventional Commits, with the resulting version in brackets:

```
type(scope): subject [vX.Y.Z]
```

`type` is one of `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`,
`build`, `ci`. Subject is imperative and under 72 characters.

Examples:

- `feat(tap): package OpSentry 1.9.0 [v0.2.0]`
- `fix(tap): correct sha256 for the 1.8.0 tarball [v0.1.2]`

## Releasing

1. Cut `release/<version>` from `develop`
2. Roll `## [Unreleased]` into a `## [<version>] - <YYYY-MM-DD>` section
3. Open a PR into `main`, merge, then tag `v<version>`
4. Merge `main` back into `develop`
5. Delete the release branch locally and on the remote, and close any PRs the release
   supersedes
