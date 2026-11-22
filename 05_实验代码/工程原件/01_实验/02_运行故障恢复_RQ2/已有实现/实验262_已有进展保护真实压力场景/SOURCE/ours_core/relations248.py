"""Auditable static provider/consumer evidence; no causal-edge claim or model."""
import ast
import difflib
import hashlib
import json
import failure_anchors248 as failure_anchors240


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode()).hexdigest()


class Index:
    def __init__(self, files):
        self.files = files
        self.providers, self.consumers, self.parse_failures = [], [], []
        for path, text in sorted(files.items()):
            self.scan(path, text, historical=False)

    def scan(self, path, text, historical=False):
        try:
            tree = ast.parse(text, filename=path)
        except SyntaxError as exc:
            self.parse_failures.append({'path': path, 'line': exc.lineno,
                                        'error': type(exc).__name__, 'historical': historical,
                                        'source_sha256': hashlib.sha256(text.encode()).hexdigest()})
            return
        source_hash = hashlib.sha256(text.encode()).hexdigest()
        index = self

        class Visit(ast.NodeVisitor):
            def __init__(self):
                self.classes, self.functions = [], []

            def record(self, node, symbol, kind):
                owner = '.'.join(self.classes + self.functions)
                return {'path': path, 'line': node.lineno,
                        'end_line': getattr(node, 'end_lineno', node.lineno),
                        'symbol': symbol, 'owner': owner, 'kind': kind,
                        'historical': historical, 'source_sha256': source_hash}

            def visit_ClassDef(self, node):
                symbol = '.'.join(self.classes + [node.name])
                index.providers.append(self.record(node, symbol, 'class_definition'))
                self.classes.append(node.name)
                self.generic_visit(node)
                self.classes.pop()

            def function(self, node):
                symbol = '.'.join(self.classes + [node.name])
                index.providers.append(self.record(node, symbol, 'function_definition'))
                self.functions.append(node.name)
                self.generic_visit(node)
                self.functions.pop()

            visit_FunctionDef = function
            visit_AsyncFunctionDef = function

            def visit_Attribute(self, node):
                if isinstance(node.value, ast.Name) and node.value.id in ('self', 'cls') and self.classes:
                    symbol = '.'.join(self.classes + [node.attr])
                    if isinstance(node.ctx, ast.Store):
                        index.providers.append(self.record(node, symbol, 'attribute_assignment'))
                    elif isinstance(node.ctx, ast.Load):
                        index.consumers.append(self.record(node, symbol, 'attribute_read'))
                self.generic_visit(node)

            def visit_Call(self, node):
                target = node.func
                if isinstance(target, ast.Name):
                    symbol = target.id
                    kind = 'bare_call_possible_reference'
                elif isinstance(target, ast.Attribute):
                    symbol = ('.'.join(self.classes + [target.attr])
                              if isinstance(target.value, ast.Name)
                              and target.value.id in ('self', 'cls') and self.classes
                              else target.attr)
                    kind = 'attribute_call_possible_reference'
                else:
                    return self.generic_visit(node)
                index.consumers.append(self.record(node, symbol, kind))
                self.generic_visit(node)

            def visit_ImportFrom(self, node):
                for value in node.names:
                    if value.name != '*':
                        index.consumers.append(self.record(node, value.name,
                                                          'import_possible_reference'))
                self.generic_visit(node)

        Visit().visit(tree)


