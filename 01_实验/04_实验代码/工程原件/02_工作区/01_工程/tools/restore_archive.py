"""Restore original research content from Git, GitHub assets and pinned upstreams."""
import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import urllib.request
import zlib
import zipfile

ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/".restore-cache"

def sha(data):return hashlib.sha256(data).hexdigest()

def safe_target(relative):
    target=(ROOT/relative).resolve()
    if not target.is_relative_to(ROOT):raise ValueError("Unsafe archive path: "+relative)
    return target

def load_catalog():
    index=json.loads((ROOT/"manifests/archive/index.json").read_text(encoding="utf-8"))
    objects={}
    for relative in index["object_maps"]:
        with gzip.open(ROOT/relative,"rt",encoding="utf-8") as f:
            for line in f:
                digest,record=json.loads(line);objects[digest]=record
    return index,objects

class Restore:
    def __init__(self,index,objects):
        self.index=index;self.objects=objects;self.tars={};self.upstreams={};self.package_archives={}
        CACHE.mkdir(exist_ok=True)

    def download(self,source):
        path=CACHE/(source["sha256"]+"-"+source["name"])
        if not path.exists():
            temporary=path.with_suffix(".download")
            url=source["url"]
            if url.startswith("https://github.com/") and "/releases/download/" in url:
                repository,asset=url.split("github.com/",1)[1].split("/releases/download/",1)
                tag,name=asset.split("/",1)
                subprocess.run(["gh","release","download",tag,"--repo",repository,"--pattern",name,"--output",str(temporary),"--clobber"],check=True)
            else:
                request=urllib.request.Request(url,headers={"User-Agent":"thesis-archive-restore/1.0"})
                with urllib.request.urlopen(request,timeout=180) as response,temporary.open("wb") as output:shutil.copyfileobj(response,output,4*2**20)
            temporary.replace(path)
        with path.open("rb") as stream:actual=hashlib.file_digest(stream,"sha256").hexdigest()
        if actual!=source["sha256"]:raise RuntimeError("Pinned download SHA256 mismatch")
        return path

    def python_package(self,record):
        catalog=json.loads((ROOT/"manifests/python_packages.json").read_text(encoding="utf-8"))
        item=catalog[record["package"]];source=item["source"]
        if "unavailable" in source:raise RuntimeError("Rebuild the recorded external package: "+item["name"]+"=="+item["version"])
        path=self.download(source)
        if record["package"] not in self.package_archives:
            self.package_archives[record["package"]]=zipfile.ZipFile(path) if source["format"]=="wheel" or path.suffix==".zip" else tarfile.open(path,"r:gz")
        archive=self.package_archives[record["package"]];member=record["member"]
        expected=record["expected_sha256"]
        if isinstance(archive,zipfile.ZipFile):
            if member in archive.namelist():data=archive.read(member)
            else:
                candidates=[p for p in archive.namelist() if p.endswith("/purelib/"+member) or p.endswith("/platlib/"+member) or p.endswith("/"+member)]
                data=next((b for p in candidates if sha(b:=archive.read(p))==expected),None)
        else:
            candidates=[m for m in archive.getmembers() if m.isfile() and (m.name==member or m.name.endswith("/"+member))]
            data=next((b for m in candidates if sha(b:=archive.extractfile(m).read())==expected),None)
        if data is None or sha(data)!=expected:raise RuntimeError("External package member differs from its original RECORD: "+member)
        return data

    def release(self,asset):
        path=CACHE/asset["name"]
        if path in self.tars:return self.tars[path]
        if not path.is_file():
            if asset.get('id'):
                temporary=path.with_suffix('.download')
                with temporary.open('wb') as output:subprocess.run(['gh','api','repos/'+self.index['repository']+'/releases/assets/'+str(asset['id']),'-H','Accept: application/octet-stream'],stdout=output,check=True)
                temporary.replace(path)
            else:subprocess.run(["gh","release","download",self.index["release_tag"],"--repo",self.index["repository"],"--pattern",asset["name"],"--dir",str(CACHE)],check=True)
        with path.open("rb") as stream:actual=hashlib.file_digest(stream,"sha256").hexdigest()
        if actual!=asset["sha256"]:raise RuntimeError("Release asset SHA256 mismatch: "+asset["name"])
        self.tars[path]=tarfile.open(path,"r:")
        return self.tars[path]

    def upstream(self,source):
        if source.get('git_blob'):
            import base64
            reference=source['git_blob'];path=CACHE/('github-blob-'+reference['oid'])
            if not path.is_file():
                response=json.loads(subprocess.check_output(['gh','api','repos/'+reference['repository']+'/git/blobs/'+reference['oid']],encoding='utf-8'))
                data=base64.b64decode(response['content']);path.write_bytes(data)
            data=path.read_bytes()
            if sha(data)!=source['blob_sha256']:raise RuntimeError('Pinned GitHub blob changed')
            return data
        url=source["url"].removesuffix(".git");revision=source["revision"]
        key=sha((url+"\n"+revision).encode())[:24]
        if url.startswith("https://github.com/"):
            path=CACHE/("upstream-"+key+".tar.gz")
            if not path.exists():
                request=urllib.request.Request("https://codeload.github.com/"+url.split("github.com/",1)[1]+"/tar.gz/"+revision,headers={"User-Agent":"thesis-archive-restore/1.0"})
                temporary=path.with_suffix(".download")
                with urllib.request.urlopen(request,timeout=180) as response,temporary.open("wb") as output:shutil.copyfileobj(response,output,4*2**20)
                temporary.replace(path)
            if key not in self.upstreams:
                archive=tarfile.open(path,"r:gz")
                prefix=archive.getnames()[0].split("/")[0]
                self.upstreams[key]=(archive,prefix)
            archive,prefix=self.upstreams[key]
            member=archive.getmember(prefix+"/"+source["path"])
            data=member.linkname.encode("utf-8") if member.issym() else archive.extractfile(member).read()
        else:
            path=CACHE/("upstream-"+key+".git")
            if not path.exists():
                subprocess.run(["git","init","--bare",str(path)],check=True,capture_output=True)
                subprocess.run(["git","-C",str(path),"fetch","--depth=1",url,revision],check=True)
            data=subprocess.check_output(["git","-C",str(path),"show",revision+":"+source["path"]])
        if source.get("blob_sha256") and sha(data)!=source["blob_sha256"]:raise RuntimeError("Pinned upstream file changed")
        return data

    def content(self,digest):
        record=self.objects[digest];kind=record["kind"]
        if kind=="git":
            path=safe_target(record["path"])
            data=path.read_bytes() if path.is_file() else None
            if data is None or sha(data)!=digest:
                commit=record.get("commit",self.index.get("git_snapshot_commit"))
                if not commit:raise RuntimeError("Archive snapshot commit is missing")
                command=["git","-C",str(ROOT),"show",commit+":"+record["path"]]
                result=subprocess.run(command,capture_output=True)
                if result.returncode:
                    subprocess.run(["git","-C",str(ROOT),"fetch","--no-tags","origin",commit],check=True,capture_output=True)
                    data=subprocess.check_output(command)
                else:data=result.stdout
        elif kind=="literal":data=record["text"].encode("utf-8")
        elif kind=="download":data=self.download(record["source"]).read_bytes()
        elif kind=="download_member":
            with zipfile.ZipFile(self.download(record["source"])) as archive:data=archive.read(record["member"])
        elif kind=="download_tar_member":
            with tarfile.open(self.download(record["source"]),"r:gz") as archive:data=archive.extractfile(record["member"]).read()
        elif kind=="provider":
            source=record["source"];home=Path(os.environ.get("CODEX_HOME",Path.home()/".codex"));base=home/"plugins/cache/openai-primary-runtime"/source["package"]
            candidates=[base/source["version"]/"skills"/source["package"]/source["relative"]]
            if base.is_dir():candidates += [p/"skills"/source["package"]/source["relative"] for p in base.iterdir() if p.is_dir()]
            data=next((p.read_bytes() for p in candidates if p.is_file() and sha(p.read_bytes())==digest),None)
            if data is None:raise RuntimeError("Install the recorded Codex artifact runtime for this optional historical helper: "+source["package"])
        elif kind=="python_package_file":
            data=self.python_package(record)
            if record.get("newline")=="CRLF":data=data.replace(b"\r\n",b"\n").replace(b"\n",b"\r\n")
        elif kind=="source_parts":
            recipe=json.loads((ROOT/record["path"]).read_text(encoding="utf-8"));chunks=[]
            for part in recipe["parts"]:
                if "literal" in part:chunks.append(part["literal"])
                else:
                    text=self.upstream(part["source"]).replace(b"\r\n",b"\n").decode("utf-8").splitlines(keepends=True)
                    chunks.append("".join(text[part["lines"][0]:part["lines"][1]]).rstrip("\n"))
            data="".join(chunks).encode("utf-8")
            if recipe.get("newline")=="CRLF":data=data.replace(b"\n",b"\r\n")
        elif kind=="asset":
            packed=b"".join(self.release(self.index["assets"][chunk["asset"]]).extractfile(chunk["member"]).read() for chunk in record["chunks"])
            data=zlib.decompress(packed) if record.get("encoding")=="zlib" else packed
        elif kind=="zip_layout":
            metadata=self.content(record["metadata"]);output=io.BytesIO();meta_position=position=0
            for begin,length,h in record["ranges"]:
                gap=begin-position;output.write(metadata[meta_position:meta_position+gap]);meta_position+=gap
                payload=self.content(h)
                if len(payload)!=length:raise RuntimeError("Tensor payload length differs")
                output.write(payload);position=begin+length
            output.write(metadata[meta_position:]);data=output.getvalue()
            if len(data)!=record["size"]:raise RuntimeError("Tensor archive size differs")
        elif kind=="deflate":
            compressor=zlib.compressobj(record["level"],zlib.DEFLATED,-15)
            raw=self.content(record["source"]);data=compressor.compress(raw)+compressor.flush()
        elif kind=="deflate_delta":
            compressor=zlib.compressobj(record['level'],zlib.DEFLATED,-15);raw=self.content(record['source']);base=compressor.compress(raw)+compressor.flush();delta=self.content(record['delta']);base=base.ljust(len(delta),b'\0');data=bytes(a^b for a,b in zip(base,delta))[:record['size']]
        elif kind=="python_bytecode":
            import base64
            version=record['version']
            result=subprocess.run(['uv','python','find',version],capture_output=True,encoding='utf-8')
            if result.returncode:
                subprocess.run(['uv','python','install',version],check=True)
                result=subprocess.run(['uv','python','find',version],capture_output=True,encoding='utf-8',check=True)
            helper="import sys,json,base64,marshal; o=json.load(sys.stdin); b=bytes.fromhex(o['header'])+marshal.dumps(compile(base64.b64decode(o['source']),o['filename'],'exec',dont_inherit=True,optimize=o['optimization'])); sys.stdout.buffer.write(b)"
            if record.get('compiled_sha256'):
                helper="import sys,json,base64,marshal; o=json.load(sys.stdin); compiled=compile(base64.b64decode(o['source']),o['filename'],'exec',dont_inherit=True,optimize=o['optimization']); b=bytes.fromhex(o['header'])+marshal.dumps(compiled); sys.stdout.buffer.write(b)"
            payload={**record,'source':base64.b64encode(self.content(record['source'])).decode()}
            data=subprocess.check_output([result.stdout.strip(),'-c',helper],input=json.dumps(payload).encode())
            if record.get('compiled_sha256'):
                if sha(data)!=record['compiled_sha256']:raise RuntimeError('Rebuilt bytecode differs before marshal-layout patches')
                patched=bytearray(data)
                for position,value in record.get('marshal_patches',[]):patched[position]=value
                data=bytes(patched)
        elif kind in {"upstream","github_blob"}:
            data=self.upstream(record["source"])
            if record.get("newline")=="CRLF":data=data.replace(b"\r\n",b"\n").replace(b"\n",b"\r\n")
            elif record.get("newline")=="LF":data=data.replace(b"\r\n",b"\n")
        elif kind=="delta":
            recipe=json.loads((ROOT/record["path"]).read_text(encoding="utf-8"))
            base_data=self.python_package(recipe["python_package"]) if "python_package" in recipe else self.upstream(recipe["source"])
            base_text=base_data.replace(b"\r\n",b"\n").decode("utf-8")
            base=list(base_text) if recipe.get('unit')=='characters' else base_text.splitlines(keepends=True)
            output=[];position=0
            for begin,end,lines in recipe["edits"]:
                output.extend(base[position:begin]);output.extend(lines);position=end
            output.extend(base[position:]);data="".join(output).encode("utf-8")
            if recipe.get("newline")=="CRLF":data=data.replace(b"\n",b"\r\n")
            if recipe.get('newline_exceptions'):
                lines=data.splitlines(keepends=True)
                for number,eol in recipe['newline_exceptions'].items():lines[int(number)]=lines[int(number)].rstrip(b'\r\n')+{'LF':b'\n','CRLF':b'\r\n','NONE':b''}[eol]
                data=b''.join(lines)
        elif kind=="omitted":return None
        else:raise RuntimeError("Unresolved object kind: "+kind)
        if sha(data)!=digest:raise RuntimeError("Restored content SHA256 mismatch: "+digest)
        return data

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--list",action="store_true")
    parser.add_argument("--scope",action="append",default=[])
    parser.add_argument('--path',action='append',default=[],help='Restore only this original file or directory prefix')
    parser.add_argument('--output',default='.',help='Destination root inside this clone; use .rebuild/history for inspection')
    parser.add_argument("--with-upstream",action="store_true",help="Also recreate downloaded source copies; often unnecessary")
    parser.add_argument("--verify-only",action="store_true",help="Check content without writing logical copies")
    args=parser.parse_args();index,objects=load_catalog()
    if args.list or not (args.scope or args.path):
        for scope,info in index["scopes"].items():print(scope,info["files"],info["destination"])
        return
    selected=args.scope or ["main"]
    restore=Restore(index,objects);checked=written=skipped=matched=0;prefixes=[p.replace('\\','/').rstrip('/') for p in args.path]
    for scope in selected:
        info=index["scopes"][scope]
        with gzip.open(ROOT/info["map"],"rt",encoding="utf-8") as stream:
            for line in stream:
                relative,digest,size,mtime,category=json.loads(line)
                if prefixes and not any(relative==p or relative.startswith(p+'/') for p in prefixes):continue
                matched+=1
                record=objects[digest]
                if record["kind"] in {"upstream","github_blob","download","download_member","download_tar_member","provider","python_package_file"} and not args.with_upstream:skipped+=1;continue
                target=safe_target((Path(args.output)/info["destination"]/relative).as_posix())
                if target.is_file():
                    with target.open("rb") as f:current=hashlib.file_digest(f,"sha256").hexdigest()
                    if current==digest:checked+=1;continue
                    if scope=="main" and relative in {"README.md","AGENTS.md",".gitignore",".gitattributes"}:skipped+=1;continue
                    raise RuntimeError("Existing different content; preserved without overwrite: "+str(target))
                data=restore.content(digest)
                if data is None:skipped+=1;continue
                checked+=1
                if not args.verify_only:
                    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);written+=1
    if prefixes and not matched:raise SystemExit('No archive paths matched the requested prefix')
    print(json.dumps({"scopes":selected,"matched":matched,"checked":checked,"written":written,"skipped_upstream_or_entry":skipped},ensure_ascii=False))

if __name__=="__main__":main()
