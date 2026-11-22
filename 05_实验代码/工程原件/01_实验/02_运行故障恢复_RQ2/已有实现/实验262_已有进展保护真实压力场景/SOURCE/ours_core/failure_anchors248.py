"""Current complete public capture plus masked Goal calls, static and audited."""
import copy
import failure_anchors240 as original

def retrieve(index,files,public_failure,initial_index=None):
    current={key:public_failure[key] for key in ('current_incumbent_public_feedback','current_native_public_captured_output') if key in public_failure}
    audit,providers,consumers=original.retrieve(index,files,current,index)
    # The deepest current traceback frame is the immediate fault site. Keep
    # complete functions from that end first, then caller spans within the bound.
    consumers=list(reversed(consumers))
    for row in consumers:row['anchor_origin']='current_complete_public_native_capture'
    current_frames=copy.deepcopy(audit['public_business_frames'])
    historical={key:public_failure[key] for key in ('initial_public_failure','initial_original_public_captured_output_historical') if key in public_failure}
    old_audit,old_providers,old_consumers=original.retrieve(index,files,historical,initial_index)
    api_matches=[]
    for call in public_failure.get('public_goal_masked_test_calls',[]):
        name=call['method_name']
        matches=[row for row in index.providers if not row['historical'] and row['kind']=='function_definition' and row['symbol'].rsplit('.',1)[-1]==name]
        for row in matches:
            api_matches.append({**copy.deepcopy(call),'current_business_function':copy.deepcopy(row),
                'same_method_name_match_count':len(matches),'receiver_type_resolution':False,'causal_claim':False})
            providers.append(copy.deepcopy(row))
            consumers.append({**copy.deepcopy(row),'kind':'public_failure_source_function','anchor_origin':'declared_public_Goal_masked_AST_call_name','static_possible_reference':True})
    # Initial failure is explicitly historical. Its source is rebound by the
    # unchanged initial AST and function symbol, after current capture anchors.
    providers.extend(old_providers)
    for row in old_consumers:row['anchor_origin']='historical_initial_public_capture_rebound_to_current_function'
    consumers.extend(old_consumers)
    unique=lambda rows:list({(row['path'],row['line'],row['end_line'],row['symbol'],row['kind'],row['historical']):row for row in rows}.values())
    audit.update(schema='current-capture-and-masked-Goal-static-anchors/1',
        current_public_business_frames=current_frames,
        historical_initial_public_business_frames=old_audit['public_business_frames'],
        current_feedback_binding=copy.deepcopy(public_failure.get('current_binding')),
        public_Goal_masked_test_AST_audit=copy.deepcopy(public_failure.get('public_goal_masked_test_AST_audit',[])),
        public_Goal_method_business_matches=api_matches,
        fallback_to_ranked_only=not current_frames and not api_matches and not audit['public_missing_attributes'],
        original_full_public_capture_used=True,whole_current_functions_not_synthetic=True)
    return audit,unique(providers),unique(consumers)
