"""Prepared only: check the existing environment clock around dense batches.

No live installation. A future reviewed controller must bind and authorize this
wrapper. Original dense source, text, vectors, device and batch size stay intact.
"""
from contextlib import contextmanager
import functools
import inspect
import textwrap


class CheckedEncoder:
    def __init__(self, original, require):
        self.original = original
        self.require = require

    def __getattr__(self, name):
        return getattr(self.original, name)

    def encode(self, *args, **kwargs):
        self.require()
        result = self.original.encode(*args, **kwargs)
        self.require()
        return result


def bounded_prepare(original_prepare, original_encoder, require):
    # Clone only the function globals so the source implementation executes
    # unchanged with a checked encoder factory. No shared module is modified.
    namespace = dict(original_prepare.__globals__)
    namespace['encoder'] = lambda *args, **kwargs: CheckedEncoder(original_encoder(*args, **kwargs), require)
    exec(compile(textwrap.dedent(inspect.getsource(original_prepare)), inspect.getsourcefile(original_prepare), 'exec'), namespace)
    exact_prepare = namespace[original_prepare.__name__]

    @functools.wraps(original_prepare)
    def checked(*args, **kwargs):
        require()
        result = exact_prepare(*args, **kwargs)
        require()
        return result
    return checked


@contextmanager
def prepared_scope(dense_module, env):
    original = dense_module.prepare
    dense_module.prepare = bounded_prepare(original, dense_module.encoder, env._require)
    try:
        yield
    finally:
        dense_module.prepare = original
