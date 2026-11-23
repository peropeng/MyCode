"""ADD-only fixed second-case launcher; pin verified before the owned Job starts."""
from common166 import *
from second_entry_v2_224 import verify_addendum


def main():
    verify_addendum(sys.argv[1])
    path = E / 'supervise_fresh224.py'; text = path.read_text('utf-8-sig')
    replacements = [("supervision=E/('supervision_'+mode+'_224.json')", "supervision=E/('v2_auth_direct_publicpack/supervision_second_'+mode+'_v2.json')"),
                    ("log=E/('logs/prepared_entry_'+mode+'224.log')", "log=E/('v2_auth_direct_publicpack/logs/second_'+mode+'_v2.log')"),
                    ("str(E/'fresh_entry224.py')", "str(E/'second_entry_v2_224.py')"),
                    ("'Exp224':'owned_runner_stopped'", "'Exp224V2Second':'owned_runner_stopped'")]
    for old, new in replacements:
        assert text.count(old) == 1, 'SECOND_REVIEWED_SUPERVISOR_ANCHOR_DRIFT'
        text = text.replace(old, new)
    # Publish immutable child birth/job assignment before allowing child code.
    resume_start = text.index('  nt=ctypes.WinDLL(')
    record_start = text.index('  save(supervision,', resume_start)
    record_end = text.index('\n', record_start) + 1
    text = text[:resume_start] + text[record_start:record_end] + text[resume_start:record_start] + text[record_end:]
    scope = {'__name__': 'reviewed_second_supervisor', '__file__': str(path)}
    exec(compile(text, str(path), 'exec'), scope)
    scope['run']()


if __name__ == '__main__': main()
