"""Record first real trial preparation before importing the full method source."""
import argparse
import datetime
import hashlib
import json
import os
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--contract', required=True); args = parser.parse_args()
    path = Path(args.contract).resolve(); raw = path.read_bytes(); contract = json.loads(raw.decode('utf-8-sig'))
    if contract.get('method') != 'OURS248_FULL' or contract.get('clock_policy') != 'START_AT_FIRST_REAL_TRIAL_PREPARATION':
        raise RuntimeError('EXP249_REAL_PREPARATION_CLOCK_CONTRACT_REQUIRED')
    out = Path(contract['output_root']).resolve()
    if out != (HERE / 'runs/OURS248_FULL' / contract['task_id'] / contract['trial_id']).resolve():
        raise RuntimeError('EXP249_TRIAL_OUTPUT_SCOPE')
    t0 = out / 'SCIENCE_T0_TRIAL_PREPARATION_STARTED.json'
    if not t0.exists():
        t0.parent.mkdir(parents=True, exist_ok=True)
        with t0.open('x', encoding='utf-8') as stream:
            json.dump({'schema': 'EXP249-real-trial-preparation-T0/1',
                'at_UTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'method': 'OURS248_FULL',
                'task_id': contract['task_id'], 'trial_id': contract['trial_id'],
                'contract_SHA256': hashlib.sha256(raw).hexdigest(), 'real_preparation_time_included': True,
                'method_module_import_and_all_initial_preparation_included': True,
                'first_POST_time_recorded_separately': True, 'existing_RQ1_reuse_cost_disclosed_separately': True,
                'old_protocol_POST_only_rule_superseded_by_later_explicit_Root_clock_instruction': True}, stream, ensure_ascii=False, indent=2)
            stream.flush(); os.fsync(stream.fileno())
    sys.argv = [str(HERE / 'ours_entry249.py'), '--contract', str(path)]
    runpy.run_path(str(HERE / 'ours_entry249.py'), run_name='__main__')


if __name__ == '__main__': main()
