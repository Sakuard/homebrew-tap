#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
ruby -c Formula/tbx.rb
ruby -c Formula/tbx@0.1.0.rb
brew tap --custom-remote Sakuard/tap "$PWD"
# A local tap is a git clone: explicitly include the uncommitted candidate.
cp Formula/*.rb "$(brew --repository Sakuard/tap)/Formula/"
brew install --build-from-source Sakuard/tap/tbx
brew test Sakuard/tap/tbx
