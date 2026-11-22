"""Original fixed21 queue with paired gate and exact prior-UNKNOWN next ack."""
from common166 import *
import inspect, ast
import main_entry_v2_224 as original
from extended_main_controller_v2_224 import install,GRANT,wait_peer,exact_unknown_ack

def entry_source():
    source=inspect.getsource(original.run)
    changes=[("'supervision_' + mode + '_v2main.json'","'supervision_' + mode + '_v2extended.json'"),
             ("        out.mkdir(parents=True, exist_ok=True)","        wait_peer(mode, index, authorize_main)\n        out.mkdir(parents=True, exist_ok=True)"),
             ("            if should_stop_queue(previous): return","            if should_stop_queue(previous) and not exact_unknown_ack(mode, index, previous): return")]
    for old,new in changes:
        assert source.count(old)==1
        source=source.replace(old,new)
    return source

def run(mode):
    authorized=install()
    scope=dict(original.__dict__);scope.update(authorize_main=authorized,GRANT=GRANT,
                                             wait_peer=wait_peer,exact_unknown_ack=exact_unknown_ack)
    exec(compile(ast.parse(entry_source()),str(E/'main_entry_v2_224.py'),'exec'),scope)
    scope['run'](mode)

if __name__=='__main__':run(sys.argv[1])
