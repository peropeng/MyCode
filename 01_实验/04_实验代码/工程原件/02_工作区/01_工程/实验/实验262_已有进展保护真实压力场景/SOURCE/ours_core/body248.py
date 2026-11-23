def body(self, role, messages, temperature, seed, max_tokens, reader_index=0, tools=None):
        current = copy.deepcopy(messages)
        # Current C0 may have been captured in Root's separate mechanical tree.
        # Only an exact match to the validated raw C0 object is replaced by its
        # common role-neutral representation. Newer native observations stay intact.
        if hasattr(self,'_Root_C0_unprojected_feedback'):
            for message in current:
                if message.get('role')!='user' or not isinstance(message.get('content'),str):continue
                try:payload=json.loads(message['content'])
                except ValueError:continue
                latest=payload.get('latest_public_feedback') if isinstance(payload,dict) else None
                if (isinstance(latest,dict) and latest.get('current_incumbent_public_feedback')==self._Root_C0_unprojected_feedback):
                    latest['current_incumbent_public_feedback']=copy.deepcopy(self.shared_current_C0_decoded)
                    message['content']=canonical(payload)
        roots = [(self.repo_root, '/workspace/repo'), (self._paths['frozen'], '/public-tests'),
                 (self.active, '/workspace'), (self.out, '/public-feedback')]
        current = projection.project(current, roots)
        if reader_index == 0:
            for m in current:
                if m.get('role') != 'user' or not isinstance(m.get('content'), str):
                    continue
                try:
                    payload = json.loads(m['content'])
                except ValueError:
                    continue
                if not isinstance(payload, dict) or 'ordered_public_edit_evidence' not in payload:
                    continue
                # Canonicalize projected public-record metadata only. The direct
                # C0 root and a reuse root can render different slash encodings;
                # complete native/error/status/source evidence stays untouched.
                def canonical_record_paths(value):
                    if isinstance(value, list):
                        for item in value:
                            canonical_record_paths(item)
                    elif isinstance(value, dict):
                        record = value.get('native_record')
                        path = record.get('path') if isinstance(record, dict) else None
                        if isinstance(path, str) and path.replace('\\', '/').startswith('/public-feedback/'):
                            tail = [part for part in path.replace('\\', '/').split('/') if part][1:]
                            if tail and tail[0] == 'public_native':
                                tail = tail[1:]
                            record['path'] = '/public-feedback/' + '/'.join(tail)
                        for item in value.values():
                            canonical_record_paths(item)
                canonical_record_paths(payload)
                files = self.business_files()
                actual = {p: hashlib.sha256(t.encode()).hexdigest() for p, t in sorted(files.items())}
                payload['actual_current_state'] = {
                    'business_files_sha256': actual, 'business_inventory_sha256': digest(actual),
                    'snapshot_inventory_sha256': self.snapshot('attempt_input_observed')['inventory_sha256'],
                    'public_rejected_attempts_are_historical_only': True}
                if self.closure_enabled or self.context_mode == 'NONEDGE':
                    _, selected = self.source_evidence()
                    public_events = payload.get('latest_public_feedback', {}).get('complete_attempt_feedback', [])
                    compatible = [event for event in public_events
                                  if not event.get('historical_rejected_attempt')
                                  and event.get('observed_business_inventory_sha256') == digest(actual)]
                    latest_current = compatible[-1:] if compatible else []
                    manifest, context = relations240.build(
                        files, selected[:int(payload['attempt'])], max_context_bytes=32768,
                        public_failure=current_feedback248.anchor_input(self,payload,files,latest_current),
                        historical_evidence=selected, initial_files=self._failure_anchor_initial_files)
                    manifest['historical_attempts_excluded_from_current_line_anchors'] = len(public_events)-len(latest_current)
                    save(self.out/'relations'/('attempt_'+str(payload['attempt'])+'.json'), manifest)
                    closure_payload = relations240.additional_context(manifest, context)
                    if self.closure_enabled:
                        payload['additional_business_context'] = closure_payload
                    else:
                        audit, control = relations240.nonedge_context(files, manifest, context)
                        save(self.out/'relations'/('attempt_'+str(payload['attempt'])+'_nonedge_match.json'), audit)
                        payload['additional_business_context'] = control
                    extra = payload['additional_business_context']
                    save(self.out/'relations'/('attempt_'+str(payload['attempt'])+'_payload_cost.json'), {
                        'arm': self.arm, 'additional_payload_bytes': len(canonical(extra).encode()),
                        'source_text_bytes': sum(len(s['text'].encode()) for s in extra['source_context']),
                        'closure_full_payload_bytes': len(canonical(closure_payload).encode()),
                        'all_derived_relationships_audited': manifest['edge_count'],
                        'model_metadata_edges': len(closure_payload['relationships']),
                        'same_neutral_payload_key': 'additional_business_context/source_context',
                        'relationship_metadata_cost_exactly_matched': False})
                # Presentation only: every arm binds the same complete original
                # initial failure to the already injected common exact line pool.
                # Relation retrieval above and node readers retain decoded text.
                payload['initial_public_failure'] = copy.deepcopy(self._encoded_initial_public_failure)
                payload['public_failure_text_pool_binding'] = {
                    'schema':'lossless-public-lines/2',
                    'pool':'unique_exact_lines in the complete common public evidence supplied immediately above',
                    'decode':'For every $public_text_lines, concatenate the indexed pool strings in order.',
                    'decoded_initial_failure_sha256':codec.digest(self.initial_public_feedback),
                    'all_initial_node_count':len(self.initial_public_feedback),
                    'all_nodes_statuses_phases_error_text_exact':True}
                # Relation retrieval uses raw current feedback above; only presentation changes.
                payload = projection.project(payload, roots)
                payload, feedback_codec_audit = feedback_codec242.pack_payload_feedback(payload)
                save(self.out/'feedback_codec'/('attempt_'+str(payload['attempt'])+'_feedback.json'), feedback_codec_audit)
                m['content'] = canonical(payload)
            index = 1 if current and current[0].get('role') == 'system' else 0
            current.insert(index, {'role': 'user', 'content': codec.render(self.pack)})
        # Identical actual provider seed across arms; arm/method are excluded.
        actual_seed = int(hashlib.sha256(canonical({
            'master': 20261008, 'task': self.task_id, 'stage': role,
            'original_fixed_stage_seed': int(seed), 'reader_index': reader_index
        }).encode()).hexdigest()[:8], 16) % 2147483647
        body = {'model': 'deepseek-flash', 'messages': current,
                'thinking': {'type': 'disabled'}, 'temperature': temperature,
                'seed': actual_seed, 'max_tokens': max_tokens, 'stream': False,
                'response_format': {'type': 'json_object'},
                'tools': copy.deepcopy(tools or shared.TOOLS)+copy.deepcopy(masked_boundary242.TOOLS), 'tool_choice': 'auto'}
        return body
