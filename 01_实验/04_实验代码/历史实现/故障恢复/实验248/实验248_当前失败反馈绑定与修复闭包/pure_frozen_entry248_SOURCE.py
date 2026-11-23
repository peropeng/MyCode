"""Run the original pure continuation without rewriting frozen derived sources.

The inherited preparation module regenerates two deterministic source files at
import. Skip those writes only after matching the exact original frozen bytes.
No model, native, private or finance capability is introduced by this entry.
"""
import argparse, hashlib, io, json, runpy, sys
from pathlib import Path

E=Path(__file__).resolve().parent
sys.dont_write_bytecode=True

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--index',required=True,type=int);args=parser.parse_args()
    seal=json.loads((E/'SOURCE_SEAL.json').read_text('utf-8-sig'))
    targets={Path(path).resolve():h for path,h in seal['sources_SHA256'].items()
             if Path(path).resolve() in {(E/'ranked_repair248.py').resolve(),(E/'body248.py').resolve()}}
    if len(targets)!=2:raise RuntimeError('EXP248_FROZEN_GENERATED_SOURCES_NOT_BOUND')
    original=Path.write_text
    def checked_write(path,data,encoding=None,errors=None,newline=None):
        destination=path.resolve()
        if destination not in targets:return original(path,data,encoding=encoding,errors=errors,newline=newline)
        memory=io.BytesIO()
        stream=io.TextIOWrapper(memory,encoding=encoding,errors=errors,newline=newline)
        count=stream.write(data);stream.flush();proposed=memory.getvalue()
        expected=targets[destination]
        if hashlib.sha256(proposed).hexdigest()!=expected or hashlib.sha256(destination.read_bytes()).hexdigest()!=expected:
            raise RuntimeError('EXP248_REGENERATED_SOURCE_DIFFERS_FROM_FROZEN_R2_NO_WRITE')
        return count
    Path.write_text=checked_write
    try:
        sys.path.insert(0,str(E));sys.argv=[str(E/'continue248.py'),'--index',str(args.index)]
        runpy.run_path(str(E/'continue248.py'),run_name='__main__')
    finally:Path.write_text=original

if __name__=='__main__':main()
