"""Explicit, byte-preserving launcher for the archived AOrchestra 261 guard.

Only Windows null-device aliases are adapted. Author flow, process identity,
the original harness guard and all file/network restrictions stay in the entry.
This is an offline-checkable compatibility candidate, not runtime qualification.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import sys


_ORIGINAL_NULL_CHECK = "if os.fsdecode(values[0]).casefold()==os.devnull.casefold():return"
_ADAPTED_NULL_CHECK = "if _rq2_null_device(values[0]):return"

# Keep the injected helper compatible with the archived Python 3.8 runtime.
# Do not normalize arbitrary paths into devices or exempt every device prefix.
_HELPER = r'''
def _rq2_null_device(value):
    raw = os.fsdecode(value)
    if os.name != 'nt':
        return raw == os.devnull
    raw = raw.replace('/', '\\').casefold()
    return raw in ('nul', '\\\\.\\nul', '\\\\.\\nul\\')

'''


def adapt_product_entry(source: str) -> str:
    """Adapt exactly the archived guard occurrence, refusing other layouts."""
    ast.parse(source)
    if source.count(_ORIGINAL_NULL_CHECK) != 1 or source.count("def main():") != 1:
        raise ValueError("RQ2_261_GUARD_LAYOUT_NOT_RECOGNIZED")
    if "def _rq2_null_device" in source:
        raise ValueError("RQ2_261_ENTRY_ALREADY_ADAPTED")
    adapted = source.replace(_ORIGINAL_NULL_CHECK, _ADAPTED_NULL_CHECK)
    adapted = adapted.replace("def main():", _HELPER + "def main():", 1)
    ast.parse(adapted)
    return adapted


def check_entry(entry: Path) -> dict:
    raw = entry.read_bytes()
    adapted = adapt_product_entry(raw.decode("utf-8-sig"))
    compile(adapted, str(entry), "exec")
    return {
        "entry": str(entry.resolve()),
        "original_sha256": hashlib.sha256(raw).hexdigest(),
        "in_memory_adapted_sha256": hashlib.sha256(adapted.encode("utf-8")).hexdigest(),
        "original_file_modified": False,
        "adaptation": "recognize only nul and normalized Windows null-device aliases before Path.resolve",
        "compiled": True,
        "full_runtime_qualified": False,
    }


def run_entry(entry: Path, envelope: Path) -> None:
    """Run the original entry with the narrow in-memory guard adaptation.

    Intended for a separately authorized child process: the original entry
    installs permanent audit hooks and still requires its original envelope,
    process identity and harness checks. No source file is rewritten.
    """
    entry = entry.resolve()
    adapted = adapt_product_entry(entry.read_text(encoding="utf-8-sig"))
    sys.path.insert(0, str(entry.parent))
    sys.argv = [str(entry), str(envelope.resolve())]
    namespace = {"__name__": "__main__", "__file__": str(entry), "__package__": None}
    exec(compile(adapted, str(entry), "exec"), namespace)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("check", help="read and compile the adapted entry without executing it")
    check.add_argument("entry", type=Path)
    run = commands.add_parser("run", help="execute the original guarded entry in this child process")
    run.add_argument("entry", type=Path)
    run.add_argument("envelope", type=Path)
    args = parser.parse_args(argv)
    if args.command == "check":
        print(json.dumps(check_entry(args.entry), ensure_ascii=False, indent=2))
    else:
        run_entry(args.entry, args.envelope)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
