"""Zero-paid checks of native parsers, projection, stats and payload bounds."""
import math
from shared import *
import paid_methods as methods
import paired_stats

def main():
    record={'sample_id':'SYNTHETIC_CONTRACT_ONLY','task':'Implement a square function.','turns':[
        {'role':'Engineer','content':'Engineer thinking:# Past Experience\n# Tool State\n# Current Plan','action':'','thought':''},
        {'role':'Engineer','content':'Engineer thinking: public action','action':'','thought':''},
        {'role':'Reviewer','content':'Reviewer thinking: review','action':'','thought':''}],
        'coordinate_map':[{'original_step_id':i} for i in range(3)]}
    parsed=methods.llm_methods.parse_diagnosis('Agent Name: Engineer (Alex)\nStep Number: 1\nReason for Mistake: observed action.',record)
    if parsed['predicted_step']!=1 or parsed['native_agent_output']!='Engineer (Alex)':raise AssertionError('display qualifier changed step/native actor')
    original={'valid':True,'chosen_step':1,'predicted_role':'Engineer','order':[1,0,2]}
    projected=event_projection(original,record,'AA_OBSERVED_EVENT_STATE_PROJECTION','AA')
    if projected['chosen_step']!=0 or projected['order'] is not None or original['order']!=[1,0,2] or original['chosen_step']!=1:raise AssertionError('projection mutates original or fabricates rank')
    record['coordinate_map'][1]['original_step_id']=9
    if event_projection(original,record,'AA_OBSERVED_EVENT_STATE_PROJECTION','AA')['chosen_step']!=1:raise AssertionError('unproven event pairing shifts an ordinal')
    checks={str(i):([1]*8,[0]*8) for i in range(13)};family=paired_stats.family(checks,13)
    if any(r['family_tests']!=13 or r['exact_mcnemar_two_sided_p']!=.0078125 for r in family.values()):raise AssertionError('primary exact/13-family statistics wrong')
    bound=module(RES/'official_codec/payload_bound.py','exp134_contract_bound')
    records=read(T/'fresh_public_records.json')['records'];count=0;max_bytes=0
    for r in records:
        for payload in methods.static_payloads(r):
            body={'model':'deepseek-flash','messages':payload['messages'],'temperature':0,'max_tokens':payload['max_tokens'],
                'stream':False,'thinking':{'type':'disabled'}}
            proof=bound.render_exact_bound(body);size=proof['encoded_utf8_bytes']
            if size+payload['max_tokens']>1048576:raise AssertionError('public payload exceeds qualified context')
            count+=1;max_bytes=max(max_bytes,size)
    receipt={'at_utc':now(),'native_display_parser_preserves_ordinal_and_string':True,'no_unproven_projection':True,
        'no_fabricated_single_choice_rank':True,'complete13_primary_family_checked':True,'public_payloads_preflighted':count,
        'largest_complete_framing_input_UTF8_bytes':max_bytes,'paid_API_calls':0,'fresh_Gold_accesses':0}
    write(T/'contract_check.json',receipt);print(canonical({'contract_checks':'passed','exact_public_payloads':count,'paid_API_calls':0}),flush=True)

if __name__=='__main__':main()
