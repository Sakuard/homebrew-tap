class TbxAT010 < Formula
  desc "Personal CLI toolbox powered by fzf"
  homepage "https://github.com/Sakuard/toolbox"
  url "https://github.com/Sakuard/toolbox/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "4979543aee4c29ab85a20450ce0a8cbe613b265ace9497b589cf51f0ccb51b2c"
  license "MIT"

  depends_on "fzf"

  def install
    libexec.install Dir["*"]
    bin.install_symlink libexec/"bin/tbx"
  end

  test do
    assert_predicate bin/"tbx", :executable?
  end
end