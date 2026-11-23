"""Public split freeze, followed by only selected official-train label mapping."""
import argparse
from collections import Counter,defaultdict
import hashlib
from pathlib import PurePosixPath
import re
import unicodedata
import zipfile
from common import *

SALT='Exp134|author-train-public-group|20261006-v1'

def norm(s):return re.sub(r'\s+',' ',unicodedata.normalize('NFC',s).strip()).casefold()
def integer(value):
    if type(value) is int:return value
    if isinstance(value,str) and re.fullmatch(r'\s*\d+\s*',value):return int(value)
    raise ValueError('not_one_exact_integer_source_step_ID')

def freeze():
    status('EXP134_PUBLIC_SPLIT_FREEZE',next_executable_command='prepare_data.py labels',train_labels_accessed=0)
    source_hash=sha(SOURCE_ZIP)
    if source_hash!='a4615b2defacc5ec181239da299055e240444b44b414bd7db3d1471c9aa5826d':raise RuntimeError('source_release_changed')
    parent={};identity={};splits={};records={};reasons=Counter();counts=Counter()
    def root(x):
        parent.setdefault(x,x)
        while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
        return x
    def union(a,b):
        a,b=root(a),root(b)
        if a!=b:parent[max(a,b)]=min(a,b)
    with zipfile.ZipFile(SOURCE_ZIP) as archive:
        for member in sorted(archive.namelist()):
            if not member.endswith('.jsonl'):continue
            domain,split=PurePosixPath(member).parts[-2:];split=split.removesuffix('.jsonl')
            allowed={'question','question_ID'}|({'history'} if split=='train' and domain in ('coding','math') else set())
            with archive.open(member) as source:
                for index,line in enumerate(source):
                    if not line.strip():continue
                    row=public_object(line,allowed);rid=f'{domain}/{split}/{index}';counts[domain+'/'+split]+=1
                    keys=['question:'+hashlib.sha256(norm(row['question']).encode()).hexdigest(),
                          'source-question:'+domain+':'+str(row['question_ID'])]
                    union(*keys);identity[rid]=keys;splits[rid]=split
                    if split!='train' or domain not in ('coding','math'):continue
                    try:
                        history=row['history']
                        if not isinstance(history,list) or not 6<=len(history)<=32:raise ValueError('public_length_outside_6_32')
                        turns=[];coordinates=[];ids=[]
                        for ordinal,event in enumerate(history):
                            original=integer(event.get('step'));ids.append(original)
                            actor=event.get('name') or event.get('role')
                            if not isinstance(actor,str) or not actor.strip() or not isinstance(event.get('content',''),str):raise ValueError('invalid_public_actor_or_content')
                            turns.append({'role':actor,'content':event.get('content',''),'action':'','thought':''})
                            coordinates.append({'ordinal_zero_based':ordinal,'original_step_id':original,
                                'source_channel_role':event.get('role'),'source_actor_name':event.get('name')})
                        if len(set(ids))!=len(ids):raise ValueError('nonunique_public_source_step_IDs')
                        sid=f'AgenTracer:data-v1.0.0:{domain}:train:{row["question_ID"]}:{index:06d}'
                        record={'sample_id':sid,'record_id':rid,'domain':domain,'source_split':'train','source_member':member,
                            'source_row':index,'question_ID':row['question_ID'],'task':row['question'],'turns':turns,'coordinate_map':coordinates}
                        size=len(canonical(record).encode('utf-8'))
                        if size>100000:raise ValueError('public_UTF8_above_100000')
                        record['public_UTF8_bytes']=size;records[rid]=record
                    except (ValueError,TypeError,KeyError) as exc:reasons[domain+':'+str(exc)]+=1
    components=defaultdict(set)
    for keys in identity.values():
        for key in keys:components[root(key)].add(key)
    gids={r:digest(sorted(keys)) for r,keys in components.items()}
    groups_for={rid:gids[root(keys[0])] for rid,keys in identity.items()}
    group_splits=defaultdict(set)
    for rid,split in splits.items():group_splits[groups_for[rid]].add(split)
    pool=defaultdict(list)
    for rid,record in records.items():
        group=groups_for[rid]
        if 'test' in group_splits[group]:reasons[record['domain']+':component_crosses_author_test']+=1;continue
        record['task_group']=group;pool[group].append(record)
    representatives={group:min(rs,key=lambda r:r['record_id']) for group,rs in pool.items()}
    priority=lambda group:(hashlib.sha256((SALT+'|'+group).encode()).hexdigest(),group)
    selected=[];available={};sizes={}
    for domain in ('coding','math'):
        groups=sorted((g for g,r in representatives.items() if r['domain']==domain),key=priority)
        available[domain]=len(groups);chosen=groups[:320]
        if len(chosen)<2:raise RuntimeError('insufficient_public_train_groups:'+domain+':'+str(len(chosen)))
        nval=64 if len(chosen)==320 else max(1,len(chosen)//5);ntrain=len(chosen)-nval
        sizes[domain]={'train':ntrain,'validation':nval,'available':len(groups)}
        for i,group in enumerate(chosen):
            record=representatives[group];record['optimization_split']='train' if i<ntrain else 'validation'
            selected.append(record)
    manifest=[{k:r[k] for k in ('sample_id','record_id','task_group','domain','source_member','source_row','optimization_split','public_UTF8_bytes')}
              |{'public_record_sha256':digest(r),'group_priority':priority(r['task_group'])[0],'raw_steps':len(r['turns'])} for r in selected]
    write_new(E/'data/public_records.json',{'records':selected,'labels_answers_reasons_present':False})
    write_new(E/'data/public_split_manifest.json',{'at_utc':now(),'records':manifest,'salt':SALT,'source_zip_sha256':source_hash,
        'full_release_public_counts':dict(counts),'eligible_group_counts':available,'selected_counts':sizes,'public_exclusions':dict(reasons),
        'group_rule':'full-release connected components of normalized question and domain+question_ID',
        'within_group_rule':'lexicographically smallest record_id among publicly eligible coding/math author-train rows',
        'cross_domain_group_ownership':'domain of canonical representative; each connected group selected once',
        'all_author_test_crossing_components_excluded':True,'train_label_values_parsed':0,'test_label_values_parsed':0,
        'public_records_sha256':sha(E/'data/public_records.json'),'plan_sha256':sha(E/'approved_plan.json')})
    write_new(E/'data/public_split_seal.json',{'at_utc':now(),'manifest_sha256':sha(E/'data/public_split_manifest.json'),
        'public_records_sha256':sha(E/'data/public_records.json'),'source_zip_sha256':source_hash,
        'before_any_selected_training_label_values_or_model_training':True})
    status('EXP134_PUBLIC_SPLIT_FROZEN',train_groups=sum(s['train'] for s in sizes.values()),validation_groups=sum(s['validation'] for s in sizes.values()),
        selected_counts=sizes,train_labels_accessed=0,next_executable_command='prepare_data.py labels')
    print(canonical({'public_split_frozen':True,'selected_counts':sizes,'train_label_values_parsed':0,'test_label_values_parsed':0}),flush=True)

def labels():
    seal=read(E/'data/public_split_seal.json');manifest=read(E/'data/public_split_manifest.json')
    if sha(E/'data/public_split_manifest.json')!=seal['manifest_sha256'] or sha(E/'data/public_records.json')!=seal['public_records_sha256'] or sha(SOURCE_ZIP)!=seal['source_zip_sha256']:raise RuntimeError('public_split_seal_changed')
    records=read(E/'data/public_records.json')['records'];selected={(r['source_member'],r['source_row']):r for r in records}
    labels=[];excluded=[]
    with zipfile.ZipFile(SOURCE_ZIP) as archive:
        for member in sorted({key[0] for key in selected}):
            if not member.endswith('/train.jsonl'):raise RuntimeError('train_labels_only')
            with archive.open(member) as source:
                for index,line in enumerate(source):
                    record=selected.get((member,index))
                    if record is None:continue
                    try:
                        annotation=public_object(line,{'mistake_step'});original=integer(annotation['mistake_step'])
                        positions=[i for i,c in enumerate(record['coordinate_map']) if c['original_step_id']==original]
                        if len(positions)!=1:raise ValueError('annotation_not_unique_original_source_step_ID')
                        labels.append({'sample_id':record['sample_id'],'record_id':record['record_id'],'task_group':record['task_group'],
                            'optimization_split':record['optimization_split'],'original_source_step_ID':original,'target_ordinal':positions[0]})
                    except (ValueError,KeyError,TypeError) as exc:excluded.append({'sample_id':record['sample_id'],'record_id':record['record_id'],'reason':str(exc)})
    if len(labels)+len(excluded)!=len(records):raise RuntimeError('selected_train_label_record_missing')
    write_new(E/'data/selected_train_labels.private.json',{'labels':labels,'label_scope':'selected author-train rows only; ordinal mapping unchanged'})
    write_new(E/'data/label_mapping_receipt.json',{'at_utc':now(),'selected_labels_parsed':len(records),'valid_labels':len(labels),'excluded':excluded,
        'manifest_sha256':seal['manifest_sha256'],'private_labels_sha256':sha(E/'data/selected_train_labels.private.json'),
        'test_labels_parsed':0,'answer_reason_error_source_values_parsed':0,'no_replacement_sampling_after_label_exclusions':True})
    validids={r['sample_id'] for r in labels};counts=Counter(r['optimization_split'] for r in records if r['sample_id'] in validids)
    status('EXP134_SELECTED_TRAIN_LABELS_MAPPED',train_groups=counts['train'],validation_groups=counts['validation'],
        train_labels_accessed=len(records),malformed_train_labels=len(excluded),next_executable_command='prepare_features.py run')
    print(canonical({'selected_train_labels_mapped':len(labels),'malformed_excluded':len(excluded),'counts':dict(counts),'test_labels_parsed':0}),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=('freeze','labels'));args=parser.parse_args()
    freeze() if args.mode=='freeze' else labels()
