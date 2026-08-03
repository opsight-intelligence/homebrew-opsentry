# Homebrew Tap for OpSentry

AI agent security guardrails for engineering teams.

## Install

```bash
brew tap opsight-intelligence/opsentry
brew install opsentry
```

## After Install

```bash
opsentry install   # Install guardrails to ~/.claude/
opsentry verify    # Verify installation integrity
opsentry update    # Pull the latest version and re-install
opsentry patrol    # Run the compliance patrol audit
opsentry test      # Run the hook test suite
opsentry --version # Show the installed version
```

## Versioning

The `VERSION` file and `vX.Y.Z` tags in this repository track the **tap**, not OpSentry
itself. The OpSentry release a given formula installs is recorded in
[CHANGELOG.md](CHANGELOG.md) and set by the `url` in
[`Formula/opsentry.rb`](Formula/opsentry.rb).

To see which version you have installed:

```bash
opsentry --version
```

### Keeping the formula current

Releasing OpSentry does not touch this repository, so the formula used to be
bumped by hand — and twice went stale, once by three releases. The
[`bump-formula`](.github/workflows/bump-formula.yml) workflow now runs daily: it
compares the newest OpSentry tag against the version this formula pins and, when
they differ, recomputes the tarball `sha256` and opens a pull request.

It opens a PR rather than pushing, because merging one changes what every
`brew install opsentry` downloads. Review it, merge it, then cut the tap release
as usual. To check immediately instead of waiting for the schedule, run the
workflow from the Actions tab.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the branching model, versioning rules, and how
to bump the packaged OpSentry version.

## Links

- [OpSentry](https://github.com/opsight-intelligence/opsentry) — Main repo
- [OpSight Intelligence](https://opsightintel.com) — Company
