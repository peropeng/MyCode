"""Reuse root-reviewed Job wrapper shape; RUNNING publication precedes Resume."""
from common166 import *
from main_environment_v2_224 import authorize_main


def reviewed_wrapper_text():
    path = E / 'supervise_fresh224.py'; text = path.read_text('utf-8-sig')
    replacements = [("supervision=E/('supervision_'+mode+'_224.json')", "supervision=E/('v2_auth_direct_publicpack/supervision_'+mode+'_v2main.json')"),
                    ("log=E/('logs/prepared_entry_'+mode+'224.log')", "log=E/('v2_auth_direct_publicpack/logs/'+mode+'_v2main.log')"),
                    ("str(E/'fresh_entry224.py')", "str(E/'main_entry_v2_224.py')"),
                    ("'Exp224':'owned_runner_stopped'", "'Exp224V2Main':'owned_runner_stopped'")]
    for old, new in replacements:
        assert text.count(old) == 1, 'MAIN_REVIEWED_SUPERVISOR_ANCHOR_DRIFT'
        text = text.replace(old, new)
    # Identical move used by root-reviewed supervise_second_v2_224.py.
    resume_start = text.index('  nt=ctypes.WinDLL(')
    record_start = text.index('  save(supervision,', resume_start)
    record_end = text.index('\n', record_start) + 1
    text = text[:resume_start] + text[record_start:record_end] + text[resume_start:record_start] + text[record_end:]
    return path, text


def main():
    authorize_main(); assert sys.argv[1] in ('main-agentless', 'main-ours')
    path, text = reviewed_wrapper_text()
    scope = {'__name__': 'reviewed_main_supervisor', '__file__': str(path)}
    exec(compile(text, str(path), 'exec'), scope)
    scope['run']()


if __name__ == '__main__': main()
