"""Restore one public-control case by original hashes; no model or test execution.

Frozen data and support are native-only. The new control boundary exposes public
history, current business source and G/O execution feedback; test source is denied.
"""
from __future__ import annotations
import argparse
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import tarfile
import subprocess

ENGINE = Path(__file__).resolve().parents[1]
INPUTS = ENGINE / '.rebuild/paper-inputs'
P249 = INPUTS / 'retained-experiments/rq2/experiment249/实验/实验249_固定顺序新任务共同确认'
OUT = ENGINE / '.rebuild/rq2-controls/selection'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


class OriginalStore:
    def __init__(self, wanted, inventories=()):
        self.catalog = {}
        with gzip.open(ENGINE / 'manifests/archive/objects.jsonl.gz', 'rt', encoding='utf-8') as stream:
            for line in stream:
                key, record = json.loads(line)
                self.catalog[key] = record
        spec = importlib.util.spec_from_file_location('_rq2_control_archive', ENGINE / 'tools/restore_archive.py')
        archive = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(archive)
        index = read(ENGINE / 'manifests/archive/index.json')
        index.setdefault('repository', 'peropeng/graduate-thesis')
        self.restore = archive.Restore(index, self.catalog)
        self.local = {}
        for bundle in read(ENGINE / 'manifests/research_data.json')['bundles']:
            for entry in bundle.get('files', []):
                if entry['sha256'] in wanted:
                    self.local.setdefault(entry['sha256'], []).append(ENGINE / bundle['restore_to'] / entry['path'])
        self.cache = {}
        self.kinds = {}
        self.relative_candidates = {}
        for inventory in inventories:
            for relative, digest in inventory.items():
                self.relative_candidates.setdefault(digest, set()).add(relative.replace('\\', '/'))
        self.upstream_sources = {}
        self.cached_upstreams = {}
        for item in self.catalog.values():
            source = item.get('source', {})
            if source.get('url', '').removesuffix('.git') == 'https://github.com/getmoto/moto':
                self.upstream_sources[source['revision']] = source['url'].removesuffix('.git')
        self.add_retained(wanted)

    def add_public_recorded_creations(self, task_id, wanted):
        path = INPUTS / 'rq2-experiment129/recovery/tasks' / task_id / 'replay_audit.json'
        if not path.is_file():
            return
        for row in read(path):
            params = row.get('source_parameters', {})
            text = params.get('file_text')
            if not isinstance(text, str):
                continue
            raw = text.encode('utf-8')
            lf = raw.replace(b'\r\n', b'\n')
            for candidate in (raw, lf, lf.replace(b'\n', b'\r\n')):
                key = sha(candidate)
                if key in wanted:
                    self.cache[key] = candidate
                    self.kinds['exact_original_public_recorded_creation'] = self.kinds.get('exact_original_public_recorded_creation', 0) + 1

    def add_retained(self, wanted):
        # Restore preserved identities from the retained maps without deriving
        # replacement data or inspecting the contents of frozen test files.
        for name in ('retained_feasibility_experiments.files.jsonl.gz',
                     'retained_feasibility_experiments.dependencies.jsonl.gz'):
            with gzip.open(ENGINE / 'manifests' / name, 'rt', encoding='utf-8') as stream:
                for line in stream:
                    item = json.loads(line)
                    key = item.get('sha256')
                    if key not in wanted:
                        continue
                    if item.get('destination'):
                        self.local.setdefault(key, []).append(ENGINE / item['destination'])
                    if item.get('original_object_record'):
                        self.catalog.setdefault(key, item['original_object_record'])
                        source = item['original_object_record'].get('source', {})
                        if source.get('url', '').removesuffix('.git') == 'https://github.com/getmoto/moto':
                            self.upstream_sources[source['revision']] = source['url'].removesuffix('.git')

    def cached_upstream_bytes(self, key):
        for revision, url in self.upstream_sources.items():
            cache_key = sha((url + '\n' + revision).encode())[:24]
            path = ENGINE / '.restore-cache' / ('upstream-' + cache_key + '.tar.gz')
            if not path.is_file():
                continue
            if cache_key not in self.cached_upstreams:
                archive = tarfile.open(path, 'r:gz')
                first = next(iter(archive))
                self.cached_upstreams[cache_key] = (archive, first.name.split('/')[0])
            archive, prefix = self.cached_upstreams[cache_key]
            for relative in self.relative_candidates.get(key, ()):
                try:
                    member = archive.getmember(prefix + '/' + relative)
                except KeyError:
                    continue
                if member.isfile():
                    data = archive.extractfile(member).read()
                    lf = data.replace(b'\r\n', b'\n')
                    for candidate in (data, lf, lf.replace(b'\n', b'\r\n')):
                        if sha(candidate) == key:
                            return candidate
        return None

    def get(self, key):
        if key in self.cache:
            return self.cache[key]
        options = [INPUTS / 'rq2-experiment129/recovery/blobs' / key, OUT / 'upstream' / key] + self.local.get(key, [])
        options += list((ENGINE / 'reproduction/current_inputs').glob(key + '*'))
        existing = next((p for p in options if p.is_file() and sha(p.read_bytes()) == key), None)
        if existing:
            data = existing.read_bytes()
            kind = 'retained_original_file'
        else:
            if key == sha(b''):
                return b''
            data = self.cached_upstream_bytes(key)
            if data is not None:
                self.cache[key] = data
                self.kinds['hash_verified_cached_upstream'] = self.kinds.get('hash_verified_cached_upstream', 0) + 1
                return data
            if key not in self.catalog:
                raise RuntimeError('EXACT_ORIGINAL_BYTES_UNAVAILABLE:' + key)
            data = self.restore.content(key)
            kind = self.catalog[key]['kind']
        if data is None or sha(data) != key:
            raise RuntimeError('EXACT_ORIGINAL_BYTES_UNAVAILABLE:' + key)
        self.cache[key] = data
        self.kinds[kind] = self.kinds.get(kind, 0) + 1
        return data


