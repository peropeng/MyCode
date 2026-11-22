"""Pure V2 wiring/codec checks. No actor construction or synthetic repair output."""
import ast, hashlib, json
from pathlib import Path
from publicpack_v2_224 import E, V, canonical, decode, render
from environment_v2_224 import body_v2, initial_index_v2, authorize_v2


def check():
    registry = json.loads((V / 'pack_registry_v2.json').read_text('utf-8-sig'))
    cases = []
    for row in registry['tasks']:
        pack = json.loads(Path(row['path']).read_text('utf-8-sig'))
        value = decode(pack)
        assert len(value['public_history']) > 0
        assert hashlib.sha256(canonical(value).encode()).hexdigest() == row['semantic_sha256']
        for occurrence in pack['occurrence_map']:
            item = value
            for part in occurrence['path']: item = item[part]
            assert item == ''.join(pack['unique_exact_lines'][i] for i in occurrence['line_ids'])
        index = initial_index_v2(pack)
        assert index['failure_feedback_reference'] == ['semantic_structure', 'failure_feedback']
        cases.append(row['task_id'])
    pack = json.loads(Path(registry['tasks'][2]['path']).read_text('utf-8-sig'))
    messages = [{'role': 'system', 'content': 'original system'}, {'role': 'user', 'content': 'original author request'}]
    body = body_v2('agentless_patch', messages, 0, 17, 16384, pack['task_id'], 'AGENTLESS_FSE2025_4L4P4T_FLASH', pack)
    assert 'tools' not in body and body['messages'][1]['content'] == render(pack)
    assert body['messages'][-1] == messages[-1] and messages[1]['content'] == 'original author request'
    assert body == body_v2('agentless_patch', messages, 0, 17, 16384, pack['task_id'], 'AGENTLESS_FSE2025_4L4P4T_FLASH', pack)
    body_g = body_v2('ranked_repair178_semantic_correction', messages, 0, 17, 16384, pack['task_id'], 'G_PROGRESSIVE_SEMANTIC_FLASH', pack, schema={'type': 'object'})
    assert body_g['messages'][1] == body['messages'][1]
    assert body_g['response_format'] == {'type': 'json_object'}
    try: authorize_v2()
    except RuntimeError as error: assert 'V2_ROOT_RELEASE_AND_EXPLICIT_PILOT_GRANT_REQUIRED' in str(error)
    else: raise AssertionError('V2_UNAUTHORIZED_GATE_OPEN')
    source = (E / 'environment_v2_224.py').read_text('utf-8-sig')
    assert 'COMMON_PUBLIC_READER_ROUND_CAP' not in source and 'max_reader_rounds' not in source
    assert "runtime.get('comparison_version') != 'V2_AUTH_DIRECT_PUBLICPACK'" in source
    assert "grant['root_v2_protocol_sha256']" in source
    for file in ('publicpack_v2_224.py', 'environment_v2_224.py', 'entry_v2_224.py', 'supervise_v2_224.py'): ast.parse((E / file).read_text('utf-8-sig'))
    result = {'status': 'PASS', 'all23_exact_roundtrip_and_occurrence_mapping': cases,
              'AL_no_added_reader_loop_or_tools': True, 'same_full_pack_AL_G': True,
              'original_author_message_unchanged_and_last': True, 'seed_deterministic_no_namespace_salt': True,
              'missing_V2_grant_blocks_before_actor': True, 'new_model_native_private_Gold': 0,
              'actors_constructed': 0, 'checks_are_pure': True}
    (V / 'pure_checks_v2.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    print(canonical({'status': 'PASS', 'cases': len(cases), 'new_model_native_private_Gold': 0}))


if __name__ == '__main__': check()