def build(files, evidence, max_context_bytes=65536, public_failure=None, historical_evidence=None, initial_files=None):
    """Resolve selected changed symbols and consumers from actual current source.

    Exact self/cls attribute matching is distinguished from possible lexical
    function/import references. Original before-image providers are explicitly
    historical; a removed initializer can still be linked to live attribute reads.
    Whole source spans are selected, never truncated. Omitted spans remain readable
    through the common source reader and are named in the complete edge manifest.
    """
    idx = Index(files)
    changed = {item['path'] for item in evidence}
    historical_hashes = {}
    for item in (historical_evidence or evidence):
        text = item['_before']
        historical_hashes[item['path']] = hashlib.sha256(text.encode()).hexdigest()
        idx.scan(item['path'], text, historical=True)
        # The public after-image is also historical. It may contain the removed
        # provider absent from the current state, and is never labeled current.
        idx.scan(item['path'], item['_after'], historical=True)
    # An edited file is not itself an intervention scope. Anchor only provider
    # spans intersecting the actual original before/after edit, then resolve the
    # same declared symbols in current source. This prevents unrelated classes
    # elsewhere in a large utility file from becoming alleged consumers.
    changed_symbols = set()
    for item in evidence:
        before, after = item['_before'], item['_after']
        ranges = {'before': [], 'after': []}
        for tag, a, b, c, d in difflib.SequenceMatcher(
                None, before.splitlines(), after.splitlines()).get_opcodes():
            if tag != 'equal':
                ranges['before'].append((a+1, max(a+1, b)))
                ranges['after'].append((c+1, max(c+1, d)))
        for label, text in (('before', before), ('after', after)):
            temporary = Index({item['path']: text})
            for provider in temporary.providers:
                if any(provider['line'] <= right and left <= provider['end_line']
                       for left, right in ranges[label]):
                    changed_symbols.add((provider['path'], provider['symbol'], provider['kind']))
    anchors = [p for p in idx.providers
               if (p['path'], p['symbol'], p['kind']) in changed_symbols]
    failure_audit, failure_providers, failure_consumers = failure_anchors240.retrieve(
        idx, files, public_failure or {}, Index(initial_files) if initial_files else None)
    anchors.extend(failure_providers)
    anchors = list({digest(p): p for p in anchors}.values())
    edges = []
    for p in anchors:
        for c in idx.consumers:
            if c['historical']:
                continue
            exact = p['symbol'] == c['symbol']
            possible = p['symbol'].rsplit('.', 1)[-1] == c['symbol'].rsplit('.', 1)[-1]
            if not (exact or possible):
                continue
            # Do not pretend every obj.forward or obj.__call__ in the repository
            # targets a changed class's method. No receiver type inference is
            # available here: qualified methods require an exact class symbol.
            if p['kind'] == 'function_definition' and '.' in p['symbol'] and not exact:
                continue
            if p['kind'] == 'attribute_assignment' and not exact:
                continue
            edges.append({'provider': p, 'consumer': c,
                          'edge_type': 'same_class_attribute_support' if exact and p['kind'] == 'attribute_assignment'
                          else 'static_possible_symbol_reference',
                          'provider_is_historical': p['historical'],
                          'causal_claim': False})
    # A stable manifest does not rank by recovery outcome or expose test source.
    unique = {digest(e): e for e in edges}
    edges = sorted(unique.values(), key=lambda e: (
        e['edge_type'] != 'same_class_attribute_support',
        not any(c['path'] == e['consumer']['path']
                and c['line'] <= e['consumer']['line'] <= c['end_line']
                for c in failure_consumers if c['kind'] == 'public_failure_source_function'),
        e['provider']['path'] != e['consumer']['path'],
        e['provider']['path'], e['provider']['line'],
        e['consumer']['path'], e['consumer']['line']))
    spans, seen, used = [], set(), 0
    # Publicly observed business frames come first, before static neighboring
    # source. This makes the existing failure evidence available at attempt1.
    source_targets = failure_consumers + [edge['consumer'] for edge in edges]
    for c in source_targets:
        enclosing = [p for p in idx.providers if not p['historical']
                     and p['path'] == c['path'] and p['line'] <= c['line'] <= p['end_line']
                     and p['kind'] == 'function_definition']
        p = min(enclosing, key=lambda v: v['end_line'] - v['line']) if enclosing else c
        key = (p['path'], p['line'], p['end_line'])
        if key in seen:
            continue
        seen.add(key)
        lines = files[p['path']].splitlines(keepends=True)
        text = ''.join(lines[p['line']-1:p['end_line']])
        item = {'path': p['path'], 'start_line': p['line'], 'end_line': p['end_line'],
                'source_sha256': p['source_sha256'], 'text': text,
                'complete_source_span': True}
        size = len(json.dumps(item, ensure_ascii=False, separators=(',', ':')).encode())
        if used + size <= max_context_bytes:
            spans.append(item)
            used += size
    manifest = {'schema': 'Exp240-static-provider-consumer-manifest/1',
                'changed_public_paths': sorted(changed),
                'current_files_sha256': {p: hashlib.sha256(t.encode()).hexdigest()
                                         for p, t in sorted(files.items())},
                'historical_before_image_sha256': historical_hashes,
                'public_failure_anchor_audit': failure_audit,
                'edges': edges, 'parse_failures': idx.parse_failures,
                'edge_count': len(edges), 'causal_edges': 0,
                'context_rule': 'Stable order; whole enclosing consumer function span if it fits64KiB; no span clipping',
                'selected_context_bytes': used, 'selected_context_spans': len(spans),
                'all_current_business_source_remains_readable': True}
    public = {'schema': manifest['schema'], 'causal_claim': False,
              'scope': 'Static possible provider-consumer relationships; historical providers may be absent in current source',
              'edge_count': len(edges), 'edges': edges,
              'consumer_source_context': spans,
              'public_failure_anchor_audit': failure_audit,
              'no_relation_fallback': not edges,
              'source_span_selection_is_not_error_clipping': True}
    return manifest, public


