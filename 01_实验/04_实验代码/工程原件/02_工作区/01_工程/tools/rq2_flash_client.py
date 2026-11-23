"""Shared paid-call ledger factory for the explicitly authorized RQ2 controls."""
import json
from pathlib import Path
import sys

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE / 'src'))
from thesis_recovery.flash_accounting import FlashClient


def create_client(output):
    # Run output does not own or reset the shared balance ledger.
    config = json.loads((ENGINE / 'manifests/rq2_control_execution.json').read_text(encoding='utf-8'))
    return FlashClient(ENGINE / '.rebuild/rq2-controls/api', config['api'])


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    print(json.dumps(create_client(None).summary(), ensure_ascii=False, indent=2))
