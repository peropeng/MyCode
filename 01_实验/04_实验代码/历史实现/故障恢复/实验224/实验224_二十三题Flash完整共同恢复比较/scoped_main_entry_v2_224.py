"""Unchanged original queue/core; precise censor-next ack and separate identity."""
from common166 import *
import ast
import main_entry_v2_224 as original
from extended_main_entry_v2_224 import entry_source as parent_source
from scoped_main_controller_v2_224 import install,GRANT,wait_peer,exact_next_ack

def entry_source():
    source=parent_source();anchor="'_v2extended.json'"
    assert source.count(anchor)==1
    return source.replace(anchor,"'_v2scoped.json'")

def run(mode):
    authorized=install();scope=dict(original.__dict__)
    scope.update(authorize_main=authorized,GRANT=GRANT,wait_peer=wait_peer,exact_unknown_ack=exact_next_ack)
    exec(compile(ast.parse(entry_source()),str(E/'main_entry_v2_224.py'),'exec'),scope);scope['run'](mode)

if __name__=='__main__':run(sys.argv[1])
