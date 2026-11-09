"""Build, validate, and zip an isolated production release. Does not deploy."""
import argparse
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

SOURCE = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('archive', type=Path)
args = parser.parse_args()
archive = args.archive.resolve()
if archive.exists():
    raise SystemExit('Choose a new archive name; existing release will not be overwritten.')
archive.parent.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix='109-production-', dir=archive.parent) as temp:
    root = Path(temp)
    assert root.resolve().parent == archive.parent, 'Temporary build must stay beside the release archive.'
    subprocess.run([sys.executable, str(SOURCE / 'tools/generate.py'), '--production', '--output-dir', str(root)], check=True)
    subprocess.run([sys.executable, str(SOURCE / 'tools/check_site.py'), '--production', '--root', str(root)], check=True)
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as bundle:
        for file in sorted(root.rglob('*')):
            if file.is_file():
                bundle.write(file, file.relative_to(root).as_posix())
digest = hashlib.sha256(archive.read_bytes()).hexdigest()
archive.with_suffix('.zip.sha256').write_text(f'{digest}  {archive.name}\n', encoding='utf-8')
print(f'Validated production release: {archive}')
print('No deployment or DNS change performed. Preview source files remain unchanged.')
