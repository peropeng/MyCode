from common166 import *
import ast
import main_entry_v2_224 as original
from next_pair_main_entry_v2_224 import entry_source as previous_source
from scoped_main_controller_v2_224 import wait_peer
from serial_5980_main_controller_v2_224 import install,exact_ack,GRANT
def entry_source():
    text=previous_source();assert text.count('if index < 11:')==1 and text.count("'_v2nextpair.json'")==1
    return text.replace('if index < 11:','if index < 12:').replace("'_v2nextpair.json'","'_v2serial5980.json'")
def run(mode):
    authorize=install();scope=dict(original.__dict__)
    scope.update(authorize_main=authorize,GRANT=GRANT,wait_peer=wait_peer,exact_unknown_ack=lambda mode,index,result:exact_ack(mode,index,result,read(GRANT)))
    exec(compile(ast.parse(entry_source()),str(E/'main_entry_v2_224.py'),'exec'),scope);scope['run'](mode)
if __name__=='__main__':run(sys.argv[1])
