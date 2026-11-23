"""SHA-bound current public feedback and declared masked Goal AST hints.

Only current business code and already authorized masked public tests are read.
No candidate, private result, Gold, model or native process is consulted.
"""
import ast, copy, hashlib, json, re, textwrap
from pathlib import Path

def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)

def digest(value):return hashlib.sha256(canonical(value).encode()).hexdigest()
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text('utf-8-sig'))

def captured_goal_prefix(env,node,name):
    """Parse only the exact Goal function already printed by public pytest.

    Masked views intentionally replace Goal functions with Pass. The shared
    public failure can still contain a source prefix up to the failed assertion.
    This is audited as a prefix, never as a complete or newly unmasked test.
    """
    native=env._current_failure248['public_validation']['native_record']
    outcome=native['pytest']['outcomes'][node]
    candidates=[outcome.get('detail',''),native.get('stdout','')]
    pattern=re.compile(r'^\s*(?:>\s*)?def\s+'+re.escape(name)+r'\s*\(')
    for text in candidates:
        lines=text.splitlines()
        for start,line in enumerate(lines):
            if not pattern.match(line):continue
            prefix=[]
            for item in lines[start:]:
                if item.lstrip().startswith('>'):
                    pos=item.index('>');item=item[:pos]+' '+item[pos+1:]
                if item.strip() and not item.startswith('    '):break
                prefix.append(item)
            source=textwrap.dedent('\n'.join(prefix))
            try:tree=ast.parse(source)
            except SyntaxError:continue
            matches=[item for item in tree.body if isinstance(item,(ast.FunctionDef,ast.AsyncFunctionDef)) and item.name==name]
            if len(matches)==1:
                return matches[0],{'public_capture_prefix_SHA256':hashlib.sha256(source.encode()).hexdigest(),
                    'source':'Current complete public native failure already shared with all methods',
                    'extraction_rule':'Find exact declared Goal def name in current outcome.detail, else current stdout; retain pytest displayed indented code lines until first non-source line; replace pytest > marker by one space, dedent, parse only this already public prefix.',
                    'source_native_witness_SHA256':env._current_failure248_binding['source_native_witness_SHA256'],
                    'complete_test_function_claim':False,'read_unmasked_test_file':False,
                    'current_feedback_semantic_SHA256':digest(env._current_failure248)}
    return None,None

def goal_body_calls(function):
    # Decorator expressions alone do not establish an executable Goal body.
    return [call for statement in function.body for call in ast.walk(statement) if isinstance(call,ast.Call)]

def prefer_observed_goal(env,node,name,target):
    usable=isinstance(target,(ast.FunctionDef,ast.AsyncFunctionDef)) and bool(goal_body_calls(target))
    if usable:return target,None
    captured,provenance=captured_goal_prefix(env,node,name)
    return (captured,provenance) if captured is not None else (target,None)

def masked_goal_calls(env):
    protocol=read(env.protocol_origin)
    reference=protocol['public_test_scope_contract']
    if sha(reference['path'])!=reference['sha256']:raise RuntimeError('EXP248_MASKED_SCOPE_DRIFT')
    scope=next(row for row in read(reference['path'])['tasks'] if row['task_id']==env.task_id)
    allowed=scope['public_test_py_files_SHA256'];root=Path(scope['public_source_repo_view']).resolve()
    calls=[];audit=[]
    for node in env.recovery_goal_nodes:
        parts=node.split('::');rel=parts[0].replace('\\','/');record={'Goal_node':node,'masked_path':rel,'consumer_calls':[]}
        if rel not in allowed:
            record['status']='GOAL_PATH_HAS_NO_DECLARED_MASKED_PY_AST';audit.append(record);continue
        path=(root/rel).resolve()
        if not path.is_relative_to(root) or sha(path)!=allowed[rel]:raise RuntimeError('EXP248_MASKED_GOAL_SOURCE_DRIFT')
        tree=ast.parse(path.read_text('utf-8-sig'),filename=rel)
        target=tree;resolved=True
        for segment in parts[1:]:
            name=segment.split('[',1)[0]
            matches=[item for item in getattr(target,'body',[]) if isinstance(item,(ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef)) and item.name==name]
            if len(matches)!=1:resolved=False;break
            target=matches[0]
        record.update(masked_source_SHA256=allowed[rel],status='EXACT_PUBLIC_GOAL_AST' if resolved and isinstance(target,(ast.FunctionDef,ast.AsyncFunctionDef)) else 'DYNAMIC_GOAL_WITHOUT_EXACT_PY_FUNCTION')
        if record['status']!='EXACT_PUBLIC_GOAL_AST' or not goal_body_calls(target):
            target,captured=prefer_observed_goal(env,node,parts[-1].split('[',1)[0],target if resolved else None)
            if captured is not None:record.update(status='ALREADY_PUBLIC_EXACT_GOAL_SOURCE_PREFIX_AST',**captured)
            elif record['status']=='EXACT_PUBLIC_GOAL_AST':record['status']='DECLARED_MASKED_GOAL_WITHOUT_USABLE_CALL_OR_PUBLIC_PREFIX'
        if record['status'] in ('EXACT_PUBLIC_GOAL_AST','ALREADY_PUBLIC_EXACT_GOAL_SOURCE_PREFIX_AST'):
            record.update(function_start=target.lineno,function_end=target.end_lineno)
            for call in goal_body_calls(target):
                function=call.func
                name=function.attr if isinstance(function,ast.Attribute) else function.id if isinstance(function,ast.Name) else None
                if not name:continue
                entry={'method_name':name,'Goal_node':node,'masked_path':rel,'masked_source_SHA256':allowed[rel],'call_line':call.lineno,'AST_source_status':record['status'],'static_possible_reference':True,'causal_claim':False}
                if 'public_capture_prefix_SHA256' in record:entry['public_capture_prefix_SHA256']=record['public_capture_prefix_SHA256']
                calls.append(entry);record['consumer_calls'].append(name)
        audit.append(record)
    return calls,audit

