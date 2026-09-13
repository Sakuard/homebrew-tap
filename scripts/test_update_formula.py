import importlib.util
import io
from pathlib import Path
import tarfile
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('updater', Path(__file__).with_name('update-formula.py'))
updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updater)

FORMULA = '''class Tbx < Formula
  url "https://github.com/Sakuard/toolbox/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "old"
  test do
    assert_predicate bin/"tbx", :executable?
  end
end
'''


class UpdateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.formula = self.root / 'tbx.rb'
        self.formula.write_text(FORMULA)
        self.archive = self.root / 'toolbox-0.1.1.tar.gz'

    def package(self, version='0.1.1'):
        with tarfile.open(self.archive, 'w:gz') as tar:
            content = (version + '\n').encode()
            info = tarfile.TarInfo('toolbox-0.1.1/VERSION')
            info.size = len(content)
            tar.addfile(info, io.BytesIO(content))

    def test_update_and_rerun(self):
        self.package()
        updater.update('v0.1.1', self.archive, self.formula)
        result = self.formula.read_text()
        self.assertIn('/releases/download/v0.1.1/toolbox-0.1.1.tar.gz', result)
        self.assertIn(updater.hashlib.sha256(self.archive.read_bytes()).hexdigest(), result)
        self.assertIn('shell_output("#{bin}/tbx --version")', result)
        updater.update('v0.1.1', self.archive, self.formula)
        self.assertEqual(result, self.formula.read_text())

    def test_reject_invalid_tag(self):
        for tag in ['v0.1.1-rc.1', '0.1.1', 'v01.1.1', 'v1.2.3\n']:
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                updater.update(tag, self.archive, self.formula)
        self.assertEqual(FORMULA, self.formula.read_text())

    def test_reject_downgrade(self):
        self.formula.write_text(FORMULA.replace('v0.1.0', 'v0.2.0'))
        with self.assertRaisesRegex(ValueError, 'downgrade'):
            updater.update('v0.1.1', self.archive, self.formula)

    def test_reject_wrong_archive_version_without_edit(self):
        self.package('0.2.0')
        with self.assertRaisesRegex(ValueError, 'VERSION'):
            updater.update('v0.1.1', self.archive, self.formula)
        self.assertEqual(FORMULA, self.formula.read_text())

    def test_reject_unexpected_formula_without_edit(self):
        self.package()
        original = FORMULA.replace('  sha256 "old"\n', '')
        self.formula.write_text(original)
        with self.assertRaises(ValueError):
            updater.update('v0.1.1', self.archive, self.formula)
        self.assertEqual(original, self.formula.read_text())
