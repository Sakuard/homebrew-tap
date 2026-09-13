"""Fetch the newest published stable release; never edit on download failure."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import urllib.request

spec = importlib.util.spec_from_file_location('updater', Path(__file__).with_name('update-formula.py'))
updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updater)
REPO = 'Sakuard/toolbox'


def download(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'Sakuard-homebrew-tap'})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def sync(formula, fetch=download):
    release = json.loads(fetch(f'https://api.github.com/repos/{REPO}/releases/latest'))
    tag = release['tag_name']
    if release['draft'] or release['prerelease'] or not re.fullmatch(
        r'v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)', tag
    ):
        raise ValueError('Expected a published stable vX.Y.Z release')
    current = re.search(r'/v(\d+\.\d+\.\d+)(?:/|\.tar\.gz)', formula.read_text())
    if not current:
        raise ValueError('Cannot determine current formula version')
    version = tag[1:]
    if tuple(map(int, version.split('.'))) <= tuple(map(int, current[1].split('.'))):
        print(f'No upgrade needed (installed formula: {current[1]}, latest release: {version})')
        return
    filename = f'toolbox-{version}.tar.gz'
    assets = {asset['name'] for asset in release['assets']}
    if not {filename, 'SHA256SUMS'} <= assets:
        raise ValueError('Release is missing package or SHA256SUMS')
    base = f'https://github.com/{REPO}/releases/download/{tag}'
    checksum_text = fetch(f'{base}/SHA256SUMS').decode()
    expected = re.fullmatch(r'([0-9a-f]{64})  ' + re.escape(filename) + r'\n?', checksum_text)
    if not expected:
        raise ValueError('Invalid checksum manifest')
    data = fetch(f'{base}/{filename}')
    if hashlib.sha256(data).hexdigest() != expected[1]:
        raise ValueError('Package checksum mismatch')
    with tempfile.TemporaryDirectory() as directory:
        archive = Path(directory) / filename
        archive.write_bytes(data)
        updater.update(tag, archive, formula)
    print(f'Updated formula to {tag}')


if __name__ == '__main__':
    sync(Path(__file__).resolve().parents[1] / 'Formula/tbx.rb')