def copy_map(root, entries, store):
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    for relative, expected in entries.items():
        target = (root / relative).resolve()
        if not target.is_relative_to(root):
            raise RuntimeError('ORIGINAL_INVENTORY_PATH_ESCAPE')
        if target.is_file():
            if sha(target.read_bytes()) != expected:
                raise RuntimeError('PRESERVED_DIFFERENT_EXISTING_FILE')
            continue
        data = store.get(expected)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)


def recover_official_frozen(task_id, contract, store, root):
    """Apply the retained official patch mechanically; expose no test text."""
    missing = {p: h for p, h in contract['frozen_inventory'].items()
               if not (root / 'frozen' / p).is_file()}
    if not missing:
        return
    task_root = INPUTS / 'rq2-experiment129/recovery/tasks' / task_id
    patch = task_root / 'official_test_patch.diff'
    task_records = read(INPUTS / 'rq2-experiment129/recovery/extra_cohort/tasks.json')
    record = next((x for x in task_records if x.get('task_id') == task_id), None)
    if record is None:
        ledger = task_root / 'qualification_ledger.json'
        if ledger.is_file():
            record = read(ledger).get('checkpoint')
    if record is None or not patch.is_file():
        return
    revision = record['base_commit']
    url = 'https://github.com/getmoto/moto'
    key = sha((url + '\n' + revision).encode())[:24]
    archive_path = ENGINE / '.restore-cache' / ('upstream-' + key + '.tar.gz')
    if not archive_path.is_file():
        return
    patched = root / 'official_patch_reconstruction'
    patched.mkdir(parents=True, exist_ok=True)
    # Isolate from the enclosing thesis worktree. Otherwise git apply can
    # silently skip paths when cwd lies below that worktree's root.
    subprocess.run(['git', 'init', '--quiet', str(patched)], check=True, capture_output=True)
    listing = subprocess.run(['git', 'apply', '--numstat', str(patch)], capture_output=True, check=True)
    paths = [line.decode('utf-8').split('\t', 2)[2] for line in listing.stdout.splitlines() if line]
    with tarfile.open(archive_path, 'r:gz') as archive:
        prefix = next(iter(archive)).name.split('/')[0]
        for relative in paths:
            target = (patched / relative).resolve()
            if not target.is_relative_to(patched.resolve()):
                raise RuntimeError('OFFICIAL_PATCH_PATH_ESCAPE')
            try:
                member = archive.getmember(prefix + '/' + relative)
            except KeyError:
                continue
            if member.isfile():
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.extractfile(member).read())
    result = subprocess.run(['git', 'apply', '--whitespace=nowarn', str(patch)], cwd=patched, capture_output=True)
    if result.returncode:
        raise RuntimeError('RETAINED_OFFICIAL_TEST_PATCH_APPLICATION_FAILED')
    matched, unmatched = [], []
    for relative, expected in missing.items():
        path = patched / relative
        if path.is_file():
            data = path.read_bytes()
            lf = data.replace(b'\r\n', b'\n')
            verified = next((b for b in (data, lf, lf.replace(b'\n', b'\r\n')) if sha(b) == expected), None)
            if verified is None:
                unmatched.append({'expected': expected, 'reconstructed': sha(data)})
                continue
            path.write_bytes(verified)
            store.local.setdefault(expected, []).append(path)
            matched.append(expected)
    save(root / 'official_frozen_recovery_receipt.json', {
        'task_id': task_id, 'base_commit': revision,
        'retained_official_patch_sha256': sha(patch.read_bytes()),
        'verified_frozen_file_hashes': matched, 'unmatched_expected_hashes': unmatched, 'new_tests_generated': False,
        'test_text_or_names_exposed': False, 'task_tests_run': 0})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('task_id')
    parser.add_argument('--stage-native-only', action='store_true',
                        help='Restore original C0 and opaque frozen bytes; do not create a ready case or model public view')
    args = parser.parse_args()
    selected = read(ENGINE / 'verification/rq2_control_candidates.json')['tasks'][args.task_id]
    contract = read(selected['contract'])
    qualification = read(INPUTS / 'experiment257/PROTOCOL257.json')['qualification'][args.task_id]['qualification_record']
    scope_binding = qualification.get('public_test_scope_contract') or qualification.get('masked_scope')
    wanted = set(contract['c0_business_paths_sha256'].values()) | set(contract['template_inventory'].values()) | set(contract['frozen_inventory'].values())
    store = OriginalStore(wanted, (contract['template_inventory'], contract['frozen_inventory'], contract['c0_business_paths_sha256']))
    store.add_public_recorded_creations(args.task_id, wanted)
    root = OUT / args.task_id / 'runtime_assets'
    business = contract['c0_business_paths_sha256']
    support_all = {p: h for p, h in contract['template_inventory'].items() if p not in business}
    # This standalone old reproduction script is not part of either new arm's
    # native dependency boundary. Preserve its gap without generating a copy.
    support = {p: h for p, h in support_all.items() if p != 'reproduce.py'}
    # Native-only support is separate from all model-readable business files.
    copy_map(root / 'current_business/repo', business, store)
    copy_map(root / 'support/repo', support, store)
    recover_official_frozen(args.task_id, contract, store, root)
    copy_map(root / 'frozen', contract['frozen_inventory'], store)
    public_view = root / 'public_empty'
    public_view.mkdir(parents=True, exist_ok=True)
    if any(public_view.iterdir()):
        raise RuntimeError('NEW_PUBLIC_EMPTY_VIEW_CONTAINS_FILES')
    policy = {'schema': 'rq2.common_information_boundary.v1',
              'policy': 'PUBLIC_HISTORY_CURRENT_BUSINESS_AND_GOAL_ORDINARY_FEEDBACK_NO_TEST_SOURCE',
              'origin': 'New development control boundary authorized by current parent task; not historical masked scope',
              'model_may_read': ['complete public history', 'current business source', 'public issue', 'public goal/ordinary execution feedback'],
              'model_test_source_access': False, 'public_view_hashes': {},
              'support_and_frozen_native_only': True,
              'historical_baseline_information_permission_differs': True,
              'historical_scope_recovered': False,
              'historical_scope_reference_only': scope_binding,
              'native_support_omissions': {p: h for p, h in support_all.items() if p not in support},
              'new_model_requests': 0, 'task_tests_run': 0}
    save(root / 'new_information_policy.json', policy)
    if args.stage_native_only:
        receipt = {'task_id': args.task_id, 'ready': False, 'stage': 'original_native_assets_only',
                   'business_files': len(business), 'support_files': len(support),
                   'frozen_files': len(contract['frozen_inventory']), 'source_kinds': store.kinds,
                   'new_information_policy': str(root / 'new_information_policy.json'),
                   'model_requests': 0, 'task_tests_run': 0}
        save(root / 'native_assets_receipt.json', receipt)
        print(json.dumps(receipt, ensure_ascii=False))
        return
    python = INPUTS.parent / 'current-method/recovery' / read(ENGINE / 'manifests/native_environment.json')['relative'] / 'Scripts/python.exe'
    if not python.is_file():
        raise RuntimeError('RECOVERED_MOTO_RUNTIME_NOT_FOUND')
    spec = {'task_id': args.task_id, 'package': 'moto', 'business_root': str(root / 'current_business/repo'), 'support_root': str(root / 'support/repo'),
            'business_hashes': business, 'support_hashes': support,
            'public_view': str(public_view), 'public_view_hashes': {}, 'public_test_py_files_SHA256': {},
            'mask_scope': None, 'information_policy': 'TEST_SOURCE_NOT_SHARED', 'information_policy_details': policy,
            'frozen_root': str(root / 'frozen'), 'frozen_inventory': contract['frozen_inventory'],
            'pack': selected['pack'], 'ref': read(selected['public_ref']), 'ranking_plan': selected['ranking_plan'],
            'goal_nodes': contract['public_target_nodes'], 'ordinary_nodes': contract['ordinary_nodes'],
            'python': str(python), 'native_harness': str(INPUTS / 'rq2-experiment129/executor/rounds/05/harness/getmoto__moto-5134'),
            'wall_budget_seconds': 1800, 'state_admission_mode': 'PROGRESS_SET',
            'original_contract': selected['contract'], 'original_public_scope_SHA256': None,
            'new_information_policy': str(root / 'new_information_policy.json'),
            'new_model_requests': 0, 'task_tests_run': 0}
    save(OUT / args.task_id / 'case.json', spec)
    receipt = {'task_id': args.task_id, 'ready': True, 'business_files': len(business), 'support_files': len(support),
               'frozen_files': len(contract['frozen_inventory']), 'public_test_files': 0,
               'new_information_policy': str(root / 'new_information_policy.json'),
               'historical_mask_scope_not_recreated': True, 'full_frozen_never_used_as_model_public_view': True,
               'source_kinds': store.kinds, 'case': str(OUT / args.task_id / 'case.json'),
               'model_requests': 0, 'model_tokens': 0, 'model_cost_CNY': 0, 'task_tests_run': 0}
    save(root / 'native_asset_gap_resolution.json', {
        'task_id': args.task_id, 'required_native_assets_complete': True,
        'original_business_and_frozen_complete': True,
        'native_support_omissions': policy['native_support_omissions'],
        'initial_gap_history_retained': (root / 'native_asset_gaps.json').is_file(),
        'ready_under_new_information_boundary': True})
    save(OUT / args.task_id / 'runtime_assets_receipt.json', receipt)
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    main()
