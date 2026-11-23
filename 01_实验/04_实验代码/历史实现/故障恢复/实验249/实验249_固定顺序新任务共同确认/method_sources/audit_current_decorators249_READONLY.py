"""Audit own observed public artifacts; never change the active method inputs."""
import ast
from trial_runtime249 import *

trial = HERE / 'runs/OURS248_FULL/getmoto__moto-5072/trial1'
rows = []
for ordinal, snapshot in ((2, 'attempt1'), (3, 'attempt2')):
    body_path = trial / 'calls' / ('call' + str(ordinal).zfill(3)) / 'FIRST_UNPOST_BODY.json'
    source_path = trial / 'snapshots' / snapshot / 'business_source.json'
    if not body_path.exists() or not source_path.exists(): continue
    body = read(body_path); files = read(source_path)
    tails = []
    for message in body['messages']:
        try: item = json.loads(message.get('content', ''))
        except (ValueError, TypeError): continue
        if isinstance(item, dict) and item.get('schema') == 'current-public-feedback-source-binding/1': tails.append(item)
    if len(tails) != 1: raise RuntimeError('EXP249_AUDIT_CURRENT_TAIL_NOT_UNIQUE')
    tail = tails[0]; inventory = {p: hashlib.sha256(t.encode()).hexdigest() for p, t in files.items()}
    if digest(inventory) != tail['binding']['source_inventory_SHA256']: raise RuntimeError('EXP249_AUDIT_SOURCE_NOT_CURRENT_REQUEST_BINDING')
    gaps = []
    for span in tail['current_business_functions']:
        rel = span['path']; text = files[rel]; lines = text.splitlines(True)
        if hashlib.sha256(text.encode()).hexdigest() != span['source_sha256']: raise RuntimeError('EXP249_AUDIT_CONTEXT_SOURCE_SHA_DRIFT')
        if ''.join(lines[span['start_line'] - 1:span['end_line']]) != span['text']: raise RuntimeError('EXP249_AUDIT_CONTEXT_SPAN_BYTES_DRIFT')
        tree = ast.parse(text)
        matches = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
            and n.lineno == span['start_line'] and n.end_lineno == span['end_line'] and n.decorator_list]
        for node in matches:
            first = min(d.lineno for d in node.decorator_list)
            gaps.append({'path': rel, 'symbol_name': node.name, 'definition_line': node.lineno,
                'actual_semantic_start_line': first, 'omitted_current_decorators': ''.join(lines[first - 1:node.lineno - 1]),
                'prompt_complete_source_span_claim': span.get('complete_source_span'), 'source_SHA256': inventory[rel],
                'specific_request_source_text_lacks_decorators': True})
    rows.append({'request_ordinal': ordinal, 'body_path': str(body_path), 'body_artifact_SHA256': sha(body_path),
        'body_semantic_SHA256': digest(body), 'current_source_path': str(source_path), 'current_source_SHA256': sha(source_path),
        'source_inventory_SHA256': digest(inventory), 'bound_current_native_witness_SHA256': tail['binding']['source_native_witness_SHA256'],
        'decorated_spans_omitted_decorators': gaps})
native = []
for attempt in (1, 2):
    path = trial / 'native_requests' / ('attempt' + str(attempt)) / 'COMPLETED_PUBLIC.json'
    if not path.exists(): continue
    value = read(path); raw = read(value['public_native_path'])
    native.append({'attempt': attempt, 'completed_path': str(path), 'completed_SHA256': sha(path),
        'original_public_native_path': value['public_native_path'], 'original_public_native_SHA256': value['public_native_SHA256'],
        'failed_goals': value['failed_goals'], 'ordinary_all_pass': value['ordinary_all_pass'],
        'Goal_error': [line for node in read(trial / 'native_requests' / ('attempt' + str(attempt)) / 'NATIVE_READY.json')['goal_nodes']
            for line in raw['pytest']['outcomes'][node].get('detail', '').splitlines() if line.startswith('E ')]})
value = {'schema': 'EXP249-own-current-decorator-span-diagnostic/1', 'task_id': 'getmoto__moto-5072', 'trial_id': 'trial1',
    'evidence_kind': 'Observed current public development evidence; not an intervention or causal ablation',
    'requests': rows, 'actual_public_native': native,
    'finding': 'AST definition lineno omits decorator_list lines from current authoritative complete function spans. @property changes call semantics.',
    'limitation': 'The first model rationale already mentioned a property, so this does not establish that decorators were absent from every shared historical input or independently caused failure.',
    'prospective_general_change_candidate': 'For future uniformly frozen versions, start function/class spans at min(definition lineno, all decorator linenos). Do not alter the currently running frozen method or add task-specific instructions.',
    'active_source_or_request_changes': 0, 'private_Gold_or_other_methods_read': 0, 'model_native_finance': 0}
path = HERE / 'OWN_PUBLIC_DECORATOR_DIAGNOSTIC249.json'; save(path, value)
print(canonical({'path': str(path), 'sha256': sha(path), 'requests': len(rows), 'omitted_decorator_spans': [len(row['decorated_spans_omitted_decorators']) for row in rows], 'active_method_changed': False}), flush=True)
