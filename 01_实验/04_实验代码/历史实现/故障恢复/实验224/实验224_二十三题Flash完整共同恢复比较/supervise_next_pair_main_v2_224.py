"""Separate supervisor using the unchanged reviewed suspended Job wrapper."""
from common166 import *
from supervise_main_v2_224 import reviewed_wrapper_text as original_text
from next_pair_main_controller_v2_224 import build_authorizer
def main():
    build_authorizer()();assert sys.argv[1] in ('main-agentless','main-ours')
    path,text=original_text()
    for old,new in [("'_v2main.json'","'_v2nextpair.json'"),("'_v2main.log'","'_v2nextpair.log'"),
                    ("str(E/'main_entry_v2_224.py')","str(E/'next_pair_main_entry_v2_224.py')")]:
        assert text.count(old)==1;text=text.replace(old,new)
    scope={'__name__':'fixed_nextpair_supervisor','__file__':str(path)}
    exec(compile(text,str(path),'exec'),scope);scope['run']()
if __name__=='__main__':main()
