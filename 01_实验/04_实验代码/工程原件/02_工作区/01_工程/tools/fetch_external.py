"""Download pinned upstream code. Downloaded files are ignored by Git."""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--core",action="store_true",help="Fetch the pinned StepFinder model used by the frozen source")
    parser.add_argument("--models",action="store_true",help="Also fetch the optional pinned text embedding model (about 1.2 GB)")
    parser.add_argument("--manifest",help="Additional recorded resource manifest, relative to this clone")
    args=parser.parse_args()
    manifest=json.loads((ROOT/"manifests/external_core.json").read_text(encoding="utf-8"))
    records=manifest["files"]
    if args.models:
        records+=json.loads((ROOT/"manifests/external_models.json").read_text(encoding="utf-8"))["files"]
    if args.manifest:
        records+=json.loads((ROOT/args.manifest).read_text(encoding="utf-8"))["files"]
    for item in records:
        target=(ROOT/item["destination"]).resolve()
        if not target.is_relative_to(ROOT):raise RuntimeError("External resource destination escaped this clone")
        if target.is_file() and hashlib.sha256(target.read_bytes()).hexdigest()==item["sha256"]:
            continue
        request=urllib.request.Request(item["url"],headers={"User-Agent":"thesis-portable-bootstrap/1.0"})
        target.parent.mkdir(parents=True,exist_ok=True)
        temporary=target.with_suffix(target.suffix+".download")
        if item.get("size",0)>64*2**20:
            digest=hashlib.sha256()
            with urllib.request.urlopen(request,timeout=120) as response, temporary.open("wb") as output:
                for block in iter(lambda:response.read(4*2**20),b""):
                    digest.update(block);output.write(block)
            if digest.hexdigest()!=item["sha256"]:
                raise RuntimeError("Upstream model hash differs from pinned source")
            temporary.replace(target)
            print("Fetched pinned model: "+item["destination"])
            continue
        with urllib.request.urlopen(request,timeout=90) as response:data=response.read()
        if item.get("newline")=="CRLF":
            data=data.replace(b"\r\n",b"\n").replace(b"\n",b"\r\n")
        if hashlib.sha256(data).hexdigest()!=item["sha256"]:
            raise RuntimeError("Upstream file hash differs from pinned source: "+item["url"])
        temporary.write_bytes(data)
        temporary.replace(target)
        print("Fetched pinned external file: "+item["destination"])


if __name__=="__main__":
    main()
