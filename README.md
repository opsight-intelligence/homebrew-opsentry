# Homebrew Tap for OpSentry

AI agent security guardrails for engineering teams.

## Install

```bash
brew tap opsight-intelligence/opsentry
brew install opsentry
```

## After Install

```bash
opsentry init      # Interactive setup wizard
opsentry install   # Install guardrails to ~/.claude/
opsentry verify    # Verify installation
opsentry status    # Check version and update availability
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

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the branching model, versioning rules, and how
to bump the packaged OpSentry version.

## Links

- [OpSentry](https://github.com/opsight-intelligence/opsentry) — Main repo
- [OpSight Intelligence](https://opsightintel.com) — Company
