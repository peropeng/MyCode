"""Compare current relation retrieval to bounded ordinary whole-source spans.

Keep SOURCE3 edits, full public history, current-source tools, feedback and
Goal protection. Select whole functions outside relation endpoints in lexical
order, up to the original relation source byte budget without padding/clipping.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE / 'src'))
from thesis_recovery.rq2_control_env import ControlEnvironment, native_callback, read, save, sha

CONDITION = 'SOURCE3_MATCHED_NONEDGE_CONTEXT'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', type=Path, required=True)
    parser.add_argument('--client-factory', type=Path, required=True)
    parser.add_argument('--trial', default='trial1')
    args = parser.parse_args()
    spec = read(args.case)
    module_spec = importlib.util.spec_from_file_location('_rq2_nonedge_client', args.client_factory)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    output = ENGINE / '.rebuild/rq2-controls/runs' / spec['task_id'] / args.trial / CONDITION
    env = ControlEnvironment(spec, 'SOURCE3', args.trial, client=module.create_client(output), output=output)
    variant = {'condition': CONDITION, 'same_base_condition': env.binding,
               'launcher_sha256': sha(Path(__file__)),
               'intervention': 'Original relations248.nonedge_context whole-source byte-budget control',
               'retained': ['SOURCE3 edits', 'full public history', 'current-source tools',
                            'raw public feedback', 'Goal identity protection', 'same API/native budgets'],
               'selection_basis': 'Public outcome only: relation package repaired the pressure task; no-extra package did not',
               'padding_or_clipping': False, 'metadata_byte_identity_claimed': False}
    marker = output / 'INTERVENTION_BINDING.json'
    if marker.exists() and read(marker) != variant:
        raise RuntimeError('Separate nonedge code/input changed')
    save(marker, variant)
    env.condition, env.arm = CONDITION, CONDITION
    env.closure_enabled, env.context_mode = False, 'NONEDGE'
    env.native = native_callback(spec, env.out)
    result = env.run()
    print(json.dumps({'task_id': spec['task_id'], 'condition': CONDITION,
                      'status': result['status'], 'first_public_pass_attempt': result['first_public_pass_attempt'],
                      'result': str(output / 'RESULT.json'), 'private_acceptance': 'NOT_RUN_BY_METHOD'}, ensure_ascii=False))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
