"""Copy exact full 4L40P40T sources and locate public-only exact dense caches."""
import ast
import re
from trial_runtime249 import *
from shared_public249 import load_public_task

AL246 = ROOT / '工作区/1011-exp246-agentless-unbudgeted/实验/实验246_Agentless论文完整配置无外部预算'
AL183 = ROOT / '工作区/1008-exp183-fixed12-complete-main/实验/实验183_固定十二题完整恢复与排序对照'
PUBLIC224 = ROOT / '工作区/1008-2320-exp224-flash-common/实验/实验224_二十三题Flash完整共同恢复比较'
target = HERE / 'agentless_core'; target.mkdir(parents=True, exist_ok=True)
mapping = {}
def copy_exact(source, relative):
    dest = target / relative; dest.parent.mkdir(parents=True, exist_ok=True)
    data = source.read_bytes()
    if dest.exists() and dest.read_bytes() != data: raise RuntimeError('EXP249_AGENTLESS_COPY_ALREADY_DIFFERS')
    if not dest.exists(): dest.write_bytes(data)
    mapping[str(dest)] = {'original': str(source), 'original_SHA256': sha(source), 'copy_SHA256': sha(dest), 'byte_exact': True}
for name in ('agentless178.py', 'agentless_source_derivative178.json', 'normalization_adapter_v3_241.py', 'FORMAL_PARAMETERS_EVIDENCE.json'):
    copy_exact(AL246 / name, name)
for name in ('__init__.py', 'official_core166.py', 'local_core166.py', 'dense166.py', 'source_symbol_map166.json', 'LICENSE'):
    copy_exact(AL183 / 'agentless_bridge' / name, 'agentless_bridge/' + name)
copy_exact(AL246 / 'agentless_bridge/official_prompts166.json', 'agentless_bridge/official_prompts166.json')
namespace = {'json': json, 'canonical': canonical, 'digest': digest, 'collections': __import__('collections'), 're': re}
source = AL183 / 'audit183/new_public_contract_preflight.py'
node = next(n for n in ast.parse(source.read_text('utf-8-sig')).body if isinstance(n, ast.FunctionDef) and n.name == 'semantic_index')
exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), 'exec'), namespace)
cache_paths = sorted((PUBLIC224 / 'retrieval/cases_v2').glob('*.json'))
caches = [(p, read(p)) for p in cache_paths]
binding = {'schema': 'EXP249-Agentless-public-exact-cache-bindings/1', 'tasks': {}, 'new_encoding': 0,
    'old_responses_candidates_private_results_not_read': True, 'preprocessing_reuse_cost_separate': True}
for task in read(E249 / 'protocol249_SOURCE.json')['task_order']:
    data = load_public_task(task); semantic = data['semantic']; contract = data['contract']
    indexed = namespace['semantic_index'](semantic['failure_feedback'])
    query = 'Restore the observed failure while preserving passing behavior. Original issue background: ' + str(semantic['original_issue']) + '\nAll distinct observed public errors:\n' + canonical(indexed['errors'])
    query_sha = hashlib.sha256(query.encode()).hexdigest()
    matching = [(p, c) for p, c in caches if c.get('source_files_sha256') == contract['c0_business_paths_sha256'] and c.get('query_sha256') == query_sha and c.get('query_complete') is True and c.get('query_truncated') is False]
    row = {'task_id': task, 'source_inventory_SHA256': digest(contract['c0_business_paths_sha256']), 'query': query,
        'query_SHA256': query_sha, 'exact_cache_found': bool(matching), 'current_C0_same_for_all_methods': True}
    if matching:
        p, c = matching[0]
        for key, expected in c['vector_sha256'].items():
            if sha(Path(c['vectors_dir']) / (key + '.npy')) != expected: raise RuntimeError('EXP249_AGENTLESS_PREVIOUS_PUBLIC_VECTOR_DRIFT')
        row.update(cache_path=str(p), cache_SHA256=sha(p), historical_preparation_seconds=c['elapsed_seconds'],
            historical_preparation_device=c.get('device'), vector_count=len(c['vector_sha256']),
            original_model_identity=c['model_identity'], dense_core_unchanged=True, new_encoder_forward=0)
    binding['tasks'][task] = row
save(HERE / 'AGENTLESS_ORIGINAL_SOURCE_MAP249.json', {'files': mapping, 'method_parameters': '4 locations x 10 patches; 40 reproduction tests', 'source_only': True})
save(HERE / 'AGENTLESS_PUBLIC_DENSE_BINDINGS249_SOURCE.json', binding)
print(canonical({'source_files': len(mapping), 'dense_exact_matches': {task: row['exact_cache_found'] for task, row in binding['tasks'].items()}, 'actual_generation_native_private_finance': 0}), flush=True)
