"""Prepared isolated Main phase routing; no frozen files or model logic changed."""
from common166 import *
import environment_v2_224 as frozen
import common_environment224 as shared
from publicpack_v2_224 import V
from fresh_entry224 import budget_disposition

PIN = V / 'main_addendum_source_pin_v2.json'
GRANT = V / 'root_main_grant_v2.json'
PARENT = '5e4d6014eab1125040e059019f245efc1d2399a30b8e8aa9a385b451226351d0'
PACK = '298efeac0dcf0498ed8f78e0067c8e24a963e24c29442fc0df64d8e047b7a37c'
MAIN_VERSION = 'V2_AUTH_DIRECT_PUBLICPACK_MAIN'
MAIN_PROTOCOL = ROOT / '工作区/1008-2320-baseline-main/frozen_main_v2_remaining21_protocol.json'
MAIN_PROTOCOL_SHA = '9571c1cb0bd4751bbc695826aa4cf79d7b1ff2cab21cda72295bd84dd9ecc455'
_original_module = frozen.module


def authorize_main():
    if not GRANT.exists(): raise RuntimeError('V2_MAIN_EXPLICIT_ROOT_FREEZE_AND_GRANT_REQUIRED')
    grant = read(GRANT); runtime = read(ROOT / '工作区/1008-2320-baseline-main/coordination/runtime_release.json')
    assert runtime.get('root_runtime_ready') is True and runtime.get('comparison_version') == MAIN_VERSION
    assert grant.get('root_authorized') is True and grant.get('version') == MAIN_VERSION
    assert grant.get('phase') == 'Round2320Main', 'V2_MAIN_NOT_A_PILOT_FALLBACK'
    assert grant.get('main_source_pin_sha256') == sha(PIN)
    assert grant.get('source_seal_sha256') == sha(V / 'source_seal_v2.json') == PARENT
    assert grant.get('pack_registry_sha256') == sha(V / 'pack_registry_v2.json') == PACK
    assert sha(frozen.ROOT_V2_PROTOCOL) == frozen.ROOT_V2_SHA
    protocol_path = MAIN_PROTOCOL.resolve()
    assert protocol_path.is_relative_to(ROOT / '工作区/1008-2320-baseline-main')
    assert sha(protocol_path) == grant['root_main_protocol_sha256'] == runtime.get('root_main_protocol_sha256') == MAIN_PROTOCOL_SHA
    protocol = read(protocol_path); pin = read(PIN)
    expected_order = [x for x in read(frozen.ROOT_V2_PROTOCOL)['cohort']['order']
                      if x not in ('dask__dask-9378', 'getmoto__moto-5072')]
    assert pin['task_order'] == expected_order and len(expected_order) == 21, 'V2_MAIN_CALIBRATION_REPLAY_FORBIDDEN'
    assert protocol['version'] == MAIN_VERSION and protocol['finance']['phase'] == 'Round2320Main'
    assert protocol['execution_order_remaining21'] == pin['task_order']
    assert protocol['calibration_primary_eligible'] is False and protocol['parent_v2_protocol_sha256'] == frozen.ROOT_V2_SHA
    through = int(grant.get('allowed_through_index', -1)); assert through >= 0
    if through > 0:
        assert grant.get('V2_EnAgent_complete_nonzero_root_accepted') is True, 'MAIN_BIG_QUEUE_REQUIRES_ACTUAL_V2_ENAGENT'
    assert grant.get('max_lead_cases') == 1
    for path, expected in {**read(V / 'source_seal_v2.json')['sealed_files'], **pin['new_sources'], **pin['read_only_inputs']}.items():
        assert sha(path) == expected, 'V2_MAIN_SOURCE_OR_INPUT_DRIFT ' + path
    if time.time() >= NO_TEST: raise RuntimeError('NO_NEW_V2_MAIN_AFTER_AUTHORIZED_CUTOFF')
    base = read(V / 'protocol_v2.json')
    assert (protocol['budget']['model_calls_total'], protocol['budget']['output_tokens_total'], protocol['budget']['wall_seconds']) == (64, 65536, 900)
    assert protocol['budget']['role_output_caps'] == base['budget']['role_output_caps']
    # Only the response provenance version changes; body/seed construction ignores it.
    return {**base, 'version': MAIN_VERSION}


def routed_module(name, path):
    m = _original_module(name, path)
    if Path(path).resolve() != Path(TRANSPORT).resolve(): return m
    class MainTransport:
        @staticmethod
        def generate(env, body, role, phase):
            authorize_main()
            assert phase == 'Round2320Pilot', 'FROZEN_PHASE_CALLSITE_DRIFT'
            env.finance_phase = 'Round2320Main'
            env.record('V2_MAIN_EXPLICIT_PHASE_ROUTING', {'original_frozen_callsite_phase': phase,
                       'actual_registered_finance_phase': 'Round2320Main', 'main_source_pin_sha256': sha(PIN),
                       'body_and_seed_unchanged': True, 'not_a_retry_or_pilot_rejection_fallback': True})
            return m.generate(env, body, role, phase='Round2320Main')
    return MainTransport


def install_isolated_main():
    # Only globals in this new dedicated Main process change. No shared source,
    # original seal, running Pilot worker or peer process is modified.
    frozen.authorize_v2 = authorize_main
    frozen.module = routed_module
    shared.authorization = authorize_main


class MainEnvironmentV2(frozen.EnvironmentV2):
    def __init__(self, ref, method):
        authorize_main()
        super().__init__(ref, method)
        self.finance_phase = 'Round2320Main'

    def finalize(self, result):
        context = self.budget_context()
        if budget_disposition(result, context) or self.finance_fatal or result.get('engineering_outcome_unknown'):
            return super().finalize(result)
        core_complete = result.get('runtime_core', {}).get('complete') is True
        selected = result.get('final_snapshot') or {}
        if not core_complete or not selected.get('diff'):
            normal = result.get('status') == 'MODEL_SEMANTIC_FAILURE' or result.get('declared_method_failure_known') is True
            disposition = {'status': result.get('status') if normal else 'ENGINEERING_UNKNOWN',
                           'success': False if normal else None,
                           'reason': 'NORMAL_TERMINAL_WITHOUT_COMPLETE_LEGAL_SELECTED_EDIT' if normal else 'INCOMPLETE_CORE_NO_PRIVATE'}
            return self.closed_result(result, disposition)
        return super().finalize(result)
