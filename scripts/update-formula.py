"""Update the stable formula using a verified release archive."""
import hashlib
import pathlib
import re
import sys
import tarfile


def update(tag, archive, formula):
    if not re.fullmatch(r"v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", tag):
        raise ValueError("Expected a stable vX.Y.Z tag")
    version = tag[1:]
    source = formula.read_text()
    current = re.search(r'/v(\d+\.\d+\.\d+)(?:/|\.tar\.gz)', source)
    if not current:
        raise ValueError("Cannot determine existing formula version")
    if tuple(map(int, version.split('.'))) < tuple(map(int, current[1].split('.'))):
        raise ValueError("Refusing to downgrade the stable formula")
    with tarfile.open(archive) as package:
        member = package.extractfile(f"toolbox-{version}/VERSION")
        if member is None or member.read().decode().strip() != version:
            raise ValueError("Archive VERSION does not match release tag")
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    url = f"https://github.com/Sakuard/toolbox/releases/download/{tag}/toolbox-{version}.tar.gz"
    for pattern, replacement in [
        (r'^  url ".*"$', f'  url "{url}"'),
        (r'^  sha256 ".*"$', f'  sha256 "{checksum}"'),
    ]:
        source, count = re.subn(pattern, replacement, source, flags=re.MULTILINE)
        if count != 1:
            raise ValueError("Expected exactly one formula URL and checksum")
    # v0.1.0 predates the --version flag; enable this test with the new package.
    source = source.replace('    assert_predicate bin/"tbx", :executable?',
                            '    assert_equal "tbx #{version}", shell_output("#{bin}/tbx --version").strip')
    formula.write_text(source)


if __name__ == '__main__':
    update(sys.argv[1], pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3]))
