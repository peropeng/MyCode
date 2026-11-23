"""Restore sealed ranking/recovery inputs in isolated legacy directories."""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from restore_archive import ROOT,Restore,load_catalog

OLD="D:/Code/毕设/graduate-thesis-experiments/"

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--component",choices=["ranking","recovery","both"],default="both")
    parser.add_argument("--with-models",action="store_true",help="Fetch the optional 1.2 GB embedding model for complete raw-text encoding")
    args=parser.parse_args();index,objects=load_catalog();restore=Restore(index,objects)
    profiles=json.loads((ROOT/"manifests/current_legacy_profiles.json").read_text(encoding="utf-8"))
    aliases=json.loads((ROOT/"manifests/legacy_path_aliases.json").read_text(encoding="utf-8"))
    reports=[]
    model_files={x["sha256"]:x for x in json.loads((ROOT/"manifests/external_models.json").read_text(encoding="utf-8"))["files"]}
    for component,profile in profiles.items():
        if args.component!="both" and component!=args.component:continue
        base=ROOT/".rebuild/current-method"/component;base.mkdir(parents=True,exist_ok=True)
        local_aliases=[]
        for entry in aliases:
            item=dict(entry)
            if item["relative"].startswith(".external/"):item["relative"]=os.path.relpath(ROOT/item["relative"],base).replace("\\","/")
            local_aliases.append(item)
        (base/"manifests").mkdir(exist_ok=True)
        (base/"manifests/legacy_path_aliases.json").write_text(json.dumps(local_aliases,ensure_ascii=False,indent=2),encoding="utf-8")
        checked=0;missing=[];deferred=[];configurations=[]
        for item in profile["files"]:
            old=item["original_path"].replace("\\","/");h=item["sha256"]
            if not old.startswith(OLD):missing.append(item);continue
            relative=old[len(OLD):]
            for alias in sorted(local_aliases,key=lambda x:len(x["old"]),reverse=True):
                prefix=alias["old"].replace("\\","/")
                if old==prefix or old.startswith(prefix+"/"):
                    relative=alias["relative"]+old[len(prefix):];break
            target=(base/relative).resolve()
            if not target.is_relative_to(base) and not target.is_relative_to(ROOT/".external"):raise RuntimeError("Unsafe sealed input path")
            if target.is_file():
                with target.open("rb") as stream:existing=hashlib.file_digest(stream,"sha256").hexdigest()
                if existing==h:checked+=1;continue
                if target.name=="pyvenv.cfg":
                    archived=base/".sealed-configs"/h/"pyvenv.cfg"
                    local_aliases.append({"old":old,"relative":archived.relative_to(base).as_posix()})
                    configurations.append({"original_path":old,"original_sha256":h,"runtime_configuration":str(target.relative_to(ROOT)).replace("\\","/"),"runtime_configuration_sha256":existing,"archived_configuration":str(archived.relative_to(ROOT)).replace("\\","/")})
                    target=archived
                else:raise RuntimeError("Existing sealed input differs: "+str(target))
            if h in model_files:
                if not args.with_models:deferred.append(item);continue
                subprocess.run([sys.executable,str(ROOT/"tools/fetch_external.py"),"--models"],check=True)
                with target.open("rb") as stream:actual=hashlib.file_digest(stream,"sha256").hexdigest()
                if actual!=h:raise RuntimeError("Restored model differs")
                checked+=1;continue
            if h not in objects:missing.append(item);continue
            data=restore.content(h)
            if data is None:missing.append(item);continue
            target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);checked+=1
        (base/"manifests/legacy_path_aliases.json").write_text(json.dumps(local_aliases,ensure_ascii=False,indent=2),encoding="utf-8")
        result={"component":component,"root":str(base.relative_to(ROOT)).replace("\\","/"),"hash_bound_files_checked":checked,"missing":missing,"optional_embedding_model_deferred":deferred,"relocated_runtime_configurations":configurations,"experiments_executed":0}
        reports.append(result);print(json.dumps(result,ensure_ascii=False),flush=True)
    report_path=ROOT/"verification/current_dependency_restore.json"
    prior=json.loads(report_path.read_text(encoding="utf-8")) if report_path.exists() else []
    combined={item['component']:item for item in prior}
    combined.update({item['component']:item for item in reports})
    report_path.write_text(json.dumps(list(combined.values()),ensure_ascii=False,indent=2),encoding="utf-8")
    if any(r["missing"] for r in reports):raise RuntimeError("Some sealed inputs need a recorded external resource or historical review")

if __name__=="__main__":main()
