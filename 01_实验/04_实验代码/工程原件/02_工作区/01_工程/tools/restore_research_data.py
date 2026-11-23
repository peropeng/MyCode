"""Restore sealed research inputs and evidence without running experiments.

Archives come from the private release named in manifests/research_data.json.
Every archive and regular file is bound by size and SHA256. Existing differing
files are never overwritten. --verify-only performs no network access.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'manifests/research_data.json'
WINDOWS_RESERVED = {'CON', 'PRN', 'AUX', 'NUL', *('COM' + str(i) for i in range(1, 10)),
                    *('LPT' + str(i) for i in range(1, 10))}


def sha256_file(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def relative_path(value):
    """Require a portable literal relative path, including on Windows."""
    if not isinstance(value, str) or not value or any(c in value for c in ('\\', ':', '\0')):
        raise ValueError('Unsafe relative path: ' + repr(value))
    path = PurePosixPath(value)
    if path.is_absolute() or value.startswith('/') or any(p in ('', '.', '..') for p in value.split('/')):
        raise ValueError('Unsafe relative path: ' + repr(value))
    for part in path.parts:
        if part.rstrip(' .') != part or part.split('.')[0].upper() in WINDOWS_RESERVED:
            raise ValueError('Nonportable path component: ' + repr(part))
    return path


def local_path(base, relative):
    """Reject filesystem links and make the containment check before writes."""
    parts = relative_path(relative).parts
    target = base.joinpath(*parts)
    if not target.resolve().is_relative_to(base.resolve()):
        raise ValueError('Path leaves intended directory: ' + str(target))
    current = base
    for part in parts:
        current = current / part
        if current.is_symlink() or (hasattr(current, 'is_junction') and current.is_junction()):
            raise ValueError('Filesystem link refused: ' + str(current))
    return target


def check_file(path, row):
    if not path.is_file() or path.stat().st_size != row['size'] or sha256_file(path) != row['sha256']:
        raise RuntimeError('Missing or differing sealed file: ' + str(path))


def bundle_files(bundle):
    result = {}
    folded = set()
    for row in bundle['files']:
        path = relative_path(row['path']).as_posix()
        if path in result or path.casefold() in folded:
            raise ValueError('Duplicate/case-colliding manifest path: ' + path)
        if type(row['size']) is not int or row['size'] < 0 or not re.fullmatch('[0-9a-f]{64}', row['sha256']):
            raise ValueError('Invalid sealed file identity: ' + path)
        result[path] = row
        folded.add(path.casefold())
    return result


def output_root(bundle):
    relative = relative_path(bundle['restore_to'])
    if relative.parts[:2] != ('.rebuild', 'paper-inputs') or len(relative.parts) < 3:
        raise ValueError('Research output must be below .rebuild/paper-inputs')
    return local_path(ROOT, relative.as_posix())


def download_archive(source, bundle):
    asset = bundle['asset_name']
    if not re.fullmatch(r'[A-Za-z0-9._+\-]+', asset):
        raise ValueError('Release asset must be a literal filename')
    if bundle['local_path'] != '.restore-cache/' + asset:
        raise ValueError('Archive cache path must match the release asset')
    cache = local_path(ROOT, '.restore-cache')
    archive = local_path(ROOT, bundle['local_path'])
    if not archive.exists():
        cache.mkdir(parents=True, exist_ok=True)
        gh = shutil.which('gh')
        if gh is None:
            fixed = Path('C:/Users/Administrator/.local/bin/gh.exe')
            if not fixed.is_file():
                raise RuntimeError('GitHub CLI is required to download private release assets')
            gh = str(fixed)
        # No --clobber; commands run serially and never overwrite cached files.
        subprocess.run([gh, 'release', 'download', source['release_tag'], '--repo', source['repo'],
                        '--pattern', asset, '--dir', str(cache)], check=True)
    check_file(archive, bundle)
    return archive


def restore_bundle(source, bundle):
    expected = bundle_files(bundle)
    destination = output_root(bundle)
    archive_path = download_archive(source, bundle)
    prefix = relative_path(bundle['strip_prefix']).as_posix()
    seen = set()
    created = reused = 0
    with tarfile.open(archive_path, 'r|gz') as archive:
        for member in archive:
            name = relative_path(member.name.rstrip('/')).as_posix()
            if not (member.isfile() or member.isdir()):
                raise ValueError('Archive links and special members are refused: ' + name)
            if name == prefix or prefix.startswith(name + '/'):
                if not member.isdir():
                    raise ValueError('Archive prefix ancestor must be a directory')
                continue
            if not name.startswith(prefix + '/'):
                raise ValueError('Member lies outside sealed archive prefix: ' + name)
            relative = name[len(prefix) + 1:]
            if member.isdir():
                local_path(destination, relative)
                continue
            if relative not in expected or relative in seen:
                raise ValueError('Unexpected or duplicate archive file: ' + relative)
            row = expected[relative]
            if member.size != row['size']:
                raise RuntimeError('Archive member size differs: ' + relative)
            target = local_path(destination, relative)
            seen.add(relative)
            if target.exists():
                check_file(target, row)
                reused += 1
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            # Recheck parents after mkdir, then stage verified bytes beside the
            # target. A hard link publishes atomically without replacing a file.
            target = local_path(destination, relative)
            staged = None
            try:
                with tempfile.NamedTemporaryFile(dir=target.parent, prefix='.research-restore-', delete=False) as out:
                    staged = Path(out.name)
                    data = archive.extractfile(member)
                    if data is None:
                        raise RuntimeError('Regular archive member has no byte stream')
                    with data:
                        shutil.copyfileobj(data, out, length=2**20)
                check_file(staged, row)
                os.link(staged, target)  # Fails if target appeared; never replaces it.
                created += 1
            finally:
                if staged is not None:
                    staged.unlink(missing_ok=True)  # Only this invocation's temporary file.
    if seen != set(expected):
        raise RuntimeError('Archive omitted manifest files: ' + repr(sorted(set(expected) - seen)[:5]))
    return {'asset_name': bundle['asset_name'], 'files': len(expected),
            'bytes': sum(r['size'] for r in expected.values()), 'created': created, 'reused': reused}


def verify_bundle(bundle):
    expected = bundle_files(bundle)
    destination = output_root(bundle)
    for relative, row in expected.items():
        check_file(local_path(destination, relative), row)
    return {'asset_name': bundle['asset_name'], 'files': len(expected),
            'bytes': sum(r['size'] for r in expected.values()), 'verified_only': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify-only', action='store_true', help='Check existing restored files; no downloads or writes')
    parser.add_argument('--bundle', action='append', help='Restore/verify only this exact asset name; may be repeated')
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8-sig'))
    if manifest['schema_version'] != 1:
        raise ValueError('Unsupported research manifest schema')
    bundles = manifest['bundles']
    if len({b['asset_name'] for b in bundles}) != len(bundles):
        raise ValueError('Duplicate release asset in manifest')
    if args.bundle:
        names = set(args.bundle)
        known = {b['asset_name'] for b in bundles}
        if not names <= known:
            raise ValueError('Unknown research asset: ' + repr(sorted(names - known)))
        bundles = [b for b in bundles if b['asset_name'] in names]
    reports = []
    for bundle in bundles:
        result = verify_bundle(bundle) if args.verify_only else restore_bundle(manifest['source'], bundle)
        reports.append(result)
        print(json.dumps(result, ensure_ascii=False), flush=True)
    print(json.dumps({'research_data_complete': True, 'bundles': len(reports),
                      'files': sum(r['files'] for r in reports), 'bytes': sum(r['bytes'] for r in reports),
                      'verify_only': args.verify_only, 'experiments_executed': 0,
                      'model_training_steps': 0, 'paid_generation_calls': 0}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
