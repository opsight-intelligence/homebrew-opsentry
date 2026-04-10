# Homebrew formula for OpSentry
# To use: brew tap opsight-intelligence/opsentry && brew install opsentry
#
# This formula installs the OpSentry CLI and config system.
# After install, run: opsentry init && opsentry install

class Opsentry < Formula
  desc "AI agent security guardrails for engineering teams"
  homepage "https://github.com/opsight-intelligence/opsentry"
  url "https://github.com/opsight-intelligence/opsentry/archive/refs/tags/v1.7.0.tar.gz"
  sha256 "5d2450a05e93a8d13d8bed20351a2036c1ed511dd91f675da48c236176f25f47"
  license "Apache-2.0"

  depends_on "python@3.11"
  depends_on "jq"

  resource "pyyaml" do
    url "https://files.pythonhosted.org/packages/cd/e5/af35f7ea75cf72f2cd079c95ee16797de7cd71f29ea7c68ae5ce7be1edd0/PyYAML-6.0.1.tar.gz"
    sha256 "bfdf460b1736c775f2ba9f6a92bca30bc2095067b8a9d77876d1fad6cc3b4a43"
  end

  resource "jinja2" do
    url "https://files.pythonhosted.org/packages/b2/5e/3a21abf3cd467d7876045335e681d276ac32492febe6d98ad89562d1a7e1/Jinja2-3.1.3.tar.gz"
    sha256 "ac8bd6544d4bb2c9792bf3f159e80bba8c0c418e0348d44c44a9f44dc89b3e47"
  end

  resource "markupsafe" do
    url "https://files.pythonhosted.org/packages/87/5b/aae44c6655f3801e81aa3eef09dbbf012431987ba564d7231722f68df02d/MarkupSafe-2.1.5.tar.gz"
    sha256 "d283d37a890ba4c1ae73ffadf8046435c76e7bc2247bbb63c00bd1a709c6544b"
  end

  def install
    # Install Python deps into libexec
    venv = virtualenv_create(libexec, "python3.11")
    venv.pip_install resources

    # Install the package
    libexec.install Dir["*"]

    # Create wrapper script
    (bin/"opsentry").write <<~EOS
      #!/bin/bash
      export PYTHONPATH="#{libexec}/lib/python3.11/site-packages:$PYTHONPATH"
      exec "#{libexec}/bin/python3" "#{libexec}/bin/opsentry" "$@"
    EOS
  end

  test do
    assert_match "opsentry", shell_output("#{bin}/opsentry --version")
  end
end
