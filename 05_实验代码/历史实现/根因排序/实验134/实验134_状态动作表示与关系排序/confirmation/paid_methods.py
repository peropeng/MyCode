"""Pinned native baselines and the pre-frozen display-qualifier repair only."""
import re
import sys
from shared import *
sys.path.insert(0,str(RES))
import llm_methods
import baseline_adapter

_canonical=llm_methods.canonical_role
def canonical_public_display(value,record):
    role=_canonical(value,record)
    if role is not None:return role
    match=re.fullmatch(r'\s*(.+?)\s*\(([^()\n]+)\)\s*',str(value))
    return _canonical(match.group(1),record) if match else None
llm_methods.canonical_role=canonical_public_display

def diagnose(condition,record,client):
    if condition=='AA_STRUCTURED':
        packet=EVENTS.representation(record)
        user=llm_methods.all_at_once_prompt(record['task'],EVENTS.canonical(packet))
        receipts=[]
        try:
            response=client.generate([{'role':'system','content':llm_methods.ALL_AT_ONCE_SYSTEM},{'role':'user','content':user}],
                sample_id=record['sample_id'],stage='AA_STRUCTURED/localization',max_tokens=1200,remaining_seconds=120)
            receipts.append(response)
            if response['finish_reason']!='stop':raise llm_methods.FormatError('response_token_limit_or_incomplete')
            parsed=AA_PARSER.parse_structured_aa(response['text'],record,llm_methods)
            return {'valid':True,'chosen_step':parsed['predicted_step'],'predicted_role':parsed['predicted_role'],
                'native_agent_output':parsed['native_agent_output'],'role_output_origin':'native_model',
                'native_complete_ranking':False,'order':None,'format_valid':True,'native_output':parsed,
                'call_ids':[r['request_id'] for r in receipts],'status':'completed'}
        except (ValueError,TypeError,KeyError) as exc:
            return {'valid':False,'chosen_step':None,'predicted_role':None,'order':None,'native_complete_ranking':False,
                'format_valid':False,'error':str(exc),'status':'invalid_output','call_ids':[r['request_id'] for r in receipts]}
    method={'AA':'all_at_once','Binary':'binary_search','SDBL':'sdbl'}[condition]
    result=baseline_adapter.diagnose(method,record,client)
    chosen=result.get('predicted_step');valid=bool(result.get('format_valid')) and type(chosen) is int and 0<=chosen<len(record['turns'])
    return {**result,'valid':valid,'chosen_step':chosen if valid else None,'order':None,'native_complete_ranking':False,
        'role_output_origin':'native_model' if condition in ('AA','SDBL') else 'derived_from_chosen_public_step',
        'display_parser_version':'exact public actor plus optional parenthesized display qualifier; native string retained'}

def static_payloads(record):
    sid=record['sample_id'];out=[]
    def add(condition,stage,system,user,cap):out.append({'sample_id':sid,'condition':condition,'stage':stage,'max_tokens':cap,
        'messages':[{'role':'system','content':system},{'role':'user','content':user}]})
    problem=llm_methods.public_problem(record);raw=llm_methods.conversation(record)
    add('AA','all_at_once/localization',llm_methods.ALL_AT_ONCE_SYSTEM,llm_methods.all_at_once_prompt(problem,raw),2048)
    add('AA_STRUCTURED','AA_STRUCTURED/localization',llm_methods.ALL_AT_ONCE_SYSTEM,
        llm_methods.all_at_once_prompt(record['task'],EVENTS.canonical(EVENTS.representation(record))),1200)
    kb=baseline_adapter.source_unknown_permissions(record)
    add('SDBL','sdbl/scope','You delineate failure-attribution scope using explicitly supplied expert knowledge.',llm_methods.scope_prompt(record,kb),2048)
    # The exact localization payload is preflighted again at send time with the
    # actual paid scope. This public empty-scope template qualifies its format.
    add('SDBL','sdbl/localization','You localize failure responsibility using full execution logs and a scope hint.',llm_methods.localization_prompt(record,[]),2048)
    def intervals(lo,hi):
        if lo==hi:return
        mid=lo+(hi-lo)//2
        prompt=llm_methods.binary_search_prompt(problem,llm_methods.conversation(record,lo,hi),
            f'from step {lo} to step {hi}',f'from step {lo} to step {mid}',f'from step {mid+1} to step {hi}')
        add('Binary',f'binary_search/interval_{lo}_{hi}',llm_methods.BINARY_SEARCH_SYSTEM,prompt,128)
        intervals(lo,mid);intervals(mid+1,hi)
    intervals(0,len(record['turns'])-1)
    return out
