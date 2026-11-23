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
    script=Path(os.environ['EXP166_REPRO_SCRIPT']).resolve()
    from scope_guard_v3 import install
    guard_source=Path(os.environ['EXP166_GUARD_SOURCE']).resolve()
    this_guard=Path(__file__).resolve()
    install({'source_root':str(source),'frozen_root':str(frozen),'output':str(out),
             'experiment_root':str(this_guard.parents[1]),
             'trusted_files':[str(this_guard),str(this_guard.parent/'scope_guard_v3.py'),str(guard_source),
                              str(guard_source.parent/'qualification_plugin.py'),str(guard_source.parent/'qualify.py')]})
    # Install our recorder first so covered attempts denied by the original
    # native guard are also observed; original process/network guard still runs.
    runpy.run_path(str(guard_source))
    def finish():
        imports=[]
        for name,module in list(sys.modules.items()):
            value=getattr(module,'__file__',None)
            if value and (name==package or name.startswith(package+'.')):
                p=Path(value).resolve()
                if p.is_relative_to(source):imports.append({'module':name,'source':str(p)})
        (out/'actual_product_imports.json').write_text(json.dumps(imports,indent=2),'utf-8')
    atexit.register(finish)
