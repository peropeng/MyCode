"""Audit the unchanged full qualified pool and freeze the remaining fresh groups."""
from collections import Counter,defaultdict
import hashlib
import json
from pathlib import Path,PurePosixPath
import re
import sys
import unicodedata
import zipfile
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent;E=T.parent
sys.path.insert(0,str(E));from common import *
H=ROOT/'工作区/1005-exp132-paper-three/实验/实验132_论文驱动三案归因对比'
V=H/'engineering_v2';P=H.parents[1]/'scratch/exp132'
CAP=64000

def norm(s):return re.sub(r'\s+',' ',unicodedata.normalize('NFC',s).strip()).casefold()
def main():
    decision=read(T/'approved_decision.json')
    if sha(E/'training/model_seal.json')!=decision['model_seal_sha256']:raise RuntimeError('root-frozen_model_seal_changed')
    qualified=read(H/'metadata/agentracer_exact_step_qualification.json')
    public_path=P/'agentracer_exact_mapping_public.jsonl'
    if sha(public_path)!=qualified['public_file_sha256']:raise RuntimeError('prior_public_qualification_changed')
    prior=read(V/'expansion_v4/expansion_plan_expanded_frontier_peak.json')
    if prior['qualified_remaining_groups_6_to16_steps']!=96 or prior['public_pool_counts'][str(CAP)]!=96:raise RuntimeError('inherited_complete_public_pool_cap_not_verified')
    parent={};identity={};splits={}
    def root(x):
        parent.setdefault(x,x)
        while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
        return x
    def union(a,b):
        a,b=root(a),root(b)
        if a!=b:parent[max(a,b)]=min(a,b)
    with zipfile.ZipFile(SOURCE_ZIP) as archive:
        for member in archive.namelist():
            if not member.endswith('.jsonl'):continue
            domain,split=PurePosixPath(member).parts[-2:];split=split.removesuffix('.jsonl')
            with archive.open(member) as f:
                for index,line in enumerate(f):
                    if not line.strip():continue
                    row=public_object(line,{'question','question_ID'});rid=f'{domain}/{split}/{index}'
                    keys=['question:'+hashlib.sha256(norm(row['question']).encode()).hexdigest(),
                          'source-question:'+domain+':'+str(row['question_ID'])]
                    union(*keys);identity[rid]=keys;splits[rid]=split
    components=defaultdict(set)
    for keys in identity.values():
        for key in keys:components[root(key)].add(key)
    gids={key:digest(sorted(values)) for key,values in components.items()}
    group_for={rid:gids[root(keys[0])] for rid,keys in identity.items()};group_splits=defaultdict(set)
    for rid,split in splits.items():group_splits[group_for[rid]].add(split)
    exposures={};source_hashes={}
    def expose_file(path,expected=None):
        if not path.exists():raise RuntimeError('missing_required_exposure_manifest:'+str(path))
        if expected and sha(path)!=expected:raise RuntimeError('exposure_manifest_hash_changed:'+str(path))
        source_hashes[str(path)]=sha(path)
        for record in read(path)['records']:
            rid=record['record_id'];group=group_for[rid]
            if record.get('task_group')!=group:raise RuntimeError('historical_group_identity_changed:'+rid)
            exposures.setdefault(group,set()).add(str(path))
    expose_file(H/'data/public_records.json',read(H/'data/public_input_seal.json')['public_records_sha256'])
    for phase in ('common_dev','common_blind'):
        folder=V/'results'/phase
        expose_file(folder/'public_records.json',read(folder/'protocol.json')['public_records_sha256'])
    expose_file(V/'interface_repair_v5/results/public_records.json',read(V/'interface_repair_v5/results/protocol.json')['public_records_sha256'])
    # The actual continuous exposure ledger covers every prior paid condition,
    # including interrupted/generated tasks absent from a completion manifest.
    ledger_path=V/'api/requests.jsonl';source_hashes[str(ledger_path)]=sha(ledger_path)
    for line in ledger_path.read_text('utf-8').splitlines():
        event=json.loads(line)
        if event.get('event')!='reserved':continue
        sid=event.get('sample_id','');parts=sid.split(':')
        if len(parts)!=6 or parts[0]!='AgenTracer' or not parts[-1].isdigit():continue
        rid=f'{parts[2]}/{parts[3]}/{int(parts[-1])}'
        if rid not in group_for:raise RuntimeError('exposed_source_identity_not_in_release:'+sid)
        exposures.setdefault(group_for[rid],set()).add('continuous_API_reserved:'+sid)
    train_groups={r['task_group'] for r in read(E/'data/public_split_manifest.json')['records']}
    pool=defaultdict(list);excluded=Counter()
    for line in public_path.read_text('utf-8').splitlines():
        if not line:continue
        row=json.loads(line);group=group_for[row['record_id']]
        if row['source_split']!='test':continue
        if group in exposures:excluded['historically_exposed_rows']+=1;continue
        if group_splits[group]!={'test'} or group in train_groups:excluded['author_train_crossing_or_selected_train_rows']+=1;continue
        if not 6<=row['num_steps']<=16 or row['public_utf8_bytes']>CAP:excluded['outside_inherited_public_scope_rows']+=1;continue
        sid=f'AgenTracer:data-v1.0.0:{row["domain"]}:test:{row["question_ID"]}:{row["source_row"]:06d}'
        pool[group].append({**row,'sample_id':sid,'task_group':group})
    representatives={group:min(values,key=lambda r:r['sample_id']) for group,values in pool.items()}
    salt=decision['selection']['sampling_salt'];priority=lambda group:(hashlib.sha256((salt+'|'+group).encode()).hexdigest(),group)
    available=sorted(representatives,key=priority)
    if len(available)<32:raise RuntimeError('remaining_fully_audited_pool_below_minimum32:'+str(len(available)))
    chosen=available[:64];records=[];manifest=[]
    for group in chosen:
        row=representatives[group]
        turns=[{'role':step.get('name') or step['role'],'content':step['content'],'action':'','thought':'',
                'original_step_id':step['step_id']} for step in row['steps']]
        coords=[{'ordinal_zero_based':step['ordinal'],'original_step_id':step['step_id'],
                 'source_channel_role':step['role'],'source_actor_name':step.get('name')} for step in row['steps']]
        record={'sample_id':row['sample_id'],'record_id':row['record_id'],'phase':'fresh_confirmation','task_group':group,
            'task':row['question'],'turns':turns,'coordinate_map':coords,'domain':row['domain'],'source_split':'test',
            'source_member':row['source_member'],'source_row':row['source_row']}
        records.append(record);manifest.append({'sample_id':row['sample_id'],'record_id':row['record_id'],'task_group':group,
            'domain':row['domain'],'steps':row['num_steps'],'qualification_public_UTF8_bytes':row['public_utf8_bytes'],
            'public_record_sha256':digest(record),'salt_priority':priority(group)[0]})
    write_new(T/'fresh_public_records.json',{'records':records,'Gold_answer_reason_fields_present':False})
    write_new(T/'fresh_sample_manifest.json',{'at_utc':now(),'records':manifest,'available_fully_audited_groups':len(available),
        'actual_n':len(records),'public_steps':[6,16],'inherited_complete_pool_public_UTF8_cap':CAP,
        'prior_N32_20667_cap_was_cohort_specific_not_full_qualified_pool':True,
        'historical_exposure_sources':source_hashes,'exclusion_counts':dict(excluded),'salt':salt,
        'all_possible_historical_API_reservations_excluded':True,'any_author_train_component_excluded':True,
        'unseen_label_values_parsed':0,'new_model_predictions':0,'decision_sha256':sha(T/'approved_decision.json')})
    write_new(T/'historical_exposure_ledger.json',{'at_utc':now(),'groups':{group:sorted(sources) for group,sources in exposures.items()},
        'source_hashes':source_hashes,'all_groups_are_prior_to_current_confirmation':True})
    write_new(T/'public_scope_seal.json',{'at_utc':now(),'public_records_sha256':sha(T/'fresh_public_records.json'),
        'manifest_sha256':sha(T/'fresh_sample_manifest.json'),'actual_n':len(records),'Gold_accesses':0,
        'before_any_fresh_model_prediction_or_paid_request':True})
    status('EXP134_CONFIRMATION_PUBLIC_SCOPE_FROZEN',fresh_confirmation={'completed_tasks':0,'total_tasks':len(records),'unexposed_test_label_accesses':0},
        confirmation_manifest=str(T/'fresh_sample_manifest.json'),next_executable_command='confirmation/freeze_protocol.py (all baselines/parser/funding/scorer)')
    print(canonical({'fresh_cohort_frozen':len(records),'remaining_audited_pool':len(available),'domain_counts':dict(Counter(r['domain'] for r in records)),
        'max_qualified_public_UTF8':max(m['qualification_public_UTF8_bytes'] for m in manifest),'Gold_accesses':0}),flush=True)

if __name__=='__main__':main()
