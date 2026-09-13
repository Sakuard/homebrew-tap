#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
for formula in Formula/*.rb; do
  ruby -c "$formula"
done
brew tap --custom-remote Sakuard/tap "$PWD"
# A local tap is a git clone: explicitly include the uncommitted candidate.
cp Formula/*.rb "$(brew --repository Sakuard/tap)/Formula/"
brew install --build-from-source Sakuard/tap/tbx
brew test Sakuard/tap/tbx
