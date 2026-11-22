"""Reuse fixed queue, all bodies/seed/limits, and independent current sources."""
from common166 import *
import ast
import main_entry_v2_224 as original
from ast_safe_main_entry_v2_224 import entry_source as previous_source
from scoped_main_controller_v2_224 import wait_peer
from next_pair_main_controller_v2_224 import install,external_ack,GRANT
def entry_source():
    source=previous_source();anchor="'_v2astsafe.json'";assert source.count(anchor)==1
    source=source.replace(anchor,"'_v2nextpair.json'")
    anchor='    for index, task in enumerate(order):\n';assert source.count(anchor)==1
    return source.replace(anchor,anchor+'        if index < 11: continue  # Prior terminal observations are never regenerated.\n        if index > 12: return\n')
def run(mode):
    authorized=install();scope=dict(original.__dict__)
    scope.update(authorize_main=authorized,GRANT=GRANT,wait_peer=wait_peer,
                 exact_unknown_ack=lambda mode,index,result:external_ack(mode,index,result,read(GRANT)))
    exec(compile(ast.parse(entry_source()),str(E/'main_entry_v2_224.py'),'exec'),scope);scope['run'](mode)
if __name__=='__main__':run(sys.argv[1])
