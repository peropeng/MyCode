"""Original queue and results; separate worker identity record only."""
from common166 import *
import inspect, ast
import main_entry_v2_224 as original
from independent_main_controller_v2_224 import install, GRANT

def entry_source():
    source=inspect.getsource(original.run)
    anchor="'supervision_' + mode + '_v2main.json'"
    assert source.count(anchor)==1
    return source.replace(anchor,"'supervision_' + mode + '_v2independent.json'")

def run(mode):
    authorized=install()
    scope=dict(original.__dict__); scope.update(authorize_main=authorized,GRANT=GRANT)
    exec(compile(ast.parse(entry_source()),str(E/'main_entry_v2_224.py'),'exec'),scope)
    scope['run'](mode)

if __name__=='__main__': run(sys.argv[1])
