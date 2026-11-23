"""Public-result-triggered ablation of the additional current-source package.

Keep SOURCE3 history edits, full history, raw public feedback, source tools and
goal protection. Only the extra relation-derived current source/context block
is absent. This is a distinct development condition, never an old-run restart.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE / 'src'))
from thesis_recovery.rq2_control_env import ControlEnvironment, native_callback, read, save, sha

CONDITION = 'SOURCE3_NO_ADDITIONAL_CONTEXT_V2'


def remove_extra_context(body):
    """Remove only the derived package after the original feedback binding."""
    removed = 0
    for message in body['messages']:
        try:
            value = json.loads(message.get('content', ''))
        except (ValueError, TypeError):
            continue
        if not isinstance(value, dict):
            continue
        if 'additional_business_context' in value:
            value.pop('additional_business_context')
            removed += 1
        if value.get('schema') == 'current-public-feedback-source-binding/1':
            value['current_business_functions'] = []
        message['content'] = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    if removed != 1:
        raise RuntimeError('Expected exactly one derived context package')
    return body


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', type=Path, required=True)
    parser.add_argument('--client-factory', type=Path, required=True)
    parser.add_argument('--trial', default='trial1')
    args = parser.parse_args()
    spec = read(args.case)
    module_spec = importlib.util.spec_from_file_location('_rq2_context_client', args.client_factory)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    output = ENGINE / '.rebuild/rq2-controls/runs' / spec['task_id'] / args.trial / CONDITION
    env = ControlEnvironment(spec, 'SOURCE3', args.trial, client=module.create_client(output), output=output)
    variant = {'condition': CONDITION, 'same_base_condition': env.binding, 'launcher_sha256': sha(Path(__file__)),
               'removed': 'additional_business_context relation-derived current code/context only',
               'retained': ['SOURCE3 historical edits', 'full public history', 'current-code read tools',
                            'raw initial/latest public feedback', 'goal identity admission', 'same API/native budgets'],
               'selection_basis': 'Both complete-context orders public-PASS only at attempt3 on the pressure problem; no private results used'}
    marker = output / 'INTERVENTION_BINDING.json'
    if marker.exists() and read(marker) != variant:
        raise RuntimeError('Separate ablation code/input changed')
    save(marker, variant)
    env.condition, env.arm = CONDITION, CONDITION
    original_body = env.body
    env.body = lambda *a, **kw: remove_extra_context(original_body(*a, **kw))
    env.native = native_callback(spec, env.out)
    result = env.run()
    print(json.dumps({'task_id': spec['task_id'], 'condition': CONDITION, 'status': result['status'],
                      'first_public_pass_attempt': result['first_public_pass_attempt'],
                      'result': str(output / 'RESULT.json'), 'private_acceptance': 'NOT_RUN_BY_METHOD'}, ensure_ascii=False))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
