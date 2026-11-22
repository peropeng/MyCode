"""Future product entry: actual self identity precedes product/pytest imports."""
import json, os, sys
from pathlib import Path

def main():
    envelope=json.loads(Path(sys.argv[1]).read_text('utf-8-sig'))
    from winjob241 import self_identity
    identity=self_identity(os.environ['PATCHPILOT_JOB'],envelope['expected_physical_python'])
    Path(envelope['identity_path']).write_text(json.dumps(identity,indent=2),'utf-8')
    import runpy
    # Original public guard is retained, installed before candidate imports.
    runpy.run_path(envelope['harness_guard'])
    source=Path(envelope['source_root']).resolve();frozen=Path(envelope['frozen_root']).resolve();out=Path(envelope['output']).resolve()
    mode=envelope['mode'];args=envelope['argv_tail']
    if mode in ('generated','generated_pytest','coverage','flake8'):
        # Same source/frozen isolation as existing generated-test overlay;
        # this guard also covers Python3.8 via relative_to.
        allowed=[Path(sys.prefix).resolve(),Path(sys.base_prefix).resolve(),out,source,Path(envelope['harness']).resolve(),Path(__file__).resolve().parent]
        allowed += [Path(p).resolve() for p in envelope.get('dependency_paths',[])]
        for item in sys.path:
            if item and ('site-packages' in item or 'python' in item.lower()):allowed.append(Path(item).resolve())
        def within(path,root):
            try:path.relative_to(root);return True
            except ValueError:return False
        def audit(event,values):
            if event in ('subprocess.Popen','os.system','socket.connect','socket.bind'):
                raise PermissionError('PATCHPILOT_GENERATED_PROCESS_OR_NETWORK_BOUNDARY')
            if event=='open' and isinstance(values[0],(str,bytes,os.PathLike)):
                if os.fsdecode(values[0]).casefold()==os.devnull.casefold():return
                p=Path(os.fsdecode(values[0])).resolve();flags=values[2] or 0;m=values[1] or ''
                write=any(x in m for x in ('w','a','x','+')) or bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
                if within(p,frozen) or (within(p,source) and (write or set(p.relative_to(source).parts)&{'test','tests','test-data','.git'})):
                    raise PermissionError('PATCHPILOT_GENERATED_SOURCE_OR_PRIVATE_TEST_BOUNDARY')
                if write and not within(p,out):raise PermissionError('PATCHPILOT_GENERATED_WRITE_SCOPE')
                if not write and not any(within(p,r) for r in allowed):raise PermissionError('PATCHPILOT_GENERATED_READ_SCOPE')
            if event in ('os.remove','os.rmdir','os.mkdir','os.rename'):
                for v in values[:2]:
                    if isinstance(v,(str,bytes,os.PathLike)) and not within(Path(os.fsdecode(v)).resolve(),out):
                        raise PermissionError('PATCHPILOT_GENERATED_MUTATION_SCOPE')
        sys.addaudithook(audit)
    # Trustworthy harness/product paths are added only after identity+guards.
    sys.path.insert(0,envelope['harness']);sys.path.insert(0,str(source))
    for path in reversed(envelope.get('dependency_paths',[])):sys.path.insert(0,path)
    def dependency_certificate(roots):
        import hashlib
        expected=envelope.get('dependency_files_sha256',{});result={}
        for name,mod in sys.modules.copy().items():
            path=getattr(mod,'__file__',None)
            if name.split('.',1)[0] not in roots or not path:continue
            path=Path(path).resolve();raw=hashlib.sha256(path.read_bytes()).hexdigest()
            if str(path) not in expected or expected[str(path)]!=raw:
                raise PermissionError('PATCHPILOT_GENERATED_UNSEALED_PRODUCT_DEPENDENCY '+name)
            result[name]={'path':str(path),'sha256':raw,'version':str(getattr(mod,'__version__','module_no_version'))}
        (out/'actual_dependency_identity.json').write_text(json.dumps({'python_version':sys.version,
            'sys_executable':sys.executable,'sys_prefix':sys.prefix,'sys_base_prefix':sys.base_prefix,
            'sys_path':list(sys.path),'actual_modules':result,'mode':mode},indent=2),'utf-8')
    if mode=='pytest':
        sys.path.append(str(frozen));sys.argv=['pytest',*(args[2:] if args[:2]==['-m','pytest'] else args)]
        raise SystemExit(runpy.run_module('pytest',run_name='__main__'))
    if mode=='py_compile':
        import py_compile
        py_compile.compile(args[-1],cfile=str(out/'checked.pyc'),doraise=True);return
    if mode=='flake8':
        import flake8,pyflakes,pycodestyle,mccabe
        dependency_certificate({'flake8','pyflakes','pycodestyle','mccabe'})
        sys.argv=['flake8',*(args[2:] if args[:2]==['-m','flake8'] else args)]
        raise SystemExit(runpy.run_module('flake8',run_name='__main__'))
    script=args[-1];sys.argv=[script]
    if mode=='generated_pytest':
        import pytest
        raise SystemExit(pytest.main([script,'-q','-p','no:cacheprovider']))
    if mode=='coverage':
        # Execute exactly this generated PoC with the actual product runtime.
        # Always save real measurements, including for a nonzero PoC exit.
        import coverage,io,hashlib
        dependency_certificate({'coverage'})
        roots={'conan','conans'} if envelope['package']=='conans' else {envelope['package']}
        morfs=[]
        for p in source.rglob('*.py'):
            rel=p.relative_to(source)
            if rel.parts[0] in roots and not set(rel.parts)&{'test','tests','test-data','__pycache__','.git'}:
                morfs.append(str(p))
        cov=coverage.Coverage(data_file=str(out/'coverage.sqlite'),config_file=False,source=[str(source/r) for r in roots])
        cov.start()
        try:
            runpy.run_path(script,run_name='__main__')
        finally:
            cov.stop();cov.save();report=io.StringIO()
            cov.report(morfs=morfs,file=report,show_missing=True,ignore_errors=True)
            (out/'coverage_report.txt').write_text(report.getvalue(),'utf-8')
            measured=[];measured_lines={}
            roots={'conan','conans'} if envelope['package']=='conans' else {envelope['package']}
            for file in cov.get_data().measured_files():
                path=Path(file).resolve()
                try:rel=path.relative_to(source).as_posix()
                except ValueError:continue
                parts=Path(rel).parts
                if parts[0] in roots and not set(parts)&{'test','tests','__pycache__','.git'} and cov.get_data().lines(file):
                    measured.append(rel);measured_lines[rel]=sorted(cov.get_data().lines(file))
            business={}
            roots={'conan','conans'} if envelope['package']=='conans' else {envelope['package']}
            for p in source.rglob('*.py'):
                rel=p.relative_to(source)
                if rel.parts[0] in roots and not set(rel.parts)&{'test','tests','__pycache__','.git'}:
                    business[rel.as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
            raw=json.dumps(business,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
            (out/'coverage_receipt.json').write_text(json.dumps({'measured_business_files':sorted(measured),
                'source_business_sha256':hashlib.sha256(raw).hexdigest(),'actual_raw_measurements':True,'measured_business_lines':measured_lines,
                'data_path':str(out/'coverage.sqlite'),'report_path':str(out/'coverage_report.txt')},indent=2),'utf-8')
        return
    # Same actual product import receipt used by strict224's generated guard.
    # Trusted entry writes it after execution; model output is not a receipt.
    try:
        runpy.run_path(script,run_name='__main__')
    finally:
        imports=[]
        for name,mod in tuple(sys.modules.items()):
            filename=getattr(mod,'__file__',None)
            if filename:
                p=Path(filename).resolve()
                try:p.relative_to(source)
                except ValueError:continue
                imports.append({'module':name,'source':str(p)})
        (out/'actual_product_imports.json').write_text(json.dumps(imports,indent=2),'utf-8')

if __name__=='__main__':main()
