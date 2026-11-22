"""Equivalent pathlib compatibility in generated-test guard on Python 3.8."""
from common166 import *

def install(environment):
 q=environment.run.qualify;original=q.execute;guard=E/'repro_guard225'
 def execute(argv,cwd,log,timeout,env=None):
  if env is None:return original(argv,cwd,log,timeout,env)
  child_env=dict(env)
  if child_env.get('EXP166_REPRO_OUTPUT'):
   paths=child_env['PYTHONPATH'].split(os.pathsep)
   if Path(paths[0]).resolve()!=(OLD/'repro_guard').resolve():raise RuntimeError('ORIGINAL_GENERATED_GUARD_PATH_DRIFT')
   child_env['PYTHONPATH']=os.pathsep.join([str(guard),*paths[1:]])
   environment.record('generated_guard_python38_compat225',{'original_guard_sha256':sha(OLD/'repro_guard/sitecustomize.py'),'compatible_guard_sha256':sha(guard/'sitecustomize.py'),'unchanged_argv':argv,'equivalent_relative_to_predicate_only':True})
  return original(argv,cwd,log,timeout,child_env)
 q.execute=execute
