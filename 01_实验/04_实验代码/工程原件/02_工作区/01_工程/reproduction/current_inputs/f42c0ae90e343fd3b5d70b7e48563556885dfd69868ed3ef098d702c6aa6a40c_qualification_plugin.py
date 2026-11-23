"""Record native pytest nodes/errors without modifying their assertions."""
import importlib
import json
import os
from pathlib import Path
import sys
import pytest

OUT = Path(os.environ['EXP129_OUTCOMES'])
RECORD = {'collected': [], 'collected_parameter_indices': {}, 'outcomes': {}, 'collection_errors': []}

# mypy's root conftest imports its package-backed test plugin before the
# sessionstart hook. Bind its product package to candidate code at plugin load.
if os.environ.get('EXP129_PACKAGE') in ('mypy', 'dask', 'conans', 'dvc', 'pandas', 'moto'):
    sys.path.insert(0, os.environ['EXP129_SOURCE_ROOT'])
    importlib.import_module(os.environ['EXP129_PACKAGE'])


def pytest_sessionstart(session):
    root = Path(os.environ['EXP129_SOURCE_ROOT']).resolve()
    sys.path.insert(0, str(root))
    name = os.environ['EXP129_PACKAGE']
    try:
        module = importlib.import_module(name)
        path = Path(module.__file__).resolve()
        RECORD['product_import'] = str(path)
        try:
            path.relative_to(root)
            correct_source = True
        except ValueError:
            correct_source = False
        if not correct_source:
            raise RuntimeError(f'Wrong product imported: {path}')
    except Exception as error:
        RECORD['product_import_error'] = repr(error)
        raise
    ready = Path(os.environ['EXP129_GUARD_READY'])
    if not ready.is_file():
        raise RuntimeError('Required Exp129 guard was not loaded')
    RECORD['guard'] = json.loads(ready.read_text('utf-8'))


@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(session, config, items):
    selector = os.environ.get('EXP129_SELECTED_NODES')
    if selector:
        wanted = json.loads(Path(selector).read_text('utf-8'))
        by_id = {item.nodeid: item for item in items}
        wanted_set = set(wanted)
        deselected = [item for item in items if item.nodeid not in wanted_set]
        config.hook.pytest_deselected(items=deselected)
        items[:] = [by_id[node] for node in wanted if node in by_id]
        RECORD['requested_but_uncollected_nodes'] = [node for node in wanted if node not in by_id]
        RECORD['selector_order_preserved'] = True
    RECORD['collected'] = [item.nodeid for item in items]
    RECORD['collected_parameter_indices'] = {item.nodeid: dict(item.callspec.indices)
                                              for item in items if hasattr(item, 'callspec')}


def pytest_collectreport(report):
    if report.failed:
        RECORD['collection_errors'].append({'nodeid': report.nodeid, 'detail': str(report.longrepr)})


def pytest_runtest_logreport(report):
    record = RECORD['outcomes'].setdefault(report.nodeid, {'phases': []})
    record['phases'].append({'when': report.when, 'outcome': report.outcome})
    if report.failed:
        record.update(status='failed' if report.when == 'call' else 'error', detail=str(report.longrepr))
    elif report.skipped:
        record['status'] = 'skipped'
    elif report.when == 'call' and record.get('status') not in ('failed', 'error'):
        record['status'] = 'passed'


def pytest_sessionfinish(session, exitstatus):
    RECORD['exitstatus'] = int(exitstatus)
    OUT.write_text(json.dumps(RECORD, ensure_ascii=False, indent=2), 'utf-8')
