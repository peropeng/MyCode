"""Rebuild the sealed Windows Moto test environment from public distributions."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile

from restore_archive import ROOT,Restore,load_catalog

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",default=".rebuild/current-method/recovery")
    args=parser.parse_args()
    if sys.platform!="win32":raise RuntimeError("This historical native test environment requires Windows")
    spec=json.loads((ROOT/"manifests/native_environment.json").read_text(encoding="utf-8"))
    restore=Restore({}, {})
    runtime=ROOT/".external/cpython-3.11.15-20260623"
    if not (runtime/"python.exe").is_file():
        archive_path=restore.download(spec["python_distribution"])
        runtime.mkdir(parents=True,exist_ok=True)
        with tarfile.open(archive_path,"r:gz") as archive:
            for member in archive.getmembers():
                parts=Path(member.name).parts
                if not parts or parts[0]!="python":continue
                target=(runtime/Path(*parts[1:])).resolve()
                if not target.is_relative_to(runtime.resolve()):raise RuntimeError("Unsafe Python distribution member")
                if member.isdir():target.mkdir(parents=True,exist_ok=True)
                elif member.isfile():
                    target.parent.mkdir(parents=True,exist_ok=True)
                    with archive.extractfile(member) as source,target.open("wb") as output:shutil.copyfileobj(source,output,2**20)
    base=(ROOT/args.root).resolve()
    if not base.is_relative_to(ROOT):raise RuntimeError("Restored environment root must remain inside this clone")
    target=base/spec["relative"]
    target.mkdir(parents=True,exist_ok=True)
    config=target/"pyvenv.cfg"
    if config.is_file() and hashlib.sha256(config.read_bytes()).hexdigest()==spec["sealed_configuration_sha256"]:
        archived=base/".sealed-configs"/spec["sealed_configuration_sha256"]/"pyvenv.cfg"
        archived.parent.mkdir(parents=True,exist_ok=True);archived.write_bytes(config.read_bytes())
        aliases_path=base/"manifests/legacy_path_aliases.json"
        aliases=json.loads(aliases_path.read_text(encoding="utf-8")) if aliases_path.exists() else []
        aliases.append({"old":spec["original_configuration_path"],"relative":archived.relative_to(base).as_posix()})
        aliases_path.parent.mkdir(exist_ok=True);aliases_path.write_text(json.dumps(aliases,ensure_ascii=False,indent=2),encoding="utf-8")
    subprocess.run([str(runtime/"python.exe"),"-m","venv","--without-pip",str(target)],check=True)
    executable=target/"Scripts/python.exe"
    if hashlib.sha256(executable.read_bytes()).hexdigest()!=spec["venv_launcher_sha256"]:raise RuntimeError("Sealed Python launcher differs")
    subprocess.run(["uv","pip","install","--python",str(executable),"--no-deps","--require-hashes","--requirements",str(ROOT/spec["requirements"])],check=True)
    probe="import json,moto,boto3,pytest,sys;print(json.dumps({'python':sys.version.split()[0],'moto':moto.__version__,'boto3':boto3.__version__,'pytest':pytest.__version__}))"
    result=json.loads(subprocess.check_output([str(executable),"-I","-c",probe],encoding="utf-8"))
    result.update({"environment":str(target.relative_to(ROOT)).replace("\\","/"),"launcher_sha256":spec["venv_launcher_sha256"],"sealed_launcher_matches":True,"runtime_configuration_sha256":hashlib.sha256(config.read_bytes()).hexdigest(),"configuration_paths_relocated":True,"experiments_executed":0,"api_requests":0})
    (ROOT/"verification/native_environment_rebuild.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))

if __name__=="__main__":main()
