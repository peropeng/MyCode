"""Inspect or explicitly run a frozen legacy entry from a relocated checkout."""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from thesis_recovery import legacy_paths


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("entry",help="Path relative to the restored repository")
    parser.add_argument("--root",default=".",help="Restored historical root, relative to this clone")
    parser.add_argument("--execute",action="store_true",help="Run the entry's main block; historical grants remain closed")
    parser.add_argument("--allow-network",action="store_true",help="Explicitly allow network for an authorized new run")
    args,tail=parser.parse_known_args()
    base=(ROOT/args.root).resolve()
    if not base.is_relative_to(ROOT):raise ValueError("Historical root must remain inside this clone")
    target=(base/args.entry).resolve()
    if not target.is_relative_to(base) or not target.is_file():
        raise FileNotFoundError("Restore this source before use: "+args.entry)
    legacy_paths.install(base,allow_network=args.allow_network)
    sys.path.insert(0,str(target.parent))
    sys.argv=[str(target),*tail]
    namespace={"__file__":str(target),"__name__":"__main__" if args.execute else "__portable_inspect__","__package__":None}
    exec(legacy_paths.relocated_compile(target.read_bytes(),str(target),"exec"),namespace)
    if not args.execute:
        print(json.dumps({"entry":args.entry,"loaded_without_original_machine":True,"main_executed":False,"network_enabled":args.allow_network},ensure_ascii=False))


if __name__=="__main__":
    main()