def anchor_input(env,payload,files,latest_current):
    actual={path:hashlib.sha256(text.encode()).hexdigest() for path,text in sorted(files.items())}
    feedback=copy.deepcopy(payload.get('latest_public_feedback',{}).get('current_incumbent_public_feedback'))
    if not isinstance(feedback,dict) or feedback.get('observed_business_inventory_sha256')!=digest(actual):
        raise RuntimeError('EXP248_CURRENT_PUBLIC_FEEDBACK_SOURCE_MISMATCH')
    if feedback.get('observation_is_current_accepted_incumbent') is not True or feedback.get('all_public_coverage_actual_complete_guarded') is not True:
        raise RuntimeError('EXP248_CURRENT_PUBLIC_FEEDBACK_NOT_COMPLETE_ACCEPTED')
    native=feedback['public_validation']['native_record']
    if not native.get('exact_test_coverage') or not native.get('executed') or native.get('timeout') or not native.get('frozen_tests_unchanged'):
        raise RuntimeError('EXP248_CURRENT_NATIVE_CAPTURE_UNKNOWN')
    env._current_failure248=copy.deepcopy(feedback)
    witness=env._native_witness_by_inventory.get(digest(actual))
    if not witness:raise RuntimeError('EXP248_CURRENT_CAPTURE_WITHOUT_SOURCE_BOUND_NATIVE_WITNESS')
    env._current_failure248_binding={'source_inventory_SHA256':digest(actual),'current_feedback_semantic_SHA256':digest(feedback),
        'source_native_witness_SHA256':witness,
        'current_native_stdout_SHA256':hashlib.sha256(native.get('stdout','').encode()).hexdigest(),
        'current_native_stderr_SHA256':hashlib.sha256(native.get('stderr','').encode()).hexdigest(),
        'feedback_is_current_accepted_incumbent':True,'native_capture_is_complete_public':True}
    calls,mask_audit=masked_goal_calls(env)
    return {'current_incumbent_public_feedback':feedback,
        'current_native_public_captured_output':{'stdout':native.get('stdout',''),'stderr':native.get('stderr','')},
        'current_binding':env._current_failure248_binding,
        'initial_public_failure':copy.deepcopy(env.initial_public_feedback),
        'initial_original_public_captured_output_historical':copy.deepcopy(env._initial_public_captured_output),
        'initial_history_is_not_current_source':True,
        'public_goal_masked_test_calls':calls,'public_goal_masked_test_AST_audit':mask_audit}

def finish_body(env,body):
    """Move complete derived source spans to the last user message, once only."""
    found=[];tail=None;retained=[]
    for message in body['messages']:
        try:value=json.loads(message.get('content',''))
        except (ValueError,TypeError):value=None
        if isinstance(value,dict) and value.get('schema')=='current-public-feedback-source-binding/1':
            tail=value
        else:retained.append(message)
    body['messages']=retained
    for message in body['messages']:
        if message.get('role')!='user' or not isinstance(message.get('content'),str):continue
        try:payload=json.loads(message['content'])
        except ValueError:continue
        if not isinstance(payload,dict) or 'additional_business_context' not in payload:continue
        context=payload['additional_business_context']
        if 'source_context' not in context:continue
        spans=context.pop('source_context')
        context['complete_source_context_reference']='The final user message current_business_functions contains these same whole current SHA-bound spans exactly once.'
        statuses=env._current_failure248['public_validation']['native_record']['pytest']['outcomes']
        goal_outcomes={'actual_PASS_count':sum(statuses[node]['status']=='passed' for node in env.recovery_goal_nodes),
                       'actual_failed_error_count':sum(statuses[node]['status'] in ('failed','error') for node in env.recovery_goal_nodes),
                       'complete_node_status_phase_reference':'The complete current_incumbent_public_feedback in the existing lossless public feedback/C0 evidence; no outcomes are omitted there.'}
        tail={'schema':'current-public-feedback-source-binding/1','binding':copy.deepcopy(env._current_failure248_binding),
              'current_public_Goal_summary':goal_outcomes,'current_business_functions':spans,
              'current_source_is_authoritative':True,'historical_before_after_is_never_current_source':True,
              'repair_requirement':'If a current public Goal is failed/error, a repair is still required; an empty edit does not establish recovery. Diagnose using this current source and current complete public capture; preserve accepted Goal PASS and ordinary PASS.',
              'SEARCH_requirement':'Every edit.old must match exactly one span in the current SHA-bound business file. Copy the exact current text, including indentation. If a needed whole span is absent, use the authorized current source reader before proposing edits. A historical before/after image is evidence only.',
              'no_task_specific_patch_or_other_method_output':True}
        # The original derived-context bound includes relationship metadata and
        # source; moving the source does not duplicate it or enlarge the bound.
        if len(canonical({'metadata':context,'tail':tail}).encode())>65536:
            raise RuntimeError('EXP248_DERIVED_SOURCE_AND_METADATA_BOUND_EXCEEDED_NO_CLIPPING')
        message['content']=canonical(payload);found.append(payload['attempt'])
    if tail is None:raise RuntimeError('EXP248_MAIN_REQUEST_MISSING_CURRENT_SOURCE_BINDING')
    if len(found)>1:raise RuntimeError('EXP248_MULTIPLE_CURRENT_MAIN_PAYLOADS')
    body['messages'].append({'role':'user','content':canonical(tail)})
    return body
