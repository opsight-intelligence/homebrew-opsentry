# Homebrew formula for OpSentry
# To use: brew tap opsight-intelligence/opsentry && brew install opsentry
#
# This formula installs the OpSentry CLI wrapper + all guardrail scripts
# from the community repo. After install, run: opsentry install

class Opsentry < Formula
  desc "AI agent security guardrails for engineering teams"
  homepage "https://github.com/opsight-intelligence/opsentry"
  url "https://github.com/opsight-intelligence/opsentry/archive/refs/tags/v1.8.0.tar.gz"
  sha256 "58ff600c66a22df847669f5d3088476e14b4142cbbad10f6bcb0b30106e2e383"
  license "Apache-2.0"

  depends_on "jq"
  depends_on "python@3.11"

  def install
    # Install the entire community repo tree into libexec. Scripts inside
    # resolve their own SCRIPT_DIR relative to their own location, so
    # nothing needs to be rewritten after install.
    libexec.install Dir["*"]

    # Create a thin CLI wrapper that dispatches to the appropriate script
    # inside libexec/opsentry/. Subcommands: install, verify, update,
    # patrol, test, --version, --help.
    (bin/"opsentry").write <<~EOS
      #!/bin/bash
      set -euo pipefail
      OPSENTRY_LIBEXEC="#{libexec}"
      cmd="${1:-}"
      if [ "$#" -gt 0 ]; then shift; fi

      case "$cmd" in
        install)
          exec bash "$OPSENTRY_LIBEXEC/opsentry/install.sh" "$@"
          ;;
        verify)
          exec bash "$OPSENTRY_LIBEXEC/opsentry/verify.sh" "$@"
          ;;
        update)
          exec bash "$OPSENTRY_LIBEXEC/opsentry/update.sh" "$@"
          ;;
        patrol)
          exec bash "$OPSENTRY_LIBEXEC/opsentry/patrol.sh" "$@"
          ;;
        test)
          exec bash "$OPSENTRY_LIBEXEC/opsentry/test.sh" "$@"
          ;;
        --version|-v|version)
          cat "$OPSENTRY_LIBEXEC/VERSION"
          ;;
        ""|--help|-h|help)
          printf '%s\\n' \\
            "opsentry -- AI agent security guardrails for Claude Code" \\
            "" \\
            "Usage: opsentry <command> [args]" \\
            "" \\
            "Commands:" \\
            "  install    Install guardrails to ~/.claude/" \\
            "  verify     Verify installation integrity" \\
            "  update     Pull the latest version and re-install" \\
            "  patrol     Run the compliance patrol audit" \\
            "  test       Run the hook test suite" \\
            "  --version  Show installed version" \\
            "  --help     Show this help"
          exit 0
          ;;
        *)
          echo "opsentry: unknown command '$cmd'" >&2
          echo "Run 'opsentry --help' for usage." >&2
          exit 1
          ;;
      esac
    EOS
  end

  test do
    # Verify the wrapper is wired up and VERSION is readable.
    assert_match(/^\d+\.\d+\.\d+$/, shell_output("#{bin}/opsentry --version").strip)
    # Verify the help text mentions the install subcommand.
    assert_match "install", shell_output("#{bin}/opsentry --help")
  end
end
