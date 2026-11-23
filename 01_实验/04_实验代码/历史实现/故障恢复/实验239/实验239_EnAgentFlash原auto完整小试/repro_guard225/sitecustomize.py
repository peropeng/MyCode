from pathlib import Path
if not hasattr(Path, 'is_relative_to'):
    def _is_relative_to(self, *other):
        try:
            self.relative_to(*other)
            return True
        except ValueError:
            return False
    Path.is_relative_to = _is_relative_to
"""Generated-test overlay: same native guard, private tests unreadable, product immutable."""
import atexit, json, os, runpy, sys
from pathlib import Path
if 'EXP166_REPRO_OUTPUT' in os.environ:
    out=Path(os.environ['EXP166_REPRO_OUTPUT']).resolve()
    source=Path(os.environ['EXP129_SOURCE_ROOT']).resolve()
    frozen=Path(os.environ['EXP129_FROZEN_ROOT']).resolve()
    package=os.environ['EXP129_PACKAGE']
    runpy.run_path(os.environ['EXP166_GUARD_SOURCE'])
    script=Path(os.environ['EXP166_REPRO_SCRIPT']).resolve()
    allowed=[Path(sys.prefix).resolve(),Path(sys.base_prefix).resolve(),out,source,Path(os.environ['EXP166_GUARD_SOURCE']).parent.resolve()]
    for value in list(sys.path):
        if value and ('site-packages' in value or 'python' in value.lower()) and not Path(value).resolve().is_relative_to(frozen):
            allowed.append(Path(value).resolve())
    def deny(event,path):
        with (out/'reproduction_denials.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps({'event':event,'path':str(path)})+'\n')
        raise PermissionError('EXP166 generated test boundary denied '+event)
    def audit(event,args):
        if event=='open' and isinstance(args[0],(str,bytes,os.PathLike)):
            if os.fsdecode(args[0]).casefold()==os.devnull.casefold():return
            p=Path(os.fsdecode(args[0])).resolve();mode=args[1] or '';flags=args[2] or 0
            write=any(v in mode for v in ('w','a','x','+')) or bool(flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
            if p.is_relative_to(frozen):deny(event,p)
            if p.is_relative_to(source):
                if write or any(v in p.relative_to(source).parts for v in ('tests','test','test-data','.git')):deny(event,p)
            elif write and not p.is_relative_to(out):deny(event,p)
            elif not any(p.is_relative_to(root) for root in allowed):deny(event,p)
        if event in ('os.remove','os.rmdir','os.mkdir','os.rename'):
            for value in args[:2]:
                if isinstance(value,(str,bytes,os.PathLike)):
                    p=Path(os.fsdecode(value)).resolve()
                    if not p.is_relative_to(out):deny(event,p)
    sys.addaudithook(audit)
    def finish():
        imports=[]
        for name,module in list(sys.modules.items()):
            value=getattr(module,'__file__',None)
            if value and (name==package or name.startswith(package+'.')):
                p=Path(value).resolve()
                if p.is_relative_to(source):imports.append({'module':name,'source':str(p)})
        (out/'actual_product_imports.json').write_text(json.dumps(imports,indent=2),'utf-8')
    atexit.register(finish)
