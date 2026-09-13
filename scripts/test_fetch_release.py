import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('fetcher', Path(__file__).with_name('fetch-release.py'))
fetcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fetcher)


class FetchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.formula = Path(self.temp.name) / 'tbx.rb'
        self.original = '  url "https://github.com/Sakuard/toolbox/archive/refs/tags/v0.1.0.tar.gz"\n  sha256 "old"\n'
        self.formula.write_text(self.original)
        self.release = dict(tag_name='v0.1.1', draft=False, prerelease=False,
                            assets=[dict(name='toolbox-0.1.1.tar.gz'), dict(name='SHA256SUMS')])
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode='w:gz') as tar:
            member = tarfile.TarInfo('toolbox-0.1.1/VERSION')
            member.size = 6
            tar.addfile(member, io.BytesIO(b'0.1.1\n'))
        self.data = buf.getvalue()
        self.checksum = hashlib.sha256(self.data).hexdigest() + '  toolbox-0.1.1.tar.gz\n'
        self.calls = []

    def fetch(self, url):
        self.calls.append(url)
        if url.endswith('/latest'):
            return json.dumps(self.release).encode()
        if url.endswith('/SHA256SUMS'):
            return self.checksum.encode()
        return self.data

    def test_full_update_and_noop(self):
        fetcher.sync(self.formula, self.fetch)
        self.assertIn('/releases/download/v0.1.1/', self.formula.read_text())
        result = self.formula.read_text()
        self.calls.clear()
        fetcher.sync(self.formula, self.fetch)
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(result, self.formula.read_text())

    def test_checksum_failure_does_not_edit(self):
        self.data += b'corrupt'
        with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
            fetcher.sync(self.formula, self.fetch)
        self.assertEqual(self.original, self.formula.read_text())

    def test_missing_asset_does_not_edit(self):
        self.release['assets'] = []
        with self.assertRaisesRegex(ValueError, 'missing'):
            fetcher.sync(self.formula, self.fetch)
        self.assertEqual(self.original, self.formula.read_text())

    def test_prerelease_rejected(self):
        self.release['prerelease'] = True
        with self.assertRaises(ValueError):
            fetcher.sync(self.formula, self.fetch)
        self.assertEqual(self.original, self.formula.read_text())

    def test_old_release_does_not_downgrade(self):
        self.release['tag_name'] = 'v0.0.9'
        fetcher.sync(self.formula, self.fetch)
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.original, self.formula.read_text())
