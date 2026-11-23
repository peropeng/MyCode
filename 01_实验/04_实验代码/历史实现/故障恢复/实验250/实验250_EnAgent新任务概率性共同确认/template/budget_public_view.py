"""Read-only common masked public view. Never frozen/private source."""
from common166 import *
def read_public_view(task,args):
 p=read(E/'protocol225.json');ref=p['public_test_scope_contract']
 if sha(ref['path'])!=ref['sha256']:raise RuntimeError('PUBLIC_VIEW_SCOPE_DRIFT')
 row=next(x for x in read(ref['path'])['tasks'] if x['task_id']==task)
 allowed=dict(row['public_test_py_files_SHA256']);allowed.update(row.get('public_support_files_SHA256',{}))
 root=Path(row['public_source_repo_view']).resolve()
 rel=args.get('path')
 if rel is None:return {'paths':sorted(allowed),'complete':True,'masked_public_only':True}
 rel=rel.removeprefix('/workspace/repo/').removeprefix('repo/')
 if rel not in allowed or '\\' in rel or ':' in rel or '..' in Path(rel).parts:raise ValueError('ONLY_HASH_BOUND_PUBLIC_VIEW_FILE')
 target=(root/rel).resolve()
 if not target.is_relative_to(root) or target.is_symlink() or sha(target)!=allowed[rel]:raise ValueError('MASKED_PUBLIC_VIEW_DRIFT')
 value=target.read_text('utf-8');rows=value.splitlines(keepends=True);start=args.get('start_line',1);end=args.get('end_line',len(rows))
 if type(start)!=int or type(end)!=int or not 1<=start<=end<=len(rows):raise ValueError('INVALID_EXPLICIT_RANGE')
 return {'path':rel,'start_line':start,'end_line':end,'total_lines':len(rows),'complete_requested_text':''.join(rows[start-1:end]),'whole_source_sha256':allowed[rel],'masked_public_only':True,'no_silent_clipping':True}
read_public_view.tool={'type':'function','function':{'name':'read_public_test_view','description':'List hash-bound masked public test/support paths or read exact requested source lines. No hidden/frozen tests.','parameters':{'type':'object','properties':{'path':{'type':'string'},'start_line':{'type':'integer'},'end_line':{'type':'integer'}},'additionalProperties':False}}}