def nonedge_context(files, closure_manifest, closure_public):
    """Whole legal functions outside the complete static relation manifest.

    Match the closure's actual source-text byte budget conservatively, without
    truncation, padding or constructing imaginary source. Stable lexical order
    and actual residual difference are recorded before any method outcome.
    """
    target = sum(len(item['text'].encode()) for item in closure_public['consumer_source_context'])
    idx = Index(files)
    changed = set(closure_manifest['changed_public_paths'])
    endpoints = [edge[role] for edge in closure_manifest['edges']
                 for role in ('provider', 'consumer') if not edge[role]['historical']]
    anchored_spans = closure_public['consumer_source_context']
    candidates = []
    for item in idx.providers:
        if item['kind'] != 'function_definition' or item['path'] in changed:
            continue
        if any(e['path'] == item['path'] and item['line'] <= e['line'] <= item['end_line']
               for e in endpoints):
            continue
        if any(s['path'] == item['path'] and item['line'] <= s['end_line']
               and s['start_line'] <= item['end_line'] for s in anchored_spans):
            continue
        candidates.append(item)
    selected, used = [], 0
    for item in sorted(candidates, key=lambda value: (value['path'], value['line'], value['end_line'])):
        lines = files[item['path']].splitlines(keepends=True)
        text = ''.join(lines[item['line']-1:item['end_line']])
        size = len(text.encode())
        if used + size <= target:
            selected.append({'path': item['path'], 'start_line': item['line'],
                             'end_line': item['end_line'], 'source_sha256': item['source_sha256'],
                             'text': text, 'complete_source_span': True})
            used += size
    audit = {'rule': 'Lexical path/start/end; whole legal function spans outside changed paths and every relation endpoint',
             'closure_source_text_bytes': target, 'nonedge_source_text_bytes': used,
             'byte_shortfall': target-used, 'nonedge_not_over_target': used <= target,
             'eligible_functions': len(candidates), 'selected_functions': len(selected),
             'padding_or_clipping': False, 'dynamic_noninterference_claim': False}
    return audit, {'source_context': selected}


def additional_context(manifest, public, total_budget=65536):
    """Bound only newly-derived metadata; retain the full audit manifest.

    Original public errors/history are untouched. A complete span is already
    selected or omitted as a unit. Relation rows for selected spans enter in the
    manifest's fixed order until the complete derived payload reaches64KiB.
    """
    audit=public['public_failure_anchor_audit']
    # Full frame paths and every ambiguous static match remain in the manifest.
    # The model receives compact references and whole source, not three copies
    # of the same current/historical traceback metadata.
    selected=public['consumer_source_context']
    covers=lambda path,line:any(span['path']==path and span['start_line']<=line<=span['end_line'] for span in selected)
    frame_rows={ (row['actual_business_path'],row['enclosing_function']):
                 {'path':row['actual_business_path'],'symbol':row['enclosing_function'],
                  'observed_line':row['reported_line'],'current_source_SHA256':row['current_source_sha256']}
                 for row in audit['current_public_business_frames'] if covers(row['actual_business_path'],row['reported_line']) }
    api_rows={ (row['method_name'],row['current_business_function']['path'],row['current_business_function']['symbol']):
                 {'method_name':row['method_name'],'current_path':row['current_business_function']['path'],
                  'current_symbol':row['current_business_function']['symbol'],
                  'same_name_match_count':row['same_method_name_match_count'],'causal_claim':False}
                 for row in audit['public_Goal_method_business_matches'] if covers(row['current_business_function']['path'],row['current_business_function']['line']) }
    summary={'schema':audit['schema'],'current_feedback_binding':audit['current_feedback_binding'],
             'current_business_frame_count':len(audit['current_public_business_frames']),
             'current_business_function_anchors':list(frame_rows.values()),
             'historical_initial_business_frame_count':len(audit['historical_initial_public_business_frames']),
             'masked_Goal_full_method_match_count':len(audit['public_Goal_method_business_matches']),
             'masked_Goal_selected_whole_span_method_matches':list(api_rows.values()),
             'omitted_or_ambiguous_matches_complete_in_manifest':True,
             'fallback_to_ranked_only':audit['fallback_to_ranked_only'],
             'complete_manifest_retained_for_audit':True,'causal_claim':False}
    total_budget-=2048  # Reserve the final current-source binding instructions.
    value = {'source_context': public['consumer_source_context'], 'relationships': [],
             'public_failure_anchors': summary,
             'causal_claim': False,
             'relationship_selection': {'full_manifest_edges': manifest['edge_count'],
                                        'selected_metadata_edges': 0,
                                        'complete_manifest_retained_for_audit': True}}
    encode_size = lambda x: len(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
    if encode_size(value) > total_budget:
        raise RuntimeError('EXP240_DERIVED_WHOLE_SPAN_CONTEXT_EXCEEDS_BOUND_NO_CLIPPING')
    for edge in manifest['edges']:
        consumer = edge['consumer']
        if not any(span['path'] == consumer['path'] and span['start_line'] <= consumer['line'] <= span['end_line']
                   for span in value['source_context']):
            continue
        row = {'provider': {key: edge['provider'][key] for key in ('path','line','end_line','symbol','kind','historical','source_sha256')},
               'consumer': {key: consumer[key] for key in ('path','line','end_line','symbol','kind','source_sha256')},
               'edge_type': edge['edge_type'], 'causal_claim': False}
        value['relationships'].append(row)
        value['relationship_selection']['selected_metadata_edges'] = len(value['relationships'])
        if encode_size(value) > total_budget:
            value['relationships'].pop()
            value['relationship_selection']['selected_metadata_edges'] = len(value['relationships'])
            break
    return value
