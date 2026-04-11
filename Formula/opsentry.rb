# Homebrew formula for OpSentry
# To use: brew tap opsight-intelligence/opsentry && brew install opsentry
#
# This formula installs the OpSentry CLI and config system.
# After install, run: opsentry init && opsentry install

class Opsentry < Formula
  desc "AI agent security guardrails for engineering teams"
  homepage "https://github.com/opsight-intelligence/opsentry"
  url "https://github.com/opsight-intelligence/opsentry/archive/refs/tags/v1.8.0.tar.gz"
  sha256 "58ff600c66a22df847669f5d3088476e14b4142cbbad10f6bcb0b30106e2e383"
  license "Apache-2.0"

  depends_on "python@3.11"
  depends_on "jq"

  resource "pyyaml" do
    url "https://files.pythonhosted.org/packages/05/8e/961c0007c59b8dd7729d542c61a4d537767a59645b82a0b521206e1e25c2/pyyaml-6.0.3.tar.gz"
    sha256 "d76623373421df22fb4cf8817020cbb7ef15c725b9d5e45f17e189bfc384190f"
  end

  resource "jinja2" do
    url "https://files.pythonhosted.org/packages/df/bf/f7da0350254c0ed7c72f3e33cef02e048281fec7ecec5f032d4aac52226b/jinja2-3.1.6.tar.gz"
    sha256 "0137fb05990d35f1275a587e9aee6d56da821fc83491a0fb838183be43f66d6d"
  end

  resource "markupsafe" do
    url "https://files.pythonhosted.org/packages/7e/99/7690b6d4034fffd95959cbe0c02de8deb3098cc577c67bb6a24fe5d7caa7/markupsafe-3.0.3.tar.gz"
    sha256 "722695808f4b6457b320fdc131280796bdceb04ab50fe1795cd540799ebe1698"
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
