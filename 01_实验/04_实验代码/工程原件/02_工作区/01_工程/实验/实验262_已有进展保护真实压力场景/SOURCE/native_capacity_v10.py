"""Mechanical native timeout/dependency adapter; no algorithm or selector change."""
from common166 import *
import ast,copy
def _rebind(module,name):
    source=Path(module.__file__);tree=ast.parse(source.read_text('utf-8-sig'))
    node=copy.deepcopy(next(v for v in tree.body if isinstance(v,ast.FunctionDef) and v.name==name))
    changes=0
    class Timeout(ast.NodeTransformer):
        def visit_Call(self,value):
            nonlocal changes
            self.generic_visit(value)
            if isinstance(value.func,ast.Name) and value.func.id=='min' and value.args and isinstance(value.args[0],ast.Constant) and value.args[0].value==120:
                value.args[0]=ast.Name(id='NATIVE_TIMEOUT_SECONDS',ctx=ast.Load());changes+=1
            return value
    node=Timeout().visit(node);ast.fix_missing_locations(node)
    if changes!=1:raise RuntimeError('V10_ORIGINAL_PROBE_TIMEOUT_ANCHOR_UNKNOWN '+str(source))
    module.__dict__['NATIVE_TIMEOUT_SECONDS']=NATIVE_TIMEOUT_SECONDS
    exec(compile(ast.Module(body=[node],type_ignores=[]),str(source)+'::v10_timeout','exec'),module.__dict__)
    return {'source':str(source),'source_SHA256':sha(source),'original_function':name,'timeout_replacements':changes,'exact_selectors_guard_coverage_unchanged':True}
def install(env):
    q=env.run.qualify
    evidence=[_rebind(q,'probe'),_rebind(env.run,'probe')]
    isolated=q.isolated_env
    def common_dependencies(*args,**kwargs):
        child=isolated(*args,**kwargs)
        if env.package=='moto':
            dependencies=ROOT/'工作区/1010-unified-six/shared_runtime_dependencies_moto311/site-packages'
            if not dependencies.is_dir():raise RuntimeError('V10_COMMON_MOTO_DEPENDENCIES_REQUIRED')
            child['PYTHONPATH']=child['PYTHONPATH']+os.pathsep+str(dependencies)
        return child
    q.isolated_env=common_dependencies
    env.record('prospective_common_native_capacity_v10',{'original_probe_AST':evidence,'per_native_timeout_seconds':NATIVE_TIMEOUT_SECONDS,'test_scope_not_expanded':True,'initial_full_pool_not_added_to_ours':True})
    return env
