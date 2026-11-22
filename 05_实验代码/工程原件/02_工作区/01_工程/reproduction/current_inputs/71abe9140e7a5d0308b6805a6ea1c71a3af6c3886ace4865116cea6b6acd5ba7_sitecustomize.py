"""Guard for Exp129 native tests; subprocesses and non-loopback network denied."""
import ipaddress
import json
import os
from pathlib import Path
import sys

if 'EXP129_FROZEN_ROOT' in os.environ:
    FROZEN = Path(os.environ['EXP129_FROZEN_ROOT']).resolve()
    SOURCE = Path(os.environ['EXP129_SOURCE_ROOT']).resolve()
    EVENTS = Path(os.environ['EXP129_GUARD_EVENTS']).resolve()
    READY = Path(os.environ['EXP129_GUARD_READY']).resolve()
    # Test packages can live inside product packages. Product imports always
    # come from candidate code; pytest uses importlib mode for frozen test files.
    sys.path.insert(0, str(SOURCE))

    def frozen(path):
        if not isinstance(path, (str, bytes, os.PathLike)):
            return False
        if os.fsdecode(path).casefold() == os.devnull.casefold():
            return False  # Windows NUL is a device, never a frozen test file.
        try:
            Path(os.fsdecode(path)).resolve().relative_to(FROZEN)
            return True
        except ValueError:
            return False

    def deny(event, detail):
        with EVENTS.open('a', encoding='utf-8') as stream:
            stream.write(json.dumps({'event': event, 'detail': str(detail)}, ensure_ascii=False) + '\n')
        raise PermissionError(f'EXP129 native-test guard blocked {event}: {detail}')

    def local(host):
        if isinstance(host, bytes):
            host = host.decode('ascii', 'ignore')
        if host in ('localhost', None, ''):
            return True
        try:
            return ipaddress.ip_address(host).is_loopback
        except ValueError:
            return False

    def audit(event, args):
        if event == 'socket.getaddrinfo' and not local(args[0]):
            deny(event, args[0])
        if event in ('socket.connect', 'socket.bind') and isinstance(args[1], tuple) and not local(args[1][0]):
            deny(event, args[1])
        if event in ('subprocess.Popen', 'os.system', 'os.posix_spawn', 'os.spawn'):
            deny(event, 'child process outside fixed native-test contract')
        if event == 'open' and frozen(args[0]):
            mode, flags = args[1] or '', args[2] or 0
            if any(s in mode for s in ('w', 'a', 'x', '+')) or flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND):
                deny(event, args[0])
        if event in ('os.remove', 'os.rmdir', 'os.mkdir', 'os.rename') and any(frozen(v) for v in args[:2]):
            deny(event, args[:2])

    sys.addaudithook(audit)
    READY.write_text(json.dumps({'guard_loaded': True, 'frozen_root': str(FROZEN), 'source_root': str(SOURCE),
                                'network': 'loopback only', 'subprocess': 'denied', 'api_credentials_present': False}), 'utf-8')
