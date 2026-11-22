"""Separate supervisor records; unchanged root-reviewed Job/deadline shape."""
from common166 import *
from supervise_main_v2_224 import reviewed_wrapper_text as parent_text
from independent_main_controller_v2_224 import build_authorizer

def reviewed_wrapper_text():
    path,text=parent_text()
    for old,new in [("'_v2main.json'","'_v2independent.json'"),
                    ("'_v2main.log'","'_v2independent.log'"),
                    ("str(E/'main_entry_v2_224.py')","str(E/'independent_main_entry_v2_224.py')")]:
        assert text.count(old)==1
        text=text.replace(old,new)
    return path,text

def main():
    build_authorizer()(); assert sys.argv[1] in ('main-agentless','main-ours')
    path,text=reviewed_wrapper_text()
    scope={'__name__':'independent_main_supervisor','__file__':str(path)}
    exec(compile(text,str(path),'exec'),scope); scope['run']()

if __name__=='__main__': main()
