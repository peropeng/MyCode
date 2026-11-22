"""Run frozen SOURCE3 vs reverse-order public repair with durable replay.

Case JSON explicitly identifies original source, public masked view, full frozen
native assets and public G/O. The client factory must export create_client(out).
This tool never executes private acceptance or reads private selector metadata.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE / 'src'))
from thesis_recovery.rq2_control_env import ControlEnvironment, native_callback, observe_case, read, save


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['observe', 'preview', 'run'])
    parser.add_argument('--case', type=Path, required=True)
    parser.add_argument('--condition', choices=['SOURCE3', 'REVERSE'], default='SOURCE3')
    parser.add_argument('--trial', default='trial1')
    parser.add_argument('--client-factory', type=Path)
    args = parser.parse_args()
    spec = read(args.case)
    if args.command == 'observe':
        result, path = observe_case(spec)
        spec['initial_validation'] = str(path)
        save(args.case, spec)
        native = result['native_record']
        print(json.dumps({'task_id': spec['task_id'], 'known_public': native.get('completed_guarded_coverage'),
                          'public_passed': native.get('passed'), 'initial_validation': str(path), 'model_requests': 0}, ensure_ascii=False))
        return
    if not spec.get('initial_validation'):
        parser.error('A completed common C0 observation is required; run observe first')
    client = None
    if args.command == 'run':
        if not args.client_factory: parser.error('run requires --client-factory')
        module_spec = importlib.util.spec_from_file_location('_rq2_control_client_factory', args.client_factory)
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        client = module.create_client(ENGINE / '.rebuild/rq2-controls/api')
    environment = ControlEnvironment(spec, args.condition, args.trial, client=client)
    environment.native = native_callback(spec, environment.out)
    if args.command == 'preview':
        evidence, _ = environment.source_evidence()
        print(json.dumps({'task_id': spec['task_id'], 'condition': args.condition,
              'selected_edit_ids': evidence['selected_evidence_ids'], 'selected_steps': evidence['selected_evidence_steps'],
              'legal_edit_count': evidence['all_legal_successful_edit_count'], 'public_history_records': len(environment.semantic['public_history']),
              'model_requests': 0}, ensure_ascii=False))
        return
    result = environment.run()
    print(json.dumps({'task_id': spec['task_id'], 'condition': args.condition, 'status': result['status'],
           'first_public_pass_attempt': result['first_public_pass_attempt'], 'result': str(environment.out / 'RESULT.json'),
           'returned_responses_this_replay': environment.calls,
           'private_acceptance': 'NOT_RUN_BY_METHOD'}, ensure_ascii=False))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
