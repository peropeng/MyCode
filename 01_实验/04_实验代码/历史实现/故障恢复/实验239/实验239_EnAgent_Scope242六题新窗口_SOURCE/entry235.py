"""Original complete controller, with deployment-only repairs and fresh outputs."""
from common166 import *
import control235
import worker_v2_225 as worker
import backend225
import git_longpaths_adapter225
from relative_traceback_projection228 import Bridge as TraceBridge
class Bridge235(TraceBridge):
 def __init__(self,env):
  super().__init__(env)
  token='%02d'%read(E/'protocol225.json')['task_order'].index(env.task_id)
  self.owned=E/(control235.MECHANICAL_NAMESPACE+'/r' if control235.MECHANICAL else 'r')/token
  self.owned.mkdir(parents=True,exist_ok=True)
def install():
 os.environ.update(GIT_CONFIG_COUNT='1',GIT_CONFIG_KEY_0='core.longpaths',GIT_CONFIG_VALUE_0='true')
 worker.Bridge=Bridge235;worker.verify_v2=control235.verify;worker.load_pack=control235.load_pack
 backend225.authorization=control235.authorization
 original=worker.module
 def load(name,path):
  value=original(name,path)
  if name=='exp225_frozen_enagent':git_longpaths_adapter225.install(value)
  return value
 worker.module=load
 OriginalEnvironment=worker.CommonEnvironment
 class TypedNativeEnvironment(OriginalEnvironment):
  def __init__(self,ref,method):
   super().__init__(ref,method)
   from native_executor224 import install as install_native
   install_native(self)
 worker.CommonEnvironment=TypedNativeEnvironment
 # Existing original environment and native helper imports use this alias.
 __import__('common166').TIME_AUTHORITY=E/'protocol225.json'
def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--task',required=True);a=p.parse_args()
 install();control235.verify(a.task,control235.PHASE)
 return worker.run(a.task,control235.PHASE)
if __name__=='__main__':main()
