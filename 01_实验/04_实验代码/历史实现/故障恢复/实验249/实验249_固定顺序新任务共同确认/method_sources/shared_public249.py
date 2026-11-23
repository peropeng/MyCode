"""Common public-only task resources. Never read a task_manifest or private tree."""
import copy
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
E249 = HERE.parent
ROOT = Path('D:/Code/毕设/graduate-thesis-experiments')
SOURCE = ROOT / '工作区/1008-2320-exp224-flash-common/实验/实验224_二十三题Flash完整共同恢复比较'
REFS = SOURCE / 'data/selected_task_bindings.json'
INPUTS = SOURCE / 'data/public_inputs.jsonl'
PLANS = SOURCE / 'ranking/plan_registry224.json'


def read(path):
    return json.loads(Path(path).read_text('utf-8-sig'))


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def decode(pack):
    pool = pack['unique_exact_lines']
    def visit(value):
        if isinstance(value, dict) and set(value) == {'$public_text_lines'}:
            return ''.join(pool[i] for i in value['$public_text_lines'])
        if isinstance(value, dict):
            return {key: visit(item) for key, item in value.items()}
        if isinstance(value, list):
            return [visit(item) for item in value]
        return value
    result = visit(pack['semantic_structure'])
    if digest(result) != pack['decoded_semantic_sha256']:
        raise RuntimeError('EXP249_COMMON_PUBLIC_PACK_DECODE_DRIFT')
    return result


def load_public_task(task_id, public_contract_path=None, refs_path=None):
    """Return contract/pack/semantic/ref/sample plus public resources() shape.

    This does not confer current-C0 qualification. Root's fresh witness is a
    separate mandatory input to every method's generation contract.
    """
    source = read(HERE / 'PUBLIC_SOURCE_BINDINGS249.json')
    if task_id not in source['task_order']:
        raise RuntimeError('EXP249_FIXED_SIX_TASK_REQUIRED')
    for path, expected in source['public_inputs_SHA256'].items():
        if sha(path) != expected:
            raise RuntimeError('EXP249_COMMON_PUBLIC_INPUT_DRIFT ' + path)
    selected = source['tasks'][task_id]
    cpath = Path(public_contract_path or selected['public_contract']).resolve()
    if cpath != Path(selected['public_contract']).resolve() or sha(cpath) != selected['public_contract_SHA256']:
        raise RuntimeError('EXP249_EXACT_PUBLIC_CONTRACT_REQUIRED')
    refpath = Path(refs_path or REFS).resolve()
    if refpath != REFS.resolve():
        raise RuntimeError('EXP249_EXACT_PUBLIC_REFS_REQUIRED')
    contract = read(cpath)
    pack = read(contract['pack'])
    if pack['task_id'] != task_id or sha(contract['pack']) != contract['pack_sha256']:
        raise RuntimeError('EXP249_PUBLIC_PACK_TASK_DRIFT')
    semantic = decode(pack)
    ref = copy.deepcopy(next(v for v in read(REFS)['tasks'] if v['task_id'] == task_id))
    if sha(ref['G_frozen_plan']) != selected['G_frozen_plan_SHA256']:
        raise RuntimeError('EXP249_RQ1_FROZEN_PLAN_DRIFT')
    sample = None
    with INPUTS.open('r', encoding='utf-8-sig') as stream:
        for line in stream:
            value = json.loads(line)
            if value.get('sample_id') == task_id:
                if sample is not None:
                    raise RuntimeError('EXP249_DUPLICATE_PUBLIC_SAMPLE')
                sample = value
    if sample is None or sample.get('gold_or_reference_patch_included') is not False:
        raise RuntimeError('EXP249_PUBLIC_PREFIX_NOT_EXACT_OR_GOLD_FLAG')
    turn_sha = hashlib.sha256(json.dumps(sample['turns'], sort_keys=True).encode()).hexdigest()
    if turn_sha != ref['input_turns_sha256']:
        raise RuntimeError('EXP249_PUBLIC_PREFIX_RQ1_TURN_BINDING_DRIFT')
    manifest = {'schema': 'EXP249-public-only-resources-view/1', 'task_id': task_id,
        'repository': contract['repository'], 'package': contract['package'],
        'runtime_source_root': contract['template'], 'native_interpreter': contract['logical_product_python'],
        'asset_root': ref['asset_root'], 'frozen_tests': {'path': contract['frozen_public_test_root']},
        'visible_target_tests': list(contract['public_target_nodes']),
        'public_regression_tests': list(contract['ordinary_nodes']), 'hidden_preservation_tests': [],
        'hidden_fields_are_unavailable_not_empty_acceptance_requirement': True,
        'independent_acceptance_only_external_Root_after_immutable_selection_and_STOP': True,
        'current_C0_qualification_inherited': False, 'private_manifest_read': False}
    paths = {'template': Path(contract['template']), 'frozen': Path(contract['frozen_public_test_root']),
             'python': Path(contract['logical_product_python']), 'asset_root': Path(ref['asset_root'])}
    return {'task_id': task_id, 'contract': contract, 'pack': pack, 'semantic': semantic,
            'public_ref': ref, 'export_input': copy.deepcopy(sample), 'resources_manifest': manifest,
            'resources_paths': paths, 'frozen_inventory': copy.deepcopy(contract['frozen_inventory']),
            'source_binding': copy.deepcopy(selected), 'private_or_Gold_read': False}


def resources(task_id, public_contract_path=None):
    value = load_public_task(task_id, public_contract_path)
    return value['resources_manifest'], value['resources_paths']


def export_input(task_id, public_contract_path=None):
    return load_public_task(task_id, public_contract_path)['export_input']
