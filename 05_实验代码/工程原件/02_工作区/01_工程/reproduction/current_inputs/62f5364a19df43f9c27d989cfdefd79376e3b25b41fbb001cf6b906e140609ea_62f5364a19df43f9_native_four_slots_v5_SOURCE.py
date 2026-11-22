"""Shared four native slots; finance byte zero and MONAI exclusion unchanged.

Every slot is an OS byte lock on the original shared file. Existing owners of
byte one or two remain mutually exclusive with this adapter. A callback checks
the current grant, STOP and finite clock while waiting; immutable source checks
are performed before waiting and again after acquisition by the caller.
"""
import time
from contextlib import contextmanager


@contextmanager
def native_lane(lock_path, package, check_wait, record, *, lock_api=None):
    if lock_api is None:
        import msvcrt as lock_api
    held = []
    started = time.monotonic()
    with open(lock_path, 'r+b') as stream:
        def acquire(offset):
            stream.seek(offset)
            try:
                lock_api.locking(stream.fileno(), lock_api.LK_NBLCK, 1)
            except OSError:
                return False
            held.append(offset)
            return True

        try:
            # Preserve the historical MONAI ordering and global single slot.
            if package == 'monai':
                while True:
                    check_wait()
                    if acquire(3):
                        break
                    time.sleep(.1)
            slot = None
            while slot is None:
                check_wait()
                for offset in (1, 2, 4, 5):
                    if acquire(offset):
                        slot = offset
                        break
                if slot is None:
                    time.sleep(.1)
            record({'event': 'SHARED_FOUR_NATIVE_SLOT_ACQUIRED', 'slot': slot,
                    'queue_seconds': time.monotonic() - started,
                    'financial_byte_zero_untouched': True,
                    'lock_held_until_owned_native_and_descendants_STOP': True})
            yield
        finally:
            for offset in reversed(held):
                stream.seek(offset)
                lock_api.locking(stream.fileno(), lock_api.LK_UNLCK, 1)
            if held:
                record({'event': 'SHARED_FOUR_NATIVE_SLOT_RELEASED',
                        'offsets': list(held)})
