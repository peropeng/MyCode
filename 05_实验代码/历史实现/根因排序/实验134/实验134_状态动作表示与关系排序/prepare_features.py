"""One label-free local encoder cache shared by every Exp134 arm."""
import argparse
from collections import Counter
import gc
import hashlib
import importlib.util
import json
import os
import sqlite3
import sys
import time
sys.dont_write_bytecode=True
os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
import numpy as np
import torch
from common import *
sys.path.insert(0,str(E/'sources'))
import model_adapters as adapters

def load_original_events():
    path=ROOT/'工作区/1006-exp133-state-action/实验/实验133_状态动作选择性核验/method.py'
    spec=importlib.util.spec_from_file_location('Exp133_public_events_only',path)
    module=importlib.util.module_from_spec(spec);exec(compile(path.read_text('utf-8'),str(path),'exec'),module.__dict__)
    return module,path

def feature_input(record,structure,events):
    turns=adapters.anonymous_public_turns(record);visible={'turns':turns};n=len(turns)
    h0=np.asarray([structure._h0_vector(visible,i) for i in range(n)],dtype=np.float32)
    neighbors=structure._build_adjacency(visible)
    adjacency=[]
    for relation in adapters.RELATIONS:
        index=np.zeros((n,2),dtype=np.int64);mask=np.zeros((n,2),dtype=np.float32)
        for i,senders in enumerate(neighbors[relation]):
            if len(senders)>2:raise RuntimeError('qualified_relation_degree_exceeded')
            index[i,:len(senders)]=senders;mask[i,:len(senders)]=1
        adjacency.append((torch.from_numpy(index),torch.from_numpy(mask)))
    packet=events.representation(record);partners=torch.zeros(n,2,dtype=torch.long);valid=torch.zeros(n,2)
    for pair in packet['observed_state_action_links']:
        state,action=pair['decision_state'],pair['ensuing_action']
        partners[state,0]=action;valid[state,0]=1
        partners[action,1]=state;valid[action,1]=1
    return {'raw_structure':torch.from_numpy(h0),'adjacency':adjacency,'paired_partner':partners,'paired_valid':valid,
        'observed_state_action_links':packet['observed_state_action_links']}

