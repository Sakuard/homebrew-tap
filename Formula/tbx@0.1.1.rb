class TbxAT011 < Formula
  desc "Personal CLI toolbox powered by fzf"
  homepage "https://github.com/Sakuard/toolbox"
  url "https://github.com/Sakuard/toolbox/releases/download/v0.1.1/toolbox-0.1.1.tar.gz"
  sha256 "6001369928c2744d90400d7bc1d35d994349236a8a8d8b7109ec25706ed88152"
  license "BSD-3-Clause"

  depends_on "fzf"

  def install
    libexec.install Dir["*"]
    bin.install_symlink libexec/"bin/tbx"
  end

  test do
    assert_equal "tbx #{version}", shell_output("#{bin}/tbx --version").strip
  end
end
