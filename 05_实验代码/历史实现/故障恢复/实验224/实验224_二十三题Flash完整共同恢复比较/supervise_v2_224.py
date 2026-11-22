"""Independent V2 Windows Job using the reviewed birth/kill-on-close wrapper."""
from common166 import *
from publicpack_v2_224 import V


def main():
    # Execute the unchanged wrapper shape in a fresh module; only entry,
    # supervision/log namespace substitutions are made, all birth guards remain.
    path = E / 'supervise_fresh224.py'
    text = path.read_text('utf-8-sig')
    replacements = [("supervision=E/('supervision_'+mode+'_224.json')", "supervision=E/('v2_auth_direct_publicpack/supervision_'+mode+'_v2.json')"),
                    ("log=E/('logs/prepared_entry_'+mode+'224.log')", "log=E/('v2_auth_direct_publicpack/logs/'+mode+'_v2.log')"),
                    ("str(E/'fresh_entry224.py')", "str(E/'entry_v2_224.py')"),
                    ("'Exp224':'owned_runner_stopped'", "'Exp224V2':'owned_runner_stopped'")]
    for old, new in replacements:
        assert text.count(old) == 1, 'V2_REVIEWED_SUPERVISOR_ANCHOR_DRIFT'
        text = text.replace(old, new)
    scope = {'__name__': 'v2_reviewed_supervisor', '__file__': str(path)}
    exec(compile(text, str(path), 'exec'), scope)
    scope['run']()


if __name__ == '__main__': main()