def build(records,output_name,allow_old_cache=False):
    assets=adapters.default_assets();binding=adapters.verify_asset_binding(assets)
    structure=adapters.load_public_structure_helpers(assets);events,event_path=load_original_events()
    cache_namespace=canonical({'encoder_files':binding['encoder_files'],'revision':adapters.ENCODER_REVISION,
        'pooling':'last_nonpadding_hidden_prefix_fp16_frozen_Qwen','max_length':8192,'public_text':'Exp132 embedding_text; anonymous role IDs'})
    key_for=lambda text,dimension:hashlib.sha256((cache_namespace+'|'+str(dimension)+'|'+text).encode('utf-8')).hexdigest()
    db=sqlite3.connect(E/'features/embedding_cache.sqlite3')
    db.execute('CREATE TABLE IF NOT EXISTS vectors (key TEXT PRIMARY KEY, dimension INTEGER, vector BLOB, token_length INTEGER)')
    db.commit();todo={};specs={};start=time.monotonic()
    for record in records:
        sid=record['sample_id'];turns=adapters.anonymous_public_turns(record)
        content=[adapters.embedding_text(t) for t in turns];roles=[t['role'] for t in turns]
        specs[sid]={'content':[(key_for(t,128),t) for t in content],'agent':[(key_for(t,32),t) for t in roles]}
        for name,dimension in [('content',128),('agent',32)]:
            for key,text in specs[sid][name]:
                if not db.execute('SELECT 1 FROM vectors WHERE key=?',(key,)).fetchone():todo[key]=(text,dimension)
    initial_missing=len(todo);pending=list(todo.items());pending.sort(key=lambda item:(item[1][1],len(item[1][0]),item[0]))
    required_unique=len({key for spec in specs.values() for entries in spec.values() for key,_ in entries})
    cached_before=required_unique-initial_missing
    encoder=None;batch_size=8;encoded=0;ooms=0;last_notice=0
    status('EXP134_LOCAL_EMBEDDING_CACHE',embedding_records_total=len(records),unique_texts_to_encode=initial_missing,
        unique_texts_encoded=0,required_unique_texts=required_unique,cached_unique_texts_at_start=cached_before,
        embedding_cache_namespace_sha256=hashlib.sha256(cache_namespace.encode()).hexdigest(),
        encoder_device='cuda',next_executable_command='prepare_features.py run (cache resumes by exact public text hash)')
    try:
        if pending:encoder=adapters.FrozenQwenEncoder(assets['encoder_directory'],'cuda' if torch.cuda.is_available() else 'cpu')
        position=0
        while position<len(pending):
            dim=pending[position][1][1];batch=pending[position:position+batch_size]
            batch=[item for item in batch if item[1][1]==dim]
            measured=encoder.tokenizer([item[1][0] for item in batch],padding=False,truncation=False)['input_ids']
            longest=min(8192,max(len(tokens) for tokens in measured))
            effective_batch=min(len(batch),max(1,8192//max(1,longest)))
            batch=batch[:effective_batch]
            try:
                vectors,lengths=encoder.encode([item[1][0] for item in batch],dim)
            except torch.cuda.OutOfMemoryError:
                ooms+=1;gc.collect();torch.cuda.empty_cache()
                if batch_size>1:batch_size=max(1,batch_size//2);continue
                encoder.model.to('cpu');encoder.device=torch.device('cpu');batch_size=1
                append(E/'features/engineering_events.jsonl',{'at_utc':now(),'event':'CUDA_OOM_CPU_FALLBACK','at_unique_text':position})
                continue
            for (key,_),vector,length in zip(batch,vectors,lengths):
                db.execute('INSERT OR IGNORE INTO vectors VALUES (?,?,?,?)',(key,dim,vector.numpy().astype('<f4').tobytes(),int(length)))
            db.commit();position+=len(batch);encoded+=len(batch)
            elapsed=time.monotonic()-start
            if elapsed-last_notice>=30 or position==len(pending):
                last_notice=elapsed
                status('EXP134_LOCAL_EMBEDDING_CACHE',embedding_records_total=len(records),unique_texts_to_encode=initial_missing,
                    unique_texts_encoded=encoded,required_unique_texts=required_unique,cached_unique_texts_at_start=cached_before,
                    current_cached_unique_texts=cached_before+encoded,embedding_cache_elapsed_seconds=elapsed,encoder_batch_size=effective_batch,
                    encoder_device=str(encoder.device),encoder_OOM_count=ooms,encoder_texts_per_second=encoded/max(elapsed,1e-6),
                    next_executable_command='prepare_features.py run (resume missing exact text hashes)')
                print(canonical({'encoder_progress':encoded,'unique_texts_total':initial_missing,'elapsed_seconds':round(elapsed,1),
                    'batch_size':effective_batch,'device':str(encoder.device),'OOMs':ooms,'cached_before_run':cached_before}),flush=True)
        def fetch(key,dimension):
            row=db.execute('SELECT dimension,vector,token_length FROM vectors WHERE key=?',(key,)).fetchone()
            if row is None or row[0]!=dimension:raise RuntimeError('embedding_cache_entry_missing_or_wrong_dimension')
            array=np.frombuffer(row[1],dtype='<f4').copy()
            if array.shape!=(dimension,) or not np.isfinite(array).all():raise RuntimeError('embedding_cache_vector_invalid')
            return torch.from_numpy(array),row[2]
        result={};pairs=Counter();truncated=0
        for record in records:
            sid=record['sample_id'];entry=feature_input(record,structure,events)
            for name,dim in [('content',128),('agent',32)]:
                vectors=[fetch(key,dim) for key,_ in specs[sid][name]]
                entry[name]=torch.stack([v for v,_ in vectors])
                if name=='content':entry['content_token_lengths']=[n for _,n in vectors];truncated+=sum(n>8192 for _,n in vectors)
            entry['public_sha256']=adapters.public_hash(record);entry['public_record_sha256']=digest(record)
            entry['sample_id']=sid;pairs[record.get('domain','unknown')]+=len(entry['observed_state_action_links'])
            result[sid]=entry
        payload={'encoder_binding':binding,'embedding_namespace_sha256':hashlib.sha256(cache_namespace.encode()).hexdigest(),
            'records':result,'label_answer_reason_fields_present':False}
        target=E/'features'/output_name
        if target.exists():raise RuntimeError('sealed_feature_file_exists_no_overwrite')
        torch.save(payload,target)
        receipt={'at_utc':now(),'feature_file_sha256':sha(target),'records':len(records),'record_public_hashes':{r['sample_id']:digest(r) for r in records},
            'encoder_binding':binding,'source_bindings':{'model_adapters':sha(E/'sources/model_adapters.py'),'public_event_representation':sha(event_path)},
            'embedding_namespace_sha256':payload['embedding_namespace_sha256'],'new_unique_texts_encoded':encoded,
            'cached_unique_texts_reused':cached_before,'total_required_unique_texts':required_unique,
            'batching':'qualified1-8 public texts; at most8192 padded tokens per batch to avoid WDDM memory paging; embeddings unchanged',
            'encoder_OOM_count':ooms,'final_encoder_batch_size':batch_size,'encoder_device':None if encoder is None else str(encoder.device),
            'elapsed_seconds':time.monotonic()-start,'observed_pair_counts_by_domain':dict(pairs),'truncated_step_texts':truncated,
            'all_relation_channels':list(adapters.RELATIONS),'no_label_or_answer_or_reason_inputs':True,'paid_API_calls':0}
        write_new(target.with_suffix('.receipt.json'),receipt)
        print(canonical({'feature_cache_complete':True,'records':len(records),'new_unique_texts':encoded,'pairs':dict(pairs),'elapsed_seconds':round(receipt['elapsed_seconds'],1)}),flush=True)
        return receipt
    finally:
        db.close()
        if encoder is not None:del encoder;gc.collect();torch.cuda.empty_cache()

def run():
    seal=read(E/'data/public_split_seal.json');mapping=read(E/'data/label_mapping_receipt.json')
    if sha(E/'data/public_records.json')!=seal['public_records_sha256'] or sha(E/'data/selected_train_labels.private.json')!=mapping['private_labels_sha256']:raise RuntimeError('frozen_selected_train_inputs_changed')
    labels=read(E/'data/selected_train_labels.private.json')['labels'];validids={r['sample_id'] for r in labels}
    records=[r for r in read(E/'data/public_records.json')['records'] if r['sample_id'] in validids]
    receipt=build(records,'train_validation_features.pt')
    status('EXP134_LOCAL_FEATURES_SEALED',embedding_records_complete=len(records),embedding_receipt=str(E/'features/train_validation_features.receipt.json'),
        next_executable_command='train.py freeze; train.py run')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=('run',));args=parser.parse_args();run()
