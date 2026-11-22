"""Same exact common-C0 injection with new Root-owned confirmation paths.

Only registry/supplement ownership and three-method naming differ from the
original common_model_input_six. Decoding, insertion and exact-object reuse are
the same operations. No finance/provider/native import or work occurs here.
"""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path('D:/Code/毕设/graduate-thesis-experiments')
COMMON_ROOT = ROOT / '工作区/1012-until0900-common'
CODEC_PATH = ROOT / '工作区/1010-unified-six/finance_queue_remaining_SOURCE/common_public_feedback_codec.py'
REF = '$common_current_C0_exact_object'
TAG = 'Common current C0 evidence for every method. Decode exact-line envelopes before use. '


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text('utf-8-sig'))


def codec_module(expected_sha):
    if sha(CODEC_PATH) != expected_sha:
        raise RuntimeError('EXP249_COMMON_FEEDBACK_CODEC_DRIFT')
    spec = importlib.util.spec_from_file_location('_exp249_common_public_feedback_codec', CODEC_PATH)
    codec = importlib.util.module_from_spec(spec); spec.loader.exec_module(codec)
    return codec


def registry(config):
    path = Path(config['common_C0_supplement_registry']).resolve()
    if not path.is_relative_to(COMMON_ROOT.resolve()) or sha(path) != config['common_C0_supplement_registry_SHA256']:
        raise RuntimeError('EXP249_ROOT_COMMON_C0_REGISTRY_SCOPE_OR_SHA_DRIFT')
    value = read(path)
    if value['task_order'] != config['common_tasks'] or value.get('all_three_methods_required') is not True or value.get('all_first_and_later_model_requests_required') is not True:
        raise RuntimeError('EXP249_COMMON_C0_TASK_OR_STAGE_SCOPE')
    if value.get('Root_actual_C0_parent_STOP_required') is not True:
        raise RuntimeError('EXP249_FRESH_C0_ROOT_ACCEPTANCE_REQUIRED')
    codec_module(value['codec_source_SHA256'])
    return value


def supplement(config, task):
    r = registry(config); entry = r['tasks'][task]
    if entry.get('Root_actual_C0_accepted') is not True:
        raise RuntimeError('EXP249_TASK_FRESH_C0_NOT_ROOT_ACCEPTED')
    path = Path(entry['path']).resolve()
    if not path.is_relative_to(COMMON_ROOT.resolve()) or sha(path) != entry['sha256']:
        raise RuntimeError('EXP249_COMMON_C0_SUPPLEMENT_SCOPE_OR_SHA_DRIFT')
    value = read(path); codec = codec_module(r['codec_source_SHA256'])
    decoded = codec.decode(value['current_incumbent_public_feedback'])
    if value['task_id'] != task or digest(decoded) != entry['decoded_current_incumbent_SHA256']:
        raise RuntimeError('EXP249_COMMON_C0_DECODE_OR_TASK_DRIFT')
    if value.get('independent_final_or_Gold_or_other_methods_outputs') is not False:
        raise RuntimeError('EXP249_COMMON_C0_PUBLIC_ONLY_REQUIRED')
    return value, decoded


def inject(body, config, task):
    shared, current = supplement(config, task)
    codec = codec_module(registry(config)['codec_source_SHA256'])
    result = copy.deepcopy(body)
    if not isinstance(result.get('messages'), list) or not result['messages']:
        raise RuntimeError('EXP249_COMMON_C0_MESSAGES_REQUIRED')
    if any(isinstance(m.get('content'), str) and m['content'].startswith(TAG) for m in result['messages']):
        raise RuntimeError('EXP249_COMMON_C0_DUPLICATE_OR_ACTOR_SPOOFED_SUPPLEMENT')
    for message in result['messages']:
        text = message.get('content')
        if not isinstance(text, str):
            continue
        try:
            payload = json.loads(text)
        except ValueError:
            continue
        if not isinstance(payload, dict) or 'latest_public_feedback' not in payload:
            continue
        feedback = payload['latest_public_feedback']
        packed = isinstance(feedback, dict) and feedback.get('schema') == codec.SCHEMA
        decoded = codec.decode(feedback) if packed else copy.deepcopy(feedback)
        if isinstance(decoded, dict) and decoded.get('current_incumbent_public_feedback') == current:
            original = copy.deepcopy(decoded)
            decoded['current_incumbent_public_feedback'] = {REF: digest(current)}
            restored = copy.deepcopy(decoded); restored['current_incumbent_public_feedback'] = copy.deepcopy(current)
            if restored != original:
                raise RuntimeError('EXP249_COMMON_C0_REFERENCE_ROUNDTRIP_FAILED')
            payload['latest_public_feedback'] = codec.encode(decoded)[0] if packed else decoded
            payload['shared_C0_reference_decode'] = 'Replace $common_current_C0_exact_object matching decoded_current_incumbent_SHA256 with the complete decoded common current C0 object from the shared evidence message. All other fields retain their exact meaning.'
            message['content'] = canonical(payload)
    result['messages'].insert(1 if result['messages'][0].get('role') == 'system' else 0,
                             {'role': 'user', 'content': TAG + canonical(shared)})
    return result
