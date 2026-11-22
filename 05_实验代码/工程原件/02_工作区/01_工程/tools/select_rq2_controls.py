"""Select RQ2 controls from public edit geometry, never method outcomes or Gold.

Only public histories, SOURCE3 orders, public issue text and current-source hashes
are inspected. Original evidence bytes are restored by the archive catalog.
This command performs no model request and no task test.
"""
from __future__ import annotations
import difflib
import gzip
import hashlib
import json
from pathlib import Path
import tarfile
import urllib.request
import zlib

ENGINE = Path(__file__).resolve().parents[1]
INPUTS = ENGINE / '.rebuild/paper-inputs'
P224 = INPUTS / 'retained-experiments/rq2/experiment224/实验/实验224_二十三题Flash完整共同恢复比较'
P249 = INPUTS / 'retained-experiments/rq2/experiment249/实验/实验249_固定顺序新任务共同确认'
P257 = INPUTS / 'experiment257'
OUT = ENGINE / '.rebuild/rq2-controls/selection'
SELECTED = ('getmoto__moto-5516', 'getmoto__moto-7081', 'getmoto__moto-6212')
BACKUP = 'getmoto__moto-6387'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def digest(value):
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode())


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8', newline='\n')


def main():
    protocol, opportunities = read(P257 / 'PROTOCOL257.json'), read(P257 / 'RANKING_INTERVENTION_OPPORTUNITIES.json')
    refs = {r['task_id']: r for r in read(P224 / 'data/selected_task_bindings.json')['tasks']}
    catalog = {}
    with gzip.open(ENGINE / 'manifests/archive/objects.jsonl.gz', 'rt', encoding='utf-8') as stream:
        for line in stream:
            key, record = json.loads(line)
            catalog[key] = record
    archive_record = read(ENGINE / 'manifests/archive/index.json')['assets']['current-inputs-full.tar']
    archive_path = ENGINE / '.restore-cache/current-inputs-full.tar'
    if sha(archive_path.read_bytes()) != archive_record['sha256']:
        raise RuntimeError('ORIGINAL_ARCHIVE_CHANGED')
    archives = {archive_path.name: tarfile.open(archive_path, 'r:')}
    cache = {}
    local_files = {}
    for bundle in read(ENGINE / 'manifests/research_data.json')['bundles']:
        for entry in bundle.get('files', []):
            local_files.setdefault(entry['sha256'], []).append(ENGINE / bundle['restore_to'] / entry['path'])

    def content(key):
        if key in cache:
            return cache[key]
        candidates = [INPUTS / 'rq2-experiment129/recovery/blobs' / key, OUT / 'upstream' / key] + local_files.get(key, [])
        local = next((p for p in candidates if p.is_file()), None)
        if local is not None:
            data = local.read_bytes()
        else:
            record = catalog[key]
            if record['kind'] == 'upstream':
                source = record['source']
                repository = source['url'].removesuffix('.git').split('github.com/', 1)[1]
                url = f"https://raw.githubusercontent.com/{repository}/{source['revision']}/{source['path']}"
                with urllib.request.urlopen(url, timeout=60) as response:
                    data = response.read()
                if sha(data) != key:
                    raise RuntimeError('PINNED_UPSTREAM_BYTES_CHANGED')
                target = OUT / 'upstream' / key
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            elif record['kind'] != 'asset':
                raise RuntimeError('PUBLIC_ORIGINAL_NOT_LOCALLY_AVAILABLE:' + key)
            else:
                compressed = b''.join(archives[c['asset']].extractfile(c['member']).read() for c in record['chunks'])
                data = zlib.decompress(compressed) if record.get('encoding') == 'zlib' else compressed
        if sha(data) != key:
            raise RuntimeError('ORIGINAL_EVIDENCE_BYTES_CHANGED')
        cache[key] = data
        return data

    screening = []
    rows = {}
    for tid in opportunities['task_order']:
        row = opportunities['rows'][tid]
        source, reverse = row['all_legal_edit_orders']['SOURCE3'], row['all_legal_edit_orders']['REVERSE']
        prefix_differences = {str(k): {
            'ordered_ids_differ': [r['call_id'] for r in source[:k]] != [r['call_id'] for r in reverse[:k]],
            'evidence_sets_differ': {r['call_id'] for r in source[:k]} != {r['call_id'] for r in reverse[:k]}}
            for k in (1, 2, 3)}
        reason = ('excluded_previous_all_methods_solved_case' if tid == 'dask__dask-9378'
                  else 'excluded_single_legal_edit' if len(source) < 2
                  else 'excluded_no_prefix_set_difference' if not any(v['evidence_sets_differ'] for v in prefix_differences.values())
                  else 'eligible_public_geometry')
        screening.append({'task_id': tid, 'legal_edit_count': len(source), 'paths': sorted({r['path'] for r in source}),
                          'prefix_comparison': prefix_differences, 'decision': reason,
                          'selected': tid in SELECTED, 'backup': tid == BACKUP})
        if tid not in SELECTED:
            continue
        original_contract = protocol['qualification'][tid]['contract_path'].replace('\\', '/')
        contract_path = P249 / original_contract.split('实验249_固定顺序新任务共同确认/', 1)[1]
        contract = read(contract_path)
        plan_path = P257 / 'ranking/plans' / tid / 'SOURCE3.json'
        plan = read(plan_path)
        ref = refs[tid]
        if digest(ref['mapping']) != plan['mapping_digest'] or ref['input_turns_sha256'] != plan['input_turns_sha256']:
            raise RuntimeError('STEP_MAPPING_OR_PUBLIC_HISTORY_DRIFT')
        pack_path = P224 / 'v2_auth_direct_publicpack/packs' / (tid + '.json')
        pack = read(pack_path)
        if sha(pack_path.read_bytes()) != contract['pack_sha256'] or pack['input_digest'] != contract['input_digest']:
            raise RuntimeError('COMMON_PUBLIC_PACK_DRIFT')
        root = OUT / tid
        edits_data = content(row['visible_edits']['sha256'])
        edits_path = root / 'task/visible/edits.json'
        edits_path.parent.mkdir(parents=True, exist_ok=True)
        edits_path.write_bytes(edits_data)
        edits = json.loads(edits_data.decode('utf-8-sig'))
        by_id = {e['call_id']: e for e in edits}
        evidence = []
        for binding in row['legal_changed_edit_bindings']:
            edit = by_id[binding['call_id']]
            before, after = b'', b''
            for name in ('before', 'after'):
                item = edit.get(name)
                raw = b'' if item is None else content(item['sha256'])
                if item:
                    target = (root / 'asset' / item['blob']).resolve()
                    if not target.is_relative_to(root.resolve()):
                        raise RuntimeError('UNSAFE_PUBLIC_BLOB_PATH')
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(raw)
                if name == 'before': before = raw
                else: after = raw
            if sha(before) != binding['before_sha256'] or sha(after) != binding['after_sha256']:
                raise RuntimeError('PUBLIC_EDIT_BINDING_DRIFT')
            path = binding['path']
            current_sha = contract['c0_business_paths_sha256'][path]
            current = content(current_sha)
            current_path = root / 'current_source' / path
            current_path.parent.mkdir(parents=True, exist_ok=True)
            current_path.write_bytes(current)
            a, b, c = before.decode('utf-8'), after.decode('utf-8'), current.decode('utf-8')
            changed_new_chunks = ['\n'.join(b.splitlines()[j1:j2]) for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a.splitlines(), b.splitlines()).get_opcodes() if tag != 'equal' and j2 > j1]
            evidence.append({**binding, 'current_sha256': current_sha, 'after_equals_current': sha(after) == current_sha,
                             'changed_after_chunks_count': len(changed_new_chunks),
                             'changed_after_chunks_still_present': sum(chunk in c for chunk in changed_new_chunks),
                             'before_after_diff': ''.join(difflib.unified_diff(a.splitlines(True), b.splitlines(True), fromfile=path + ':before', tofile=path + ':after'))})
        portable = {k: ref[k] for k in ('task_id', 'mapping', 'package', 'input_digest', 'input_turns_sha256')}
        portable.update(task_path=str(root / 'task'), asset_root=str(root / 'asset'), G_frozen_plan=str(plan_path))
        save(root / 'public_ref.json', portable)
        save(root / 'historical_public_edit_review.json', evidence)
        rows[tid] = {'contract': str(contract_path), 'pack': str(pack_path), 'ranking_plan': str(plan_path),
                     'public_ref': str(root / 'public_ref.json'), 'public_edit_review': str(root / 'historical_public_edit_review.json'),
                     'public_issue': contract['issue'], 'package': contract['package'],
                     'public_target_nodes': contract['public_target_nodes'], 'ordinary_nodes': contract['ordinary_nodes'],
                     'legal_edits': len(source), 'source3_first_three': source[:3], 'reverse_first_three': reverse[:3],
                     'prefix_comparison': prefix_differences,
                     'current_C0_matches_pack_business_inventory': pack['c0_business_paths_sha256'] == contract['c0_business_paths_sha256'],
                     'restored_original_history_bytes': True, 'public_edit_count': len(edits),
                     'current_source_paths': {p: str(root / 'current_source' / p) for p in {e['path'] for e in evidence}}}
    result = {'schema': 'rq2.public_control_selection.v1',
              'selection_basis': 'Public information difference before any new outcomes; choose multi-file provider/response boundaries first, then distinct prefix sets and existing Moto environment.',
              'not_used': ['Gold', 'private tests', 'prior method wins/losses'],
              'rules': ['exclude Dask9378 completed easy case', 'at least two distinct legal changed edits',
                        'SOURCE3 and reverse must expose different evidence sets at some fixed budget1/2/3',
                        'prefer multiple business files with producer/consumer or normalization boundary',
                        'restore original public bytes and keep same common C0/targets'],
              'selected_tasks': list(SELECTED), 'backup_task': BACKUP,
              'development_steering_disclosure': 'Initial public-geometry shortlist included IoT/Athena/CloudFront, with EC2 fleet as blind structural backup. Parent subsequently found all original methods already solve those first three naturally, while EC2 fleet is an exposed all-method negative case. User explicitly prioritizes mechanisms with improvement opportunity. The active pressure group uses fleet/IoT/Athena; CloudFront remains calibration backup. This is exposed development selection, not independent evaluation and not selection for an existing ours win.',
              'screening': screening, 'tasks': rows,
              'new_model_requests': 0, 'new_model_tokens': 0, 'model_cost_CNY': 0, 'task_tests_run': 0}
    save(ENGINE / 'verification/rq2_control_candidates.json', result)
    print(json.dumps({'selected': list(rows), 'screened': len(screening), 'original_public_evidence_verified': True,
                      'new_model_requests': 0, 'model_cost_CNY': 0}, ensure_ascii=False))


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    main()
