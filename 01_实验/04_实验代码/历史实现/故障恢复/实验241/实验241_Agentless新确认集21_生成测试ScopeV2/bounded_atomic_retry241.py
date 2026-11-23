"""Additive preparation only; no installation or finance work on import."""
import ast, inspect, os, time

def replace_retry(source, target, replace=os.replace, sleep=time.sleep):
    for attempt in range(20):
        try:
            return replace(source, target)
        except PermissionError as error:
            if getattr(error, 'winerror', None) != 5 or attempt == 19:
                raise
            sleep(.05)

def patched_atomic(module):
    source = inspect.getsource(module.atomic)
    anchor = 'os.replace(tmp,path)'
    if source.count(anchor) != 1:
        raise RuntimeError('EXACT_ORIGINAL_ATOMIC_ANCHOR_REQUIRED')
    scope = dict(module.__dict__)
    scope['replace_retry'] = replace_retry
    exec(compile(ast.parse(source.replace(anchor, 'replace_retry(tmp,path)')),
                 str(module.__file__), 'exec'), scope)
    return scope['atomic']

def install_scoped_factory(transport):
    """Call only on an already PP-scoped isolated transport instance."""
    original = transport.LegacyIO
    class BoundedScopedIO(original):
        def __init__(self):
            super().__init__()
            self.m.atomic = patched_atomic(self.m)
    transport.LegacyIO = BoundedScopedIO
