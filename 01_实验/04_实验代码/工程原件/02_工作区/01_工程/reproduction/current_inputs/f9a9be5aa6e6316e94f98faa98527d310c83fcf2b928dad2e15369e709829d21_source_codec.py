"""Lossless left-inverse of the official SWE-Gym OpenHands SFT serializer.

Authority: SWE-Gym/OpenHands commit e644a2ca45c3623b27a7e6c169e3d479f0a87fbc,
openhands/llm/fn_call_converter.py, convert_tool_call_to_string. The forward
serializer inserts ONE LF before and after a string iff that original string
contains LF. This inverse is decided by representation only, never by matching
a file. It does not use the lossy OpenHands non-native `.strip()` input parser.
"""
from __future__ import annotations

import copy

CODEC_ID = 'SWE-Gym-OpenHands-forward-serializer-left-inverse/1.0'
UPSTREAM_COMMIT = 'e644a2ca45c3623b27a7e6c169e3d479f0a87fbc'
UPSTREAM_SHA256 = '6b3ec45ea4422e5c8067c107463c4ba331d1c86f0f68d363b819160a748d49db'


class UnsupportedSerialization(ValueError):
    pass


def encode_string(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError('String value required')
    return '\n' + value + '\n' if '\n' in value else value


def decode_string(serialized: str) -> str:
    if not isinstance(serialized, str):
        raise TypeError('Serialized parameter must be a string')
    if '\n' not in serialized:
        value = serialized
    else:
        if not (serialized.startswith('\n') and serialized.endswith('\n')):
            raise UnsupportedSerialization('Multiline parameter lacks exactly identifiable outer LF wrapper')
        value = serialized[1:-1]
        if '\n' not in value:
            raise UnsupportedSerialization('Removing one LF wrapper gives a single-line value not in forward serializer image')
    if encode_string(value) != serialized:
        raise UnsupportedSerialization('Forward re-encoding does not equal serialized parameter bytes')
    return value


def decode_call(call: dict) -> dict:
    decoded = copy.deepcopy(call)
    raw = copy.deepcopy(call['parameters'])
    values = {key: decode_string(value) for key, value in raw.items()}
    decoded.update(parameters=values, serialized_parameters=raw, parameter_codec=CODEC_ID,
                   parameter_roundtrip_verified=True)
    if 'command' in values:
        decoded['command'] = values['command'].strip()
    return decoded
